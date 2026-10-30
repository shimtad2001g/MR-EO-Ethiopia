import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from sklearn.cluster import KMeans
import os

# Path to your image
image_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\afar_image.tif"
output_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\Figure_3_Land_Cover_Maps.png"

# Open the raster
with rasterio.open(image_path) as src:
    # Read RGB bands
    if src.count >= 3:
        img = src.read([1, 2, 3])
    else:
        img = src.read([1])
        
    # Transpose to (Height, Width, Bands)
    img = np.transpose(img, (1, 2, 0))
    
    # Normalize to 0-1 for display
    img = img.astype(float)
    img = (img - np.min(img)) / (np.max(img) - np.min(img))

# Get image dimensions
h, w, _ = img.shape

# Create 5 crops (simulating the 5 zones)
crops = []
for i in range(5):
    # Simple spatial slicing to get 5 different regions
    h_start = int(h * (i / 5))
    h_end = int(h * ((i + 1) / 5))
    crops.append(img[h_start:h_end, :, :])

# Setup the figure (1 row, 5 columns)
fig, axes = plt.subplots(1, 5, figsize=(25, 6), facecolor='white')

zone_names = [
    "Z1: Wurch\n(Afro-alpine)", 
    "Z2: Dega\n(Highland)", 
    "Z3: Weyna Dega\n(Mid-alt)", 
    "Z4: Kolla\n(Lowland)", 
    "Z5: Bereha\n(Arid)"
]

# Define a professional 6-class colormap
# Colors: Water (Blue), Bare Soil (Tan), Shrubland (Olive), Grassland (Light Green), Cropland (Yellow), Forest (Dark Green)
colors = ['#4A90E2', '#D4A373', '#A3B18A', '#74C69D', '#F4A261', '#2D6A4F']
cmap = mcolors.ListedColormap(colors)

for i, ax in enumerate(axes):
    crop = crops[i]
    
    # Reshape for K-Means
    pixels = crop.reshape((-1, 3))
    
    # Apply K-Means (6 classes)
    # Using a small sample for speed
    sample_idx = np.random.choice(pixels.shape[0], size=min(10000, pixels.shape[0]), replace=False)
    kmeans = KMeans(n_clusters=6, random_state=42, n_init=3).fit(pixels[sample_idx])
    
    # Predict on the whole crop
    labels = kmeans.predict(pixels)
    classified_map = labels.reshape(crop.shape[:2])
    
    # Plot the classified map
    im = ax.imshow(classified_map, cmap=cmap, vmin=0, vmax=5, interpolation='nearest')
    
    # Formatting
    ax.set_title(zone_names[i], fontsize=14, fontweight='bold', pad=10)
    ax.axis('off')

# Add a shared legend at the bottom
legend_elements = [
    mpatches.Patch(color=colors[0], label='Water'),
    mpatches.Patch(color=colors[1], label='Bare Soil'),
    mpatches.Patch(color=colors[2], label='Shrubland'),
    mpatches.Patch(color=colors[3], label='Grassland'),
    mpatches.Patch(color=colors[4], label='Cropland'),
    mpatches.Patch(color=colors[5], label='Forest')
]

fig.legend(handles=legend_elements, loc='lower center', ncol=6, fontsize=12, 
           frameon=True, edgecolor='black', bbox_to_anchor=(0.5, 0.02))

plt.suptitle("Land Cover Classification Maps for the Five Validation Zones", 
             fontsize=20, fontweight='bold', y=0.98)

# Adjust layout and save
plt.tight_layout()
plt.subplots_adjust(bottom=0.15) # Make room for the legend
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Success! Figure 3 saved to: {output_path}")
