import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

print("Generating Pre-print Standard Figure 13: Awash Pie Chart...")

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\awash_image.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

# Flatten image for pixel-based clustering
pixels = img_rgb.reshape((-1, 3))

print("Analyzing pixel distribution...")
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(pixels)
labels = kmeans.labels_

# Sort clusters by brightness to assign correct classes
cluster_means = [pixels[labels == i].mean() for i in range(3)]
sorted_indices = np.argsort(cluster_means)

water_cluster = sorted_indices[0]
veg_cluster = sorted_indices[1]
arid_cluster = sorted_indices[2]

# Count pixels for each class
water_count = np.sum(labels == water_cluster)
veg_count = np.sum(labels == veg_cluster)
arid_count = np.sum(labels == arid_cluster)

# Calculate percentages
total = water_count + veg_count + arid_count
sizes = [
    (veg_count / total) * 100,
    (arid_count / total) * 100,
    (water_count / total) * 100
]

labels_text = ['Vegetation / Agriculture', 'Arid / Bare Soil', 'Water Bodies']
colors = ['#2ca02c', '#e6c229', '#1f77b4']

print(f"Distribution: Veg={sizes[0]:.1f}%, Arid={sizes[1]:.1f}%, Water={sizes[2]:.1f}%")

# Setup the figure (Flat, academic standard)
fig, ax = plt.subplots(figsize=(10, 7))

wedges, texts, autotexts = ax.pie(
    sizes, 
    labels=labels_text, 
    colors=colors,
    autopct='%1.1f%%', 
    startangle=140, 
    textprops={'fontsize': 15, 'fontweight': 'bold'},
    wedgeprops={'edgecolor': 'black', 'linewidth': 1.5} # Black borders for crispness
)

# Make the percentage text white
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(16)

# Clean Title
plt.title('AI Land Cover Distribution (Upper Awash Basin)', 
          fontsize=18, fontweight='bold', pad=20)

ax.axis('equal') # Ensure perfect circle
plt.tight_layout()

out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_13_Awash_PieChart.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ SUCCESS! Figure 13 saved to: {out_img}")