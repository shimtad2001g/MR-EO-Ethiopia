import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

print("Generating Hawassa Map (Fast Method)...")

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\hawassa_image.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

# Fast K-Means Clustering
pixels = img_rgb.reshape((-1, 3))
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(pixels)
labels = kmeans.labels_
classified_img = labels.reshape((img.shape[0], img.shape[1]))

# Map colors: Darkest=Water, Med=Veg, Bright=Urban
cluster_means = [pixels[labels == i].mean() for i in range(3)]
sorted_idx = np.argsort(cluster_means)
water, veg, urban = sorted_idx[0], sorted_idx[1], sorted_idx[2]

corrected = np.zeros_like(classified_img)
corrected[classified_img == veg] = 0   # Green
corrected[classified_img == urban] = 1 # Yellow
corrected[classified_img == water] = 2 # Blue

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

ax1.imshow(img_rgb)
ax1.set_title("Raw Sentinel-2 (Hawassa)", fontsize=18, fontweight='bold')
ax1.axis('off')

cmap = ListedColormap(['#2ca02c', '#e6c229', '#1f77b4'])
ax2.imshow(corrected, cmap=cmap, vmin=0, vmax=2)
ax2.set_title("AI-Classified Land Cover (Hawassa Replication)", fontsize=18, fontweight='bold')
ax2.axis('off')

legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Vegetation / Agriculture'),
    Patch(facecolor='#e6c229', edgecolor='black', label='Urban / Bare Soil'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water Bodies (Lake Hawassa)')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=14, framealpha=0.9, edgecolor='black', title="AI Predictions", title_fontsize=15)

fig.suptitle("Visual Comparison of AI Classification (Hawassa)", fontsize=22, fontweight='bold')
fig.subplots_adjust(top=0.88)

out = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_22_Hawassa_Map.png"
plt.savefig(out, dpi=300, bbox_inches='tight')
print(f"SUCCESS! Saved to: {out}")