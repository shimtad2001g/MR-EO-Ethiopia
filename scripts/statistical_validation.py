import torch
import torchvision
import rasterio
import numpy as np
import xgboost as xgb
from sklearn.metrics import confusion_matrix, cohen_kappa_score, accuracy_score
from sklearn.model_selection import train_test_split
from torchvision import transforms
import ee
import requests
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds

print("1. Loading Local SSL Model and Image...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ee.Initialize()

# Load SSL Backbone
model = torchvision.models.resnet18(weights=None)
model.fc = torch.nn.Identity()
weights_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\massive_ssl_weights.pth"
model.load_state_dict(torch.load(weights_path, map_location=device))
model = model.to(device)
model.eval()

# Load the harmonized image
img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"
with rasterio.open(img_path) as src:
    img = src.read()
    img = np.moveaxis(img, 0, -1)
    img_crs = src.crs
    img_bounds = src.bounds
    img_shape = src.shape

preprocess = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

print("2. Fetching REAL ESA WorldCover data from GEE...")
wgs84_bounds = transform_bounds(img_crs, 'EPSG:4326', img_bounds.left, img_bounds.bottom, img_bounds.right, img_bounds.top)
roi = ee.Geometry.Rectangle(wgs84_bounds)
wc_image = ee.ImageCollection('ESA/WorldCover/v200').first().select('Map')
url = wc_image.getDownloadURL({
    'crs': img_crs.to_string(),
    'dimensions': f"{img_shape[1]}x{img_shape[0]}",
    'region': roi,
    'format': 'GEO_TIFF'
})
response = requests.get(url, stream=True)
with MemoryFile(response.content) as memfile:
    with memfile.open() as wc_src:
        wc_data = wc_src.read(1)

print("3. Finding Balanced Patches (Stratified Sampling)...")
# Find coordinates for Urban (50) and Vegetation (10/30/40)
urban_coords = np.argwhere(wc_data == 50)
veg_coords = np.argwhere(np.isin(wc_data, [10, 30, 40]))

# Shuffle and pick up to 50 of each to ensure balance
np.random.seed(42)
np.random.shuffle(urban_coords)
np.random.shuffle(veg_coords)

selected_coords = []
# Grab 50 Urban patches
for cy, cx in urban_coords:
    if 112 <= cy < img_shape[0]-112 and 112 <= cx < img_shape[1]-112:
        selected_coords.append((cy, cx, 1)) # 1 = Urban
        if len([c for c in selected_coords if c[2] == 1]) >= 50: break

# Grab 50 Vegetation patches
for cy, cx in veg_coords:
    if 112 <= cy < img_shape[0]-112 and 112 <= cx < img_shape[1]-112:
        selected_coords.append((cy, cx, 0)) # 0 = Vegetation
        if len([c for c in selected_coords if c[2] == 0]) >= 50: break

print(f"   Selected {len(selected_coords)} balanced patches for training.")

print("4. Extracting SSL Features...")
features_list = []
y = []
patch_size = 224

for cy, cx, true_class in selected_coords:
    y_start, x_start = cy - 112, cx - 112
    patch = img[y_start:y_start+patch_size, x_start:x_start+patch_size, :]
    
    patch_tensor = preprocess(patch.astype(np.float32) / 10000.0).unsqueeze(0).to(device)
    with torch.no_grad():
        feature = model(patch_tensor).cpu().numpy()
    features_list.append(feature.flatten())
    y.append(true_class)

X = np.array(features_list)
y = np.array(y)

# Split into 70% Train and 30% Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print("5. Training Random Forest on Balanced Data...")
rf = xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss')
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

# Calculate Metrics
cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
oa = accuracy_score(y_test, y_pred)
kappa = cohen_kappa_score(y_test, y_pred)

print("\n==============================================")
print("    FINAL SCIENTIFIC VALIDATION (BALANCED)")
print("==============================================")
print("Confusion Matrix (0=Veg, 1=Urban):")
print(cm)
print(f"\nOverall Accuracy (OA): {oa * 100:.2f}%")
print(f"Kappa Coefficient: {kappa:.4f}")
print("==============================================")