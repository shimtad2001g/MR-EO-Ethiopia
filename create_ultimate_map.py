import os
import numpy as np
import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe

# Set global font to avoid black box issues
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

print("--- Step 1: Loading Data ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
ethiopia_gpkg = r"D:\GamoGofa_Carbon_Assessment\02_Data\01_Boundaries\Processed\Ethiopia_ADM2_Zone_Boundary.gpkg"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Ultimate_Map.png"

# Clean up if file exists to prevent lock errors
if os.path.exists(output_png):
    os.remove(output_png)

# Read raster
with rasterio.open(input_tif) as src:
    data = src.read(1)
    bounds = src.bounds
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

# Mask NoData and empty space
data = np.ma.masked_where((data == -9999) | (data <= 1.0), data)

print("--- Step 2: Building the Masterpiece ---")
# Setup Figure (A4 Landscape)
fig, ax = plt.subplots(figsize=(16.5, 11.7), dpi=300)
fig.patch.set_facecolor('white')

# Plot Raster
cmap = plt.get_cmap('RdYlGn')
cmap.set_bad(color='white') # Masked pixels become white
im = ax.imshow(data, cmap=cmap, extent=extent, vmin=1.0, vmax=np.max(data))

# Set extent and Neatline
ax.set_xlim(bounds.left, bounds.right)
ax.set_ylim(bounds.bottom, bounds.top)

# Add Grid and Lat/Long Labels
ax.grid(True, linestyle='--', color='gray', alpha=0.5)
ax.tick_params(axis='both', which='major', labelsize=10)
ax.set_xlabel('Longitude (°E)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Latitude (°N)', fontsize=12, fontweight='bold', labelpad=10)

# Add Title
ax.set_title('Gamo-Gofa 12-Band Carbon Biomass Prediction', fontsize=20, fontweight='bold', pad=20)

# Add Colorbar Legend
cbar = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.04, aspect=30)
cbar.set_label('Predicted Carbon Biomass (tons/ha)', rotation=270, labelpad=25, fontsize=12, fontweight='bold')

# Add Scale Bar
scalebar = ScaleBar(111000, "m", length_fraction=0.15, location='lower left', 
                    box_alpha=0.8, font_properties={'size': 10, 'weight': 'bold'})
ax.add_artist(scalebar)

# Add North Arrow
x, y, arrow_length = 0.95, 0.15, 0.05
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=14, fontweight='bold',
            xycoords='axes fraction', textcoords='axes fraction')

# Add Metadata Text (Bottom Right)
metadata_text = "Projection: WGS 84 (EPSG:4326)\nData: Sentinel-2 L2A (AWS)\nModel: 12-Band ResNet18"
ax.text(0.98, 0.02, metadata_text, transform=ax.transAxes, fontsize=9,
        verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

# Add Inset Map (Top Right)
print("--- Step 3: Adding Inset Map ---")
# Create inset axes: [left, bottom, width, height]
ax_inset = fig.add_axes([0.68, 0.65, 0.18, 0.18])
try:
    ethiopia = gpd.read_file(ethiopia_gpkg)
    ethiopia.plot(ax=ax_inset, color='lightgray', edgecolor='black', linewidth=0.5)
    
    # Add Red Box for Gamo-Gofa extent
    rect = Rectangle((bounds.left, bounds.bottom), 
                     bounds.right - bounds.left, 
                     bounds.top - bounds.bottom,
                     linewidth=2, edgecolor='red', facecolor='none')
    ax_inset.add_patch(rect)
    
    ax_inset.set_title("Ethiopia Context", fontsize=10, fontweight='bold')
    ax_inset.set_xticks([])
    ax_inset.set_yticks([])
    ax_inset.set_facecolor('#f0f0f0')
except Exception as e:
    print(f"Could not load inset map: {e}")

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.9, right=0.9)

print("--- Step 4: Saving Publication-Ready Map ---")
plt.savefig(output_png, bbox_inches='tight', pad_inches=0.3, facecolor='white')
plt.close()

print(f"[SUCCESS] Ultimate map saved to: {output_png}")
