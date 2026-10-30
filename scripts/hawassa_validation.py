import torch
import torchvision
import rasterio
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import cohen_kappa_score, accuracy_score
from torchvision import transforms
import ee
import requests
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds
import matplotlib.pyplot as plt

print("Validating Hawassa SSL Features with XGBoost...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the Hawassa specific model
model = torchvision.models.resnet18(weights=None)
model.fc = torch.nn.Identity()
model.load_state_dict(torch.load(r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\hawassa_ssl_weights.pth", map_location=device))
model = model.to(device)
model.eval()

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\hawassa_image.tif"
with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    img_crs = src.crs
    img_shape = img.shape

preprocess = transforms.Compose([transforms.ToPILImage(), transforms.Resize((224, 224)), transforms.ToTensor()])

# Extract features
features_list, coords = [], []
for y in range(0, img.shape[0] - 224, 112):
    for x in range(0, img.shape[1] - 224, 112):
        patch = img[y:y+224, x:x+224, :]
        patch_t = preprocess(patch.astype(np.float32) / 10000.0).unsqueeze(0).to(device)
        with torch.no_grad():
            feat = model(patch_t).cpu().numpy()
        features_list.append(feat.flatten())
        coords.append((y+112, x+112))

X = np.array(features_list)

# Fetch ESA WorldCover for Hawassa
ee.Initialize()
wgs84_bounds = transform_bounds(img_crs, 'EPSG:4326', bounds.left, bounds.bottom, bounds.right, bounds.top)
roi = ee.Geometry.Rectangle(wgs84_bounds)
wc_image = ee.ImageCollection('ESA/WorldCover/v200').first().select('Map')
url = wc_image.getDownloadURL({'crs': img_crs.to_string(), 'dimensions': f"{img_shape[1]}x{img_shape[0]}", 'region': roi, 'format': 'GEO_TIFF'})
response = requests.get(url, stream=True)
with MemoryFile(response.content) as memfile:
    with memfile.open() as wc_src:
        wc_data = wc_src.read(1)

true_map = np.zeros_like(wc_data)
true_map[np.isin(wc_data, [10, 30, 40])] = 0 # Veg
true_map[np.isin(wc_data, [50, 60])] = 1     # Urban/Bare
true_map[wc_data == 80] = 2                  # Water

y = np.array([true_map[cy, cx] for cy, cx in coords])

# Stratified Random Sampling (Balanced)
valid_idx = y != -1
X, y = X[valid_idx], y[valid_idx]

# Train XGBoost
import xgboost as xgb
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
clf = xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss')
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

oa = accuracy_score(y_test, y_pred)
kappa = cohen_kappa_score(y_test, y_pred)
print(f"Hawassa Replication Accuracy: OA = {oa*100:.2f}%, Kappa = {kappa:.4f}")

# Plot Bar Chart (Figure 22)
fig, ax = plt.subplots(figsize=(10, 7))
scores = [oa * 100, kappa * 100]
bars = ax.bar(['Overall Accuracy (OA)', 'Kappa Coefficient (x100)'], scores, color=['#1f77b4', '#2ca02c'], width=0.5, edgecolor='black', linewidth=1.5)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.2f}%', ha='center', va='bottom', fontsize=16, fontweight='bold')

ax.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Target Accuracy (80%)')
ax.set_ylim(0, 110)
ax.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold')
ax.set_title('AI Model Performance Metrics (Hawassa Replication)', fontsize=18, fontweight='bold', pad=20)
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)
ax.legend(fontsize=12, loc='upper right', framealpha=0.9, edgecolor='black')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_22_Hawassa_BarChart.png", dpi=300, bbox_inches='tight')
print("✅ Figure 22 saved.")