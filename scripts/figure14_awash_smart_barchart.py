import ee
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import torch
import torchvision
from torchvision import transforms
from sklearn.cluster import KMeans
from sklearn.metrics import cohen_kappa_score, accuracy_score
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds
import requests

print("Calculating Deep Learning Accuracy Metrics for Upper Awash Basin...")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 1. Load the Pre-trained SSL Model (from Addis Ababa)
print("Loading Deep Learning Model...")
model = torchvision.models.resnet18(weights=None)
model.fc = torch.nn.Identity()
weights_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\ssl_backbone_weights.pth"
model.load_state_dict(torch.load(weights_path, map_location=device))
model = model.to(device)
model.eval()

# 2. Load Awash Image
img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\awash_image.tif"
with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    img_crs = src.crs

# 3. Extract Deep Features from a Grid of Patches
print("Extracting deep features from Awash (this takes 1-2 minutes)...")
preprocess = transforms.Compose([transforms.ToPILImage(), transforms.Resize((224, 224)), transforms.ToTensor()])
patch_size = 224
stride = 112
features_list = []
coords = []

for y in range(0, img.shape[0] - patch_size, stride):
    for x in range(0, img.shape[1] - patch_size, stride):
        patch = img[y:y+patch_size, x:x+patch_size, :]
        patch_tensor = preprocess(patch.astype(np.float32) / 10000.0).unsqueeze(0).to(device)
        with torch.no_grad():
            feature = model(patch_tensor).cpu().numpy()
        features_list.append(feature.flatten())
        coords.append((y + patch_size//2, x + patch_size//2))

features = np.array(features_list)

# 4. Cluster Deep Features
print("Clustering deep features...")
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(features)
labels = kmeans.labels_

# Intelligent mapping based on cluster centers (approximate brightness)
cluster_rgb_means = []
for i in range(3):
    cluster_pixels = []
    for j, (cy, cx) in enumerate(coords):
        if labels[j] == i:
            cluster_pixels.append(img[cy, cx])
    cluster_rgb_means.append(np.mean(cluster_pixels, axis=0))

# Sort by overall brightness (sum of RGB)
brightness = [np.sum(c) for c in cluster_rgb_means]
sorted_indices = np.argsort(brightness)
water_cluster = sorted_indices[0]
veg_cluster = sorted_indices[1]
arid_cluster = sorted_indices[2]

# Create a coarse prediction map for these grid centers
pred_map = np.zeros_like(img[:,:,0])
for j, (cy, cx) in enumerate(coords):
    if labels[j] == veg_cluster: pred_map[cy, cx] = 0
    elif labels[j] == arid_cluster: pred_map[cy, cx] = 1
    elif labels[j] == water_cluster: pred_map[cy, cx] = 2

# 5. Fetch ESA WorldCover
print("Fetching ESA WorldCover data from GEE...")
ee.Initialize()
wgs84_bounds = transform_bounds(img_crs, 'EPSG:4326', bounds.left, bounds.bottom, bounds.right, bounds.top)
roi = ee.Geometry.Rectangle(wgs84_bounds)
wc_image = ee.ImageCollection('ESA/WorldCover/v200').first().select('Map')
url = wc_image.getDownloadURL({
    'crs': img_crs.to_string(),
    'dimensions': f"{img.shape[1]}x{img.shape[0]}",
    'region': roi,
    'format': 'GEO_TIFF'
})
response = requests.get(url, stream=True)
with MemoryFile(response.content) as memfile:
    with memfile.open() as wc_src:
        wc_data = wc_src.read(1)

true_map = np.zeros_like(wc_data)
true_map[np.isin(wc_data, [10, 30, 40])] = 0 
true_map[np.isin(wc_data, [50, 60])] = 1     
true_map[wc_data == 80] = 2                  

# 6. Compare at Grid Centers
y_true = []
y_pred = []
for j, (cy, cx) in enumerate(coords):
    y_true.append(true_map[cy, cx])
    y_pred.append(pred_map[cy, cx])

oa = accuracy_score(y_true, y_pred)
kappa = cohen_kappa_score(y_true, y_pred)
print(f"NEW Deep Learning Awash Accuracy: OA = {oa*100:.2f}%, Kappa = {kappa:.4f}")

# 7. Plot Bar Chart
metrics = ['Overall Accuracy (OA)', 'Kappa Coefficient (x100)']
scores = [oa * 100, kappa * 100]

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.bar(metrics, scores, color=['#1f77b4', '#2ca02c'], width=0.5, edgecolor='black', linewidth=1.5)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.2f}%', 
            ha='center', va='bottom', fontsize=16, fontweight='bold')

ax.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Target Accuracy (80%)')
ax.set_ylim(0, 100)
ax.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold')
ax.set_title('AI Model Performance Metrics (Upper Awash Basin)', fontsize=18, fontweight='bold', pad=20)
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)
ax.legend(fontsize=12, loc='upper right', framealpha=0.9, edgecolor='black')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_14_Awash_Smart_BarChart.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ SUCCESS! Figure 14 saved to: {out_img}")