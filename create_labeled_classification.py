import os
import numpy as np
import rasterio
from sklearn.cluster import KMeans
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.ticker import FormatStrFormatter
import matplotlib.patheffects as pe

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

print("--- Step 1: Loading Data ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
ethiopia_gpkg = r"D:\GamoGofa_Carbon_Assessment\02_Data\01_Boundaries\Processed\Ethiopia_ADM2_Zone_Boundary.gpkg"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Final_Classified_Map.png"

if os.path.exists(output_png):
    os.remove(output_png)

with rasterio.open(input_tif) as src:
    red = src.read(4)
    green = src.read(3)
    blue = src.read(2)
    bounds = src.bounds
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    data = src.read()

# Normalize RGB
def normalize(band):
    p2, p98 = np.percentile(band, (2, 98))
    return np.clip((band - p2) / (p98 - p2), 0, 1)

rgb = np.dstack((normalize(red), normalize(green), normalize(blue)))
rgb[rgb <= 0] = np.nan 

print("--- Step 2: Running K-Means Classification ---")
height, width = data.shape[1], data.shape[2]
data_reshaped = data.reshape(12, -1).T
valid_idx = ~np.all(data_reshaped == 0, axis=1)
valid_data = data_reshaped[valid_idx]

kmeans = KMeans(n_clusters=5, random_state=42, n_init=5)
kmeans.fit(valid_data)
classes = kmeans.predict(valid_data)

classified_image = np.full(data_reshaped.shape[0], -1)
classified_image[valid_idx] = classes
classified_image = classified_image.reshape(height, width)
classified_image = np.ma.masked_where(classified_image == -1, classified_image)

print("--- Step 3: Plotting the Map with Labels ---")
fig = plt.figure(figsize=(16, 12), dpi=600)
fig.patch.set_facecolor('white')

ax = fig.add_axes([0.08, 0.15, 0.65, 0.70])

# Plot Basemap & Classification
ax.imshow(rgb, extent=extent, alpha=1.0)
class_colors = ['#006400', '#FFD700', '#1E90FF', '#A52A2A', '#808080']
cmap = ListedColormap(class_colors)
ax.imshow(classified_image, cmap=cmap, extent=extent, alpha=0.6)

ax.set_xlim(extent[0], extent[1])
ax.set_ylim(extent[2], extent[3])

# Add Vector Boundaries & Labels
print("Adding Labels...")
try:
    zones = gpd.read_file(ethiopia_gpkg)
    gamo_gofa_zones = zones[zones['ADM2_EN'].isin(['Gamo', 'Gofa'])]
    gamo_gofa_zones.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.5, linestyle='--', zorder=15)
    
    for idx, row in gamo_gofa_zones.iterrows():
        centroid = row.geometry.centroid
        if extent[0] < centroid.x < extent[1] and extent[2] < centroid.y < extent[3]:
            ax.text(centroid.x, centroid.y, row['ADM2_EN'], fontsize=14, fontweight='bold', 
                    ha='center', va='center', zorder=20,
                    path_effects=[pe.withStroke(linewidth=4, foreground="white")])
except Exception as e:
    print(f"Could not load zones: {e}")

# Add Lake Chamo
ax.text(37.55, 5.85, "Lake\nChamo", fontsize=12, fontstyle='italic', 
        ha='center', va='center', zorder=20, color='darkblue',
        path_effects=[pe.withStroke(linewidth=3, foreground="white")])

# Format Grid
ax.grid(True, color='white', linestyle='--', linewidth=0.7, alpha=0.8, zorder=10)
ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f°E'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f°N'))
ax.tick_params(axis='both', which='major', labelsize=11, top=True, right=True, labeltop=True, labelright=True, direction='inout', length=6)

# Outer Neatline
for spine in ax.spines.values():
    spine.set_linewidth(2)
    spine.set_color('black')

# Title
fig.text(0.405, 0.92, 'Gamo-Gofa High-Resolution Land Cover Classification', ha='center', va='center', fontsize=20, fontweight='bold')
fig.text(0.405, 0.88, 'Sentinel-2 12-Band Pixel-Wise K-Means Analysis', ha='center', va='center', fontsize=14, fontstyle='italic')

# Legend
legend_elements = [
    Patch(facecolor='#006400', label='Dense Forest'),
    Patch(facecolor='#FFD700', label='Agriculture / Cropland'),
    Patch(facecolor='#1E90FF', label='Water Body'),
    Patch(facecolor='#A52A2A', label='Bare Soil / Rock'),
    Patch(facecolor='#808080', label='Urban / Sparse Vegetation')
]
ax.legend(handles=legend_elements, loc='upper left', title='Land Cover Classes', 
          title_fontsize=11, fontsize=10, framealpha=0.9, edgecolor='black')

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
fig.text(0.08, 0.02, metadata_text, ha='left', va='bottom', fontsize=10,
         fontfamily='monospace', linespacing=1.5,
         bbox=dict(boxstyle='round,pad=0.8', facecolor='white', alpha=0.9, edgecolor='black'))

# Outer Neatline (entire figure)
fig.add_artist(Rectangle((0.02, 0.02), 0.96, 0.96, transform=fig.transFigure, 
                         facecolor='none', edgecolor='black', linewidth=3, zorder=100))

print("--- Step 4: Saving Final Map ---")
plt.savefig(output_png, bbox_inches='tight', pad_inches=0.3, facecolor='white')
plt.close()

print(f"[SUCCESS] Labeled Classification Map saved to: {output_png}")
