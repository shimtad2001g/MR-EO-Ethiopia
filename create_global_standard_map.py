import os
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Rectangle
from matplotlib.ticker import FormatStrFormatter

# Suppress GDAL warning
os.environ['GDAL_DATA'] = r"C:\Users\SHIMELES_TADESSE\.conda\envs\geospatial_auditor\Library\share\gdal"

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

print("--- Step 1: Loading and Reprojecting Local Data to WGS84 ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
carbon_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
ethiopia_gpkg = r"D:\GamoGofa_Carbon_Assessment\02_Data\01_Boundaries\Processed\Ethiopia_ADM2_Zone_Boundary.gpkg"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Global_Standard_Map.png"

if os.path.exists(output_png):
    os.remove(output_png)

# Read and Reproject RGB
with rasterio.open(input_tif) as src:
    transform, width, height = calculate_default_transform(src.crs, 'EPSG:4326', src.width, src.height, *src.bounds)
    red = src.read(4)
    green = src.read(3)
    blue = src.read(2)
    
    rgb_out = np.zeros((3, height, width), dtype=np.float32)
    for i, band in enumerate([red, green, blue]):
        reproject(
            source=band, destination=rgb_out[i],
            src_transform=src.transform, src_crs=src.crs,
            dst_transform=transform, dst_crs='EPSG:4326',
            resampling=Resampling.bilinear
        )
    
    bounds_4326 = rasterio.transform.array_bounds(height, width, transform)
    extent_4326 = [bounds_4326[0], bounds_4326[2], bounds_4326[1], bounds_4326[3]]

# Normalize RGB and Mask Empty Space
rgb_out[rgb_out <= 0] = np.nan
p2, p98 = np.percentile(rgb_out[~np.isnan(rgb_out)], (2, 98))
rgb_out = np.clip((rgb_out - p2) / (p98 - p2), 0, 1)
rgb_final = np.moveaxis(rgb_out, 0, -1)

# Read and Reproject Carbon Data
with rasterio.open(carbon_tif) as src:
    carbon_data = np.empty((height, width), dtype=np.float32)
    reproject(
        source=rasterio.band(src, 1), destination=carbon_data,
        src_transform=src.transform, src_crs=src.crs,
        dst_transform=transform, dst_crs='EPSG:4326',
        resampling=Resampling.bilinear
    )

carbon_data = np.ma.masked_where((carbon_data == -9999) | (carbon_data <= 1.0), carbon_data)

print("--- Step 2: Building the Global Standard Map with Optimized Layout ---")
# Increased figure width slightly to give the colorbar more breathing room
fig = plt.figure(figsize=(22, 14), dpi=600)
fig.patch.set_facecolor('white')

# Main Map Axes
ax = fig.add_axes([0.06, 0.28, 0.55, 0.55]) 

# 1. Plot Basemap and Heatmap
ax.imshow(rgb_final, extent=extent_4326)
cmap = plt.get_cmap('RdYlGn')
cmap.set_bad(color=(0, 0, 0, 0)) 
im = ax.imshow(carbon_data, cmap=cmap, extent=extent_4326, vmin=1.0, vmax=np.max(carbon_data), alpha=0.65)

ax.set_xlim(extent_4326[0], extent_4326[1])
ax.set_ylim(extent_4326[2], extent_4326[3])

# 2. Graticule
ax.set_axisbelow(False)
ax.grid(True, which='major', color='black', linestyle='-', linewidth=0.6, alpha=0.7, zorder=10)
ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f°E'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f°N'))
ax.tick_params(axis='both', which='major', labelsize=11, top=True, right=True, labeltop=True, labelright=True, direction='inout', length=6)

# 3. Neatline
for spine in ax.spines.values():
    spine.set_linewidth(2)
    spine.set_color('black')

# 4. Title and Subtitle
fig.text(0.33, 0.92, 'Gamo-Gofa Carbon Biomass Prediction', ha='center', va='center', fontsize=26, fontweight='bold')
fig.text(0.33, 0.88, 'High-Resolution 12-Band Multispectral Deep Learning Analysis', ha='center', va='center', fontsize=16, fontstyle='italic')

# 5. Colorbar (Increased labelpad to prevent overlap)
cbar_ax = fig.add_axes([0.65, 0.28, 0.02, 0.55])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.set_label('Predicted Carbon Biomass (tons/ha)', rotation=270, labelpad=35, fontsize=14, fontweight='bold')

# 6. Scale Bar & North Arrow
scalebar = ScaleBar(111000, "m", length_fraction=0.15, location='lower left', box_alpha=0.9, font_properties={'size': 11, 'weight': 'bold'})
ax.add_artist(scalebar)
x, y, arrow_length = 0.92, 0.12, 0.06
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=14, fontweight='bold',
            xycoords='axes fraction', textcoords='axes fraction')

# 7. Inset Map
ax_inset = fig.add_axes([0.73, 0.55, 0.15, 0.20])
try:
    ethiopia = gpd.read_file(ethiopia_gpkg)
    ethiopia.plot(ax=ax_inset, color='lightgray', edgecolor='black', linewidth=0.5)
    rect = Rectangle((extent_4326[0], extent_4326[2]), extent_4326[1] - extent_4326[0], extent_4326[3] - extent_4326[2], linewidth=2, edgecolor='red', facecolor='none')
    ax_inset.add_patch(rect)
    ax_inset.set_title("Ethiopia Context", fontsize=11, fontweight='bold')
    ax_inset.set_xticks([])
    ax_inset.set_yticks([])
    ax_inset.set_facecolor('#f0f0f0')
    for spine in ax_inset.spines.values():
        spine.set_linewidth(1.5)
except Exception as e:
    print(f"Could not load inset map: {e}")

# 8. Cartographic Metadata & Author Attribution Panel
metadata_text = (
    "--- CARTOGRAPHIC METADATA ---\n"
    "Projection: WGS 84 (EPSG:4326)\n"
    "Spatial Resolution: 10m\n"
    "Grid Interval: 0.10 Decimal Degrees\n\n"
    "--- METHODOLOGY & DATA SOURCES ---\n"
    "Model: 12-Band ResNet18 Deep Learning Regression\n"
    "Source: Sentinel-2 L2A Surface Reflectance (AWS Earth Search)\n"
    "Target: GEDI L4A Aboveground Biomass Density (AGBD) Proxy\n"
    "Accuracy: RMSE 2.74 tons/ha\n\n"
    "--- AUTHOR ---\n"
    "Map created by Shimeles Tadesse Zelelew\n"
    "Email: shimtad2001g@gmail.com"
)

fig.text(0.06, 0.02, metadata_text, ha='left', va='bottom', fontsize=10, 
         fontfamily='monospace', linespacing=1.6,
         bbox=dict(boxstyle='square,pad=1.2', facecolor='white', edgecolor='black', linewidth=1.5))

print("--- Step 3: Saving Ultra-High Resolution Map ---")
# Added a larger pad_inches to ensure nothing gets cropped on the right edge
plt.savefig(output_png, bbox_inches='tight', pad_inches=0.6, facecolor='white')
plt.close()

print(f"[SUCCESS] Global Standard Map saved to: {output_png}")
