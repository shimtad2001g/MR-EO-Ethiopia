import os
import numpy as np
import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Rectangle
from pyproj import Transformer

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

print("--- Step 1: Loading Local Data ---")
# Note: We are now reading the original 12-band image to get the RGB true color
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
carbon_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
ethiopia_gpkg = r"D:\GamoGofa_Carbon_Assessment\02_Data\01_Boundaries\Processed\Ethiopia_ADM2_Zone_Boundary.gpkg"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_TrueColor_Map.png"

if os.path.exists(output_png):
    os.remove(output_png)

# Read the True Color (RGB) from the original 12-band image
with rasterio.open(input_tif) as src:
    # Our 12 bands are ["B01", "B02", "B03", "B04", "B05", ...]
    # B04 is Red (index 3), B03 is Green (index 2), B02 is Blue (index 1)
    red = src.read(4).astype(np.float32)
    green = src.read(3).astype(np.float32)
    blue = src.read(2).astype(np.float32)
    
    bounds = src.bounds
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    
    # Normalize RGB to 0-1 for matplotlib
    def normalize(band):
        p2, p98 = np.percentile(band, (2, 98))
        return np.clip((band - p2) / (p98 - p2), 0, 1)
        
    rgb = np.dstack((normalize(red), normalize(green), normalize(blue)))

# Read Carbon Data
with rasterio.open(carbon_tif) as src:
    carbon_data = src.read(1)

# Mask Carbon NoData
carbon_data = np.ma.masked_where((carbon_data == -9999) | (carbon_data <= 1.0), carbon_data)

print("--- Step 2: Building the Masterpiece ---")
fig, ax = plt.subplots(figsize=(16.5, 11.7), dpi=600)
fig.patch.set_facecolor('white')

# 1. Plot the True Color Satellite Basemap
ax.imshow(rgb, extent=extent)

# 2. Plot the Carbon Heatmap on top (with 65% opacity)
cmap = plt.get_cmap('RdYlGn')
cmap.set_bad(color=(0, 0, 0, 0)) 
im = ax.imshow(carbon_data, cmap=cmap, extent=extent, vmin=1.0, vmax=np.max(carbon_data), alpha=0.65)

ax.set_xlim(extent[0], extent[1])
ax.set_ylim(extent[2], extent[3])

# Format Axes
transformer = Transformer.from_crs("EPSG:4326", "EPSG:4326", always_xy=True) # Already in WGS84
xticks = ax.get_xticks()
yticks = ax.get_yticks()
ax.set_xticklabels([f"{x:.2f}°E" for x in xticks], fontsize=10)
ax.set_yticklabels([f"{y:.2f}°N" for y in yticks], fontsize=10)

ax.tick_params(axis='both', which='major', labelsize=10)
ax.set_xlabel('Longitude (°E)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Latitude (°N)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Gamo-Gofa Carbon Biomass Prediction (True-Color Satellite Basemap)', fontsize=20, fontweight='bold', pad=20)

# Add Colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.04, aspect=30)
cbar.set_label('Predicted Carbon Biomass (tons/ha)', rotation=270, labelpad=25, fontsize=12, fontweight='bold')

# Add Scale Bar (Calculated for Gamo-Gofa ~6°N)
scalebar = ScaleBar(111000, "m", length_fraction=0.15, location='lower left', box_alpha=0.8, font_properties={'size': 10, 'weight': 'bold'})
ax.add_artist(scalebar)

# Add North Arrow
x, y, arrow_length = 0.95, 0.15, 0.05
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=14, fontweight='bold',
            xycoords='axes fraction', textcoords='axes fraction')

# Add Metadata Text
metadata_text = "Projection: WGS 84 (EPSG:4326)\nBasemap: Local Sentinel-2 True Color\nModel: 12-Band ResNet18"
ax.text(0.98, 0.02, metadata_text, transform=ax.transAxes, fontsize=9,
        verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

# Add Inset Map
print("--- Step 3: Adding Inset Map ---")
ax_inset = fig.add_axes([0.68, 0.65, 0.18, 0.18])
try:
    ethiopia = gpd.read_file(ethiopia_gpkg)
    ethiopia.plot(ax=ax_inset, color='lightgray', edgecolor='black', linewidth=0.5)
    
    rect = Rectangle((extent[0], extent[2]), 
                     extent[1] - extent[0], 
                     extent[3] - extent[2],
                     linewidth=2, edgecolor='red', facecolor='none')
    ax_inset.add_patch(rect)
    
    ax_inset.set_title("Ethiopia Context", fontsize=10, fontweight='bold')
    ax_inset.set_xticks([])
    ax_inset.set_yticks([])
    ax_inset.set_facecolor('#f0f0f0')
except Exception as e:
    print(f"Could not load inset map: {e}")

plt.tight_layout()

print("--- Step 4: Saving Ultra-High Resolution Map ---")
plt.savefig(output_png, bbox_inches='tight', pad_inches=0.3, facecolor='white')
plt.close()

print(f"[SUCCESS] Ultimate map saved to: {output_png}")
