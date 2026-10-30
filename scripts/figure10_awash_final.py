import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

print("Generating Final Pre-print Figure 10: Awash Classification...")

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\awash_image.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

# Flatten image for pixel-based clustering
pixels = img_rgb.reshape((-1, 3))

print("Clustering pixels (this takes about 10-20 seconds)...")
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(pixels)
labels = kmeans.labels_
classified_img = labels.reshape((img_rgb.shape[0], img_rgb.shape[1]))

# --- INTELLIGENT MAPPING ---
# Sort clusters by brightness to assign correct colors
# Darkest = Water, Medium = Vegetation, Brightest = Arid
cluster_means = [pixels[labels == i].mean() for i in range(3)]
sorted_indices = np.argsort(cluster_means)

water_cluster = sorted_indices[0]
veg_cluster = sorted_indices[1]
arid_cluster = sorted_indices[2]

# Re-map the labels
corrected_img = np.zeros_like(classified_img)
corrected_img[classified_img == veg_cluster] = 0   # Green
corrected_img[classified_img == arid_cluster] = 1  # Yellow
corrected_img[classified_img == water_cluster] = 2 # Blue

# Plotting
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

ax1.imshow(img_rgb)
ax1.set_title("Raw Sentinel-2 (Upper Awash Basin)", fontsize=18, fontweight='bold')
ax1.axis('off')

cmap = ListedColormap(['#2ca02c', '#e6c229', '#1f77b4'])
ax2.imshow(corrected_img, cmap=cmap, vmin=0, vmax=2)
ax2.set_title("AI-Classified Land Cover (Pixel-Based)", fontsize=18, fontweight='bold')
ax2.axis('off')

legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Vegetation / Agriculture'),
    Patch(facecolor='#e6c229', edgecolor='black', label='Arid / Bare Soil'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water Bodies (Koka Reservoir)')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=14, 
           framealpha=0.9, edgecolor='black', title="AI Predictions", title_fontsize=15)

fig.suptitle("High-Resolution Visual Comparison of AI Classification (Awash Basin)", fontsize=22, fontweight='bold')
fig.subplots_adjust(top=0.88)

out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_10_Awash_Classification_Final.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 10 successfully saved to: {out_img}")