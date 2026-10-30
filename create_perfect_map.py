import os
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Rectangle
from matplotlib.ticker import FormatStrFormatter

# Suppress the GDAL warning
os.environ['GDAL_DATA'] = r"C:\Users\SHIMELES_TADESSE\.conda\envs\geospatial_auditor\Library\share\gdal"

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

print("--- Step 1: Loading and Reprojecting Local Data to WGS84 ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
carbon_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
ethiopia_gpkg = r"D:\GamoGofa_Carbon_Assessment\02_Data\01_Boundaries\Processed\Ethiopia_ADM2_Zone_Boundary.gpkg"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Perfect_Map.png"

if os.path.exists(output_png):
    os.remove(output_png)

# Read and Reproject RGB
with rasterio.open(input_tif) as src:
    transform, width, height = calculate_default_transform(src.crs, 'EPSG:4326', src.width, src.height, *src.bounds)
    
    # Read bands
    red = src.read(4)
    green = src.read(3)
    blue = src.read(2)
    
    # Reproject arrays
    kwargs = src.meta.copy()
    kwargs.update({'crs': 'EPSG:4326', 'transform': transform, 'width': width, 'height': height})
    
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

# Normalize RGB and Mask Empty Space (0,0,0)
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

# Mask Carbon NoData
carbon_data = np.ma.masked_where((carbon_data == -9999) | (carbon_data <= 1.0), carbon_data)

print("--- Step 2: Building the Perfect Map ---")
fig, ax = plt.subplots(figsize=(16.5, 11.7), dpi=600)
fig.patch.set_facecolor('white')

# 1. Plot True Color Basemap
ax.imshow(rgb_final, extent=extent_4326)

# 2. Plot Carbon Heatmap
cmap = plt.get_cmap('RdYlGn')
cmap.set_bad(color=(0, 0, 0, 0)) 
im = ax.imshow(carbon_data, cmap=cmap, extent=extent_4326, vmin=1.0, vmax=np.max(carbon_data), alpha=0.65)

ax.set_xlim(extent_4326[0], extent_4326[1])
ax.set_ylim(extent_4326[2], extent_4326[3])

# Format Axes (Now correctly in Degrees)
ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f°E'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f°N'))
ax.tick_params(axis='both', which='major', labelsize=10)
ax.set_xlabel('Longitude', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Latitude', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Gamo-Gofa Carbon Biomass Prediction (True-Color Satellite Basemap)', fontsize=20, fontweight='bold', pad=20)

# Add Colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.04, aspect=30)
cbar.set_label('Predicted Carbon Biomass (tons/ha)', rotation=270, labelpad=25, fontsize=12, fontweight='bold')

# Add Scale Bar
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
    
    rect = Rectangle((extent_4326[0], extent_4326[2]), 
                     extent_4326[1] - extent_4326[0], 
                     extent_4326[3] - extent_4326[2],
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

print(f"[SUCCESS] Perfect map saved to: {output_png}")
