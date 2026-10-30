import os
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.fill import fillnodata
from scipy.ndimage import gaussian_filter
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Rectangle
from matplotlib.ticker import FormatStrFormatter
import matplotlib.patheffects as pe

# Suppress GDAL warning
os.environ['GDAL_DATA'] = r"C:\Users\SHIMELES_TADESSE\.conda\envs\geospatial_auditor\Library\share\gdal"

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

print("--- Step 1: Loading and Reprojecting Local Data to WGS84 ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
carbon_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
ethiopia_gpkg = r"D:\GamoGofa_Carbon_Assessment\02_Data\01_Boundaries\Processed\Ethiopia_ADM2_Zone_Boundary.gpkg"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Publication_Grade_Final.png"

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

# --- FIX 1: Fill small internal holes and smooth the 256x256 checkerboard effect ---
# Mask original NoData
original_mask = (carbon_data == -9999) | (carbon_data <= 1.0)
carbon_data_masked = np.ma.masked_where(original_mask, carbon_data)

# Fill small holes inside the valid area using nearest neighbor
filled_data = fillnodata(carbon_data, mask=(~original_mask).astype(np.uint8), max_search_distance=100)

# Apply a Gaussian filter to blend the 256x256 patch edges (sigma=3 is a gentle smoothing)
smoothed_data = gaussian_filter(filled_data, sigma=3)

# Re-apply the original external mask to keep the boundary shape strict
final_carbon_data = np.ma.masked_where(original_mask, smoothed_data)

# --- TIGHT CROPPING to remove the white wedge ---
valid_rows = np.where(np.any(~final_carbon_data.mask, axis=1))[0]
valid_cols = np.where(np.any(~final_carbon_data.mask, axis=0))[0]

if len(valid_rows) > 0 and len(valid_cols) > 0:
    min_row, max_row = valid_rows[0], valid_rows[-1]
    min_col, max_col = valid_cols[0], valid_cols[-1]
    
    x_res = (extent_4326[1] - extent_4326[0]) / width
    y_res = (extent_4326[3] - extent_4326[2]) / height
    
    new_extent = [
        extent_4326[0] + (min_col * x_res),
        extent_4326[0] + ((max_col + 1) * x_res),
        extent_4326[3] - ((max_row + 1) * y_res),
        extent_4326[3] - (min_row * y_res)
    ]
    
    rgb_final = rgb_final[min_row:max_row+1, min_col:max_col+1]
    final_carbon_data = final_carbon_data[min_row:max_row+1, min_col:max_col+1]
    extent_4326 = new_extent

print("--- Step 2: Building the Publication-Grade Map ---")
fig = plt.figure(figsize=(18, 12), dpi=600)
fig.patch.set_facecolor('white')

# Main Map Axes (Adjusted for cleaner layout)
ax = fig.add_axes([0.08, 0.25, 0.52, 0.60]) 

# 1. Plot Basemap and Smoothed Heatmap
ax.imshow(rgb_final, extent=extent_4326)
cmap = plt.get_cmap('RdYlGn')
cmap.set_bad(color=(0, 0, 0, 0)) 
im = ax.imshow(final_carbon_data, cmap=cmap, extent=extent_4326, vmin=1.0, vmax=np.max(final_carbon_data), alpha=0.65)

ax.set_xlim(extent_4326[0], extent_4326[1])
ax.set_ylim(extent_4326[2], extent_4326[3])

# 2. Overlay Zone Boundaries
try:
    zones = gpd.read_file(ethiopia_gpkg)
    gamo_gofa_zones = zones[zones['ADM2_EN'].isin(['Gamo', 'Gofa'])]
    gamo_gofa_zones.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.5, linestyle='--', zorder=15)
    
    for idx, row in gamo_gofa_zones.iterrows():
        centroid = row.geometry.centroid
        if extent_4326[0] < centroid.x < extent_4326[1] and extent_4326[2] < centroid.y < extent_4326[3]:
            ax.text(centroid.x, centroid.y, row['ADM2_EN'], fontsize=12, fontweight='bold', 
                    ha='center', va='center', zorder=20,
                    path_effects=[pe.withStroke(linewidth=3, foreground="white")])
except Exception as e:
    pass

# Add Lake Chamo Annotation
ax.text(37.55, 5.85, "Lake\nChamo", fontsize=11, fontstyle='italic', 
        ha='center', va='center', zorder=20, color='darkblue',
        path_effects=[pe.withStroke(linewidth=3, foreground="white")])

# 3. Graticule
ax.set_axisbelow(False)
ax.grid(True, which='major', color='black', linestyle='-', linewidth=0.6, alpha=0.5, zorder=10)
ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f°E'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f°N'))
ax.tick_params(axis='both', which='major', labelsize=10, top=True, right=True, labeltop=True, labelright=True, direction='inout', length=5)

# 4. Inner Neatline
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

# 5. Title and Subtitle
fig.text(0.34, 0.92, 'Gamo-Gofa Carbon Biomass Prediction', ha='center', va='center', fontsize=22, fontweight='bold')
fig.text(0.34, 0.88, 'High-Resolution 12-Band Multispectral Deep Learning Analysis', ha='center', va='center', fontsize=14, fontstyle='italic')

# 6. Colorbar
cbar_ax = fig.add_axes([0.63, 0.25, 0.015, 0.60])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.set_label('Predicted Carbon Biomass (tons/ha)', rotation=270, labelpad=25, fontsize=13, fontweight='bold')

# 7. Scale Bar & North Arrow
scalebar = ScaleBar(111000, "m", length_fraction=0.15, location='lower left', box_alpha=0.9, font_properties={'size': 9, 'weight': 'bold'})
ax.add_artist(scalebar)
x, y, arrow_length = 0.92, 0.12, 0.06
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=12, fontweight='bold',
            xycoords='axes fraction', textcoords='axes fraction')

# 8. Inset Map
ax_inset = fig.add_axes([0.72, 0.60, 0.12, 0.15])
try:
    ethiopia = gpd.read_file(ethiopia_gpkg)
    ethiopia.plot(ax=ax_inset, color='lightgray', edgecolor='black', linewidth=0.3)
    rect = Rectangle((extent_4326[0], extent_4326[2]), extent_4326[1] - extent_4326[0], extent_4326[3] - extent_4326[2], linewidth=1.5, edgecolor='red', facecolor='none')
    ax_inset.add_patch(rect)
    ax_inset.set_title("Ethiopia Context", fontsize=9, fontweight='bold')
    ax_inset.set_xticks([])
    ax_inset.set_yticks([])
    for spine in ax_inset.spines.values():
        spine.set_linewidth(1)
except Exception as e:
    pass

# 9. Metadata Panel
metadata_text = (
    "--- CARTOGRAPHIC METADATA ---\n"
    "Projection: WGS 84 (EPSG:4326)\n"
    "Spatial Resolution: 10m\n"
    "Grid Interval: 0.10 Decimal Degrees\n\n"
    "--- METHODOLOGY & DATA SOURCES ---\n"
    "Model: 12-Band ResNet18 Deep Learning Regression\n"
    "Source: Sentinel-2 L2A Surface Reflectance (AWS Earth Search)\n"
    "Target: GEDI L4A Aboveground Biomass Density (AGBD) Proxy\n"
    "Accuracy: RMSE 2.74 tons/ha\n"
    "Boundaries: Gamo & Gofa Zones (ADM2)\n\n"
    "--- AUTHOR ---\n"
    "Map created by Shimeles Tadesse Zelewe\n"
    "Email: shimtad2001g@gmail.com"
)

fig.text(0.08, 0.02, metadata_text, ha='left', va='bottom', fontsize=8.5, 
         fontfamily='monospace', linespacing=1.5,
         bbox=dict(boxstyle='square,pad=1', facecolor='white', edgecolor='black', linewidth=1.5))

# --- FIX 2: Add the Outer Neatline (Border enclosing the entire figure) ---
fig.add_artist(Rectangle((0.02, 0.02), 0.96, 0.96, transform=fig.transFigure, 
                         facecolor='none', edgecolor='black', linewidth=3, zorder=100))

print("--- Step 3: Saving Publication-Grade Map ---")
plt.savefig(output_png, bbox_inches='tight', pad_inches=0.3, facecolor='white')
plt.close()

print(f"[SUCCESS] Publication-Grade Map saved to: {output_png}")
