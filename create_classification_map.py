import os
import numpy as np
import rasterio
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.ticker import FormatStrFormatter
import matplotlib.patheffects as pe

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

print("--- Step 1: Loading 12-Band Satellite Data ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_HighRes_Classification.png"

if os.path.exists(output_png):
    os.remove(output_png)

# Read the raw image
with rasterio.open(input_tif) as src:
    # Read B04, B03, B02 for the true-color background
    red = src.read(4)
    green = src.read(3)
    blue = src.read(2)
    bounds = src.bounds
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

    # Read all 12 bands for classification
    data = src.read()
    
# Normalize RGB for visualization
def normalize(band):
    p2, p98 = np.percentile(band, (2, 98))
    return np.clip((band - p2) / (p98 - p2), 0, 1)

rgb = np.dstack((normalize(red), normalize(green), normalize(blue)))
rgb[rgb <= 0] = np.nan # Mask empty space

print("--- Step 2: Running Pixel-Wise K-Means Classification ---")
# Reshape the 12-band data from (12, H, W) to (H*W, 12)
height, width = data.shape[1], data.shape[2]
data_reshaped = data.reshape(12, -1).T

# Remove NaNs and zeroes for clustering
valid_idx = ~np.all(data_reshaped == 0, axis=1)
valid_data = data_reshaped[valid_idx]

# We will classify into 5 distinct land cover classes
kmeans = KMeans(n_clusters=5, random_state=42, n_init=5)
print("Fitting K-Means model on millions of pixels... (This might take a minute)")
kmeans.fit(valid_data)

# Predict classes for the valid pixels
classes = kmeans.predict(valid_data)

# Reconstruct the classified image array
classified_image = np.full(data_reshaped.shape[0], -1)
classified_image[valid_idx] = classes
classified_image = classified_image.reshape(height, width)

# Mask the empty space (-1) so it's transparent
classified_image = np.ma.masked_where(classified_image == -1, classified_image)

print("--- Step 3: Plotting the Map ---")
fig, ax = plt.subplots(figsize=(14, 12), dpi=600)
fig.patch.set_facecolor('white')

# Plot true color basemap
ax.imshow(rgb, extent=extent, alpha=1.0)

# Define custom colors for the 5 classes (Forest, Cropland, Water, Bare Soil, Urban/Other)
# These are standard remote sensing colors
class_colors = ['#006400', '#FFD700', '#1E90FF', '#A52A2A', '#808080']
cmap = ListedColormap(class_colors)

# Overlay the classified image with 60% opacity
ax.imshow(classified_image, cmap=cmap, extent=extent, alpha=0.6)

ax.set_xlim(extent[0], extent[1])
ax.set_ylim(extent[2], extent[3])

# Format Grid and Ticks
ax.grid(True, color='white', linestyle='--', linewidth=0.5, alpha=0.7)
ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f°E'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f°N'))
ax.tick_params(axis='both', which='major', labelsize=10, direction='out', length=5)

# Titles and Labels
ax.set_title('Study Area: Gamo-Gofa, Ethiopia\nSentinel-2 12-Band Land Cover Classification', fontsize=18, fontweight='bold', pad=15)
ax.set_xlabel('Longitude (°E)', fontsize=14, fontweight='bold')
ax.set_ylabel('Latitude (°N)', fontsize=14, fontweight='bold')

# Custom Legend
legend_elements = [
    Patch(facecolor='#006400', label='Dense Forest'),
    Patch(facecolor='#FFD700', label='Agriculture / Cropland'),
    Patch(facecolor='#1E90FF', label='Water Body'),
    Patch(facecolor='#A52A2A', label='Bare Soil / Rock'),
    Patch(facecolor='#808080', label='Urban / Sparse Vegetation')
]
ax.legend(handles=legend_elements, loc='upper left', title='Land Cover Classes', 
          title_fontsize=12, fontsize=11, framealpha=0.9, edgecolor='black')

# Scale Bar
scalebar = ScaleBar(111000, "m", length_fraction=0.15, location='lower right', 
                    box_alpha=0.9, font_properties={'size': 10, 'weight': 'bold'})
ax.add_artist(scalebar)

# North Arrow
x, y, arrow_length = 0.95, 0.15, 0.05
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=14, fontweight='bold',
            xycoords='axes fraction', textcoords='axes fraction')

# Metadata Panel
metadata_text = (
    "Projection: EPSG:4326\n"
    "Data Source: Sentinel-2 L2A (AWS Earth Search)\n"
    "Method: Pixel-wise K-Means Clustering (k=5)\n"
    "Author: Shimeles Tadesse Zelelew\n"
    "Email: shimtad2001g@gmail.com"
)
ax.text(0.01, 0.01, metadata_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='bottom', horizontalalignment='left',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='black'))

plt.tight_layout()

print("--- Step 4: Saving Ultra-High Resolution Map ---")
plt.savefig(output_png, bbox_inches='tight', pad_inches=0.2, facecolor='white')
plt.close()

print(f"[SUCCESS] High-Resolution Classification Map saved to: {output_png}")
