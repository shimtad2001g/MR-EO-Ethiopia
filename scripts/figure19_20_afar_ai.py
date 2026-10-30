import ee
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import cohen_kappa_score, accuracy_score
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds
import requests

print("Generating Figure 19 (Map) & Figure 20 (Metrics) for Afar...")

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\afar_image.tif"
with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    img_crs = src.crs
    img_shape = img.shape

print("Fetching WorldCover...")
ee.Initialize()
wgs84_bounds = transform_bounds(img_crs, 'EPSG:4326', bounds.left, bounds.bottom, bounds.right, bounds.top)
roi = ee.Geometry.Rectangle(wgs84_bounds)
wc_image = ee.ImageCollection('ESA/WorldCover/v200').first().select('Map')
url = wc_image.getDownloadURL({'crs': img_crs.to_string(), 'dimensions': f"{img_shape[1]}x{img_shape[0]}", 'region': roi, 'format': 'GEO_TIFF'})
response = requests.get(url, stream=True)
with MemoryFile(response.content) as memfile:
    with memfile.open() as wc_src:
        wc_data = wc_src.read(1)

# Classes: 0=Sparse Vegetation, 1=Bare Soil/Sand, 2=Water
true_map = np.zeros_like(wc_data)
true_map[np.isin(wc_data, [10, 30, 40])] = 0 # Vegetation
true_map[np.isin(wc_data, [50, 60])] = 1     # Arid / Bare Soil
true_map[wc_data == 80] = 2                  # Water

X = img.reshape(-1, 3)
y = true_map.flatten()

valid_idx = y != -1
X, y = X[valid_idx], y[valid_idx]

np.random.seed(42)
sample_idx = np.random.choice(len(y), min(50000, len(y)), replace=False)
X_train, X_test, y_train, y_test = train_test_split(X[sample_idx], y[sample_idx], test_size=0.3, random_state=42)

rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

oa = accuracy_score(y_test, y_pred)
kappa = cohen_kappa_score(y_test, y_pred)
print(f"Afar Accuracy: OA = {oa*100:.2f}%, Kappa = {kappa:.4f}")

# --- FIGURE 19: CLASSIFIED MAP ---
full_pred = rf.predict(X).reshape(img_shape[0], img_shape[1])
cmap = ListedColormap(['#2ca02c', '#e6c229', '#1f77b4']) # Veg, Arid, Water

fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
p2, p98 = np.percentile(img, (2, 98))
ax1.imshow(np.clip((img - p2) / (p98 - p2), 0, 1))
ax1.set_title("Raw Sentinel-2 (Afar Arid Zone)", fontsize=18, fontweight='bold')
ax1.axis('off')

ax2.imshow(full_pred, cmap=cmap, vmin=0, vmax=2)
ax2.set_title("AI-Classified Land Cover (Random Forest)", fontsize=18, fontweight='bold')
ax2.axis('off')

legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Sparse Vegetation / Shrubs'),
    Patch(facecolor='#e6c229', edgecolor='black', label='Bare Soil / Sand'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water Bodies')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=14, framealpha=0.9, edgecolor='black', title="AI Predictions", title_fontsize=15)

# REMOVED "Figure 19:" from the title
fig1.suptitle("Visual Comparison of AI Classification (Afar)", fontsize=22, fontweight='bold')
fig1.subplots_adjust(top=0.88)
plt.savefig(r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_19_Afar_Classification_Final.png", dpi=300, bbox_inches='tight')
plt.close(fig1)
print("✅ Figure 19 saved.")

# --- FIGURE 20: BAR CHART ---
fig2, ax3 = plt.subplots(figsize=(10, 7))
scores = [oa * 100, kappa * 100]
bars = ax3.bar(['Overall Accuracy (OA)', 'Kappa Coefficient (x100)'], scores, color=['#1f77b4', '#2ca02c'], width=0.5, edgecolor='black', linewidth=1.5)

for bar in bars:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.2f}%', ha='center', va='bottom', fontsize=16, fontweight='bold')

ax3.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Target Accuracy (80%)')
ax3.set_ylim(0, 115) # Increased ylim to prevent text overlap
ax3.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold')
ax3.set_title('AI Model Performance Metrics (Afar Arid Zone)', fontsize=18, fontweight='bold', pad=20)
ax3.yaxis.grid(True, linestyle='--', alpha=0.7)
ax3.set_axisbelow(True)
ax3.legend(fontsize=12, loc='upper right', framealpha=0.9, edgecolor='black')
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_20_Afar_BarChart_Final.png", dpi=300, bbox_inches='tight')
plt.close(fig2)
print("✅ Figure 20 saved.")