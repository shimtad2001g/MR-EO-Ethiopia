import ee
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import cohen_kappa_score, accuracy_score
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds
import requests

print("Calculating Real Accuracy Metrics for Upper Awash Basin...")

# 1. Load Awash Image
img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\awash_image.tif"
with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    img_crs = src.crs

# 2. Run K-Means Clustering (Pixel-based)
p2, p98 = np.percentile(img, (2, 98))
img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)
pixels = img_rgb.reshape((-1, 3))

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(pixels)
labels = kmeans.labels_
classified_img = labels.reshape((img.shape[0], img.shape[1]))

# 3. Intelligent Mapping (Dark=Water, Med=Veg, Bright=Arid)
cluster_means = [pixels[labels == i].mean() for i in range(3)]
sorted_indices = np.argsort(cluster_means)
water_cluster, veg_cluster, arid_cluster = sorted_indices[0], sorted_indices[1], sorted_indices[2]

pred_map = np.zeros_like(classified_img)
pred_map[classified_img == veg_cluster] = 0   # 0 = Veg
pred_map[classified_img == arid_cluster] = 1  # 1 = Arid
pred_map[classified_img == water_cluster] = 2 # 2 = Water

# 4. Fetch ESA WorldCover for Awash to validate
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

# Map WorldCover to our 3 classes (0=Veg, 1=Arid, 2=Water)
true_map = np.zeros_like(wc_data)
true_map[np.isin(wc_data, [10, 30, 40])] = 0 # Veg (Trees, Shrub, Crop)
true_map[np.isin(wc_data, [50, 60])] = 1     # Arid (Built, Bare)
true_map[wc_data == 80] = 2                  # Water

# 5. Sample 50,000 pixels to calculate metrics
np.random.seed(42)
sample_size = min(50000, true_map.size)
sample_idx = np.random.choice(true_map.size, sample_size, replace=False)
y_true = true_map.flatten()[sample_idx]
y_pred = pred_map.flatten()[sample_idx]

# 6. Calculate Metrics
oa = accuracy_score(y_true, y_pred)
kappa = cohen_kappa_score(y_true, y_pred)
print(f"Calculated Awash Accuracy: OA = {oa*100:.2f}%, Kappa = {kappa:.4f}")

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
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_14_Awash_BarChart.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ SUCCESS! Figure 14 saved to: {out_img}")