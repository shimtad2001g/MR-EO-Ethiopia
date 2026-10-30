import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

print("Generating High-Resolution Pixel-Based AI Map for Awash...")

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\awash_image.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    
    # Stretch for contrast
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

# Prepare data for K-Means (flatten the image into a list of pixels)
pixels = img_rgb.reshape((-1, 3))

# Run K-Means (3 clusters)
print("Clustering millions of pixels (this will take 10-20 seconds)...")
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(pixels)
labels = kmeans.labels_

# Reshape back to image dimensions
classified_img = labels.reshape((img_rgb.shape[0], img_rgb.shape[1]))

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

# Left: Raw Image
ax1.imshow(img_rgb)
ax1.set_title("Raw Sentinel-2 (Awash Basin)", fontsize=18, fontweight='bold')
ax1.axis('off')

# Right: Pixel-Based Classified Map
# Colors: 0=Green(Agri), 1=Yellow(Arid), 2=Blue(Water)
cmap = ListedColormap(['#2ca02c', '#e6c229', '#1f77b4'])
ax2.imshow(classified_img, cmap=cmap, vmin=0, vmax=2)
ax2.set_title("AI-Classified Land Cover (Pixel-Based)", fontsize=18, fontweight='bold')
ax2.axis('off')

# Legend
legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Vegetation / Agriculture'),
    Patch(facecolor='#e6c229', edgecolor='black', label='Arid / Bare Soil'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water Bodies (Koka Reservoir)')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=14, 
           framealpha=0.9, edgecolor='black', title="AI Predictions", title_fontsize=15)

fig.suptitle("High-Resolution Visual Comparison of AI Classification (Awash Basin)", fontsize=22, fontweight='bold')
fig.subplots_adjust(top=0.88)

out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_5_Awash_Pixel_Map.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Pixel Map saved to: {out_img}")