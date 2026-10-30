import ee
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import cohen_kappa_score, accuracy_score
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds
import requests

print("Calculating Random Forest Accuracy Metrics for Upper Awash Basin...")

# 1. Load Awash Image
img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\awash_image.tif"
with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    img_crs = src.crs
    img_shape = img.shape

# 2. Fetch ESA WorldCover for Awash
print("Fetching ESA WorldCover data from GEE...")
ee.Initialize()
wgs84_bounds = transform_bounds(img_crs, 'EPSG:4326', bounds.left, bounds.bottom, bounds.right, bounds.top)
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

# 3. Prepare Training Data (Pixel-based)
print("Extracting training samples...")
# Map WorldCover classes to our 3 classes (0=Veg, 1=Arid, 2=Water)
true_map = np.zeros_like(wc_data)
true_map[np.isin(wc_data, [10, 30, 40])] = 0 # Veg
true_map[np.isin(wc_data, [50, 60])] = 1     # Arid
true_map[wc_data == 80] = 2                  # Water

# Flatten the arrays
X = img.reshape(-1, 3) # RGB bands
y = true_map.flatten()

# Filter out unclassified pixels (value -1 if any)
valid_idx = y != -1
X = X[valid_idx]
y = y[valid_idx]

# Take a random sample of 50,000 pixels for fast training
np.random.seed(42)
sample_size = min(50000, len(y))
sample_idx = np.random.choice(len(y), sample_size, replace=False)
X_sample = X[sample_idx]
y_sample = y[sample_idx]

# 4. Train Random Forest
print("Training Random Forest on Awash data...")
X_train, X_test, y_train, y_test = train_test_split(X_sample, y_sample, test_size=0.3, random_state=42)

rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)

# 5. Calculate Metrics
oa = accuracy_score(y_test, y_pred)
kappa = cohen_kappa_score(y_test, y_pred)
print(f"NEW Random Forest Awash Accuracy: OA = {oa*100:.2f}%, Kappa = {kappa:.4f}")

# 6. Plot Bar Chart
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
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_14_Awash_RF_BarChart.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ SUCCESS! Figure 14 saved to: {out_img}")