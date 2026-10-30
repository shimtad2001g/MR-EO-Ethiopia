import os
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Rectangle
import contextily as ctx
import pyproj
from pyproj import Transformer

# Set global font
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

print("--- Step 1: Loading and Reprojecting Data to Web Mercator ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
ethiopia_gpkg = r"D:\GamoGofa_Carbon_Assessment\02_Data\01_Boundaries\Processed\Ethiopia_ADM2_Zone_Boundary.gpkg"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Ultra_HighRes_Map.png"

if os.path.exists(output_png):
    os.remove(output_png)

# Read raster and reproject to EPSG:3857 (Web Mercator) for the basemap
with rasterio.open(input_tif) as src:
    src_crs = src.crs
    transform, width, height = calculate_default_transform(
        src.crs, 'EPSG:3857', src.width, src.height, *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({
        'crs': 'EPSG:3857',
        'transform': transform,
        'width': width,
        'height': height
    })
    
    data = np.empty((height, width), dtype=np.float32)
    reproject(
        source=rasterio.band(src, 1),
        destination=data,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs='EPSG:3857',
        resampling=Resampling.bilinear
    )
    
    bounds_3857 = rasterio.transform.array_bounds(height, width, transform)
    extent_3857 = [bounds_3857[0], bounds_3857[2], bounds_3857[1], bounds_3857[3]]

# Mask NoData
data = np.ma.masked_where((data == -9999) | (data <= 1.0), data)

print("--- Step 2: Building the Masterpiece with Basemap ---")
# Setup Figure (A4 Landscape at Ultra-High 600 DPI)
fig, ax = plt.subplots(figsize=(16.5, 11.7), dpi=600)
fig.patch.set_facecolor('white')

# Plot Raster (with alpha for transparency)
cmap = plt.get_cmap('RdYlGn')
# THE FIX: Use RGBA tuple (0,0,0,0) instead of the string 'transparent'
cmap.set_bad(color=(0, 0, 0, 0)) 
im = ax.imshow(data, cmap=cmap, extent=extent_3857, vmin=1.0, vmax=np.max(data), alpha=0.65)

# Set extent
ax.set_xlim(extent_3857[0], extent_3857[1])
ax.set_ylim(extent_3857[2], extent_3857[3])

# Add High-Resolution Esri World Imagery Basemap
print("Fetching High-Resolution Esri Basemap (This might take a moment)...")
try:
    ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zoom=13, attribution_size=6)
except Exception as e:
    print(f"Basemap fetch failed: {e}. Falling back to OpenStreetMap.")
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=13, attribution_size=6)

# Format Axes to show Lat/Lon (even though data is in 3857)
transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

# Create custom ticks
xticks = ax.get_xticks()
yticks = ax.get_yticks()
ax.set_xticklabels([f"{transformer.transform(x, extent_3857[2])[0]:.2f}°E" for x in xticks], fontsize=10)
ax.set_yticklabels([f"{transformer.transform(extent_3857[0], y)[1]:.2f}°N" for y in yticks], fontsize=10)

ax.tick_params(axis='both', which='major', labelsize=10)
ax.set_xlabel('Longitude', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Latitude', fontsize=12, fontweight='bold', labelpad=10)
ax.set_title('Gamo-Gofa 12-Band Carbon Biomass Prediction (High-Res Basemap)', fontsize=20, fontweight='bold', pad=20)

# Add Colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.04, aspect=30)
cbar.set_label('Predicted Carbon Biomass (tons/ha)', rotation=270, labelpad=25, fontsize=12, fontweight='bold')

# Add Scale Bar (calculated for Web Mercator)
scalebar = ScaleBar(1, "m", length_fraction=0.15, location='lower left', 
                    box_alpha=0.8, font_properties={'size': 10, 'weight': 'bold'})
ax.add_artist(scalebar)

# Add North Arrow
x, y, arrow_length = 0.95, 0.15, 0.05
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=14, fontweight='bold',
            xycoords='axes fraction', textcoords='axes fraction')

# Add Metadata Text
metadata_text = "Projection: EPSG:3857 (Web Mercator)\nBasemap: Esri World Imagery\nData: Sentinel-2 L2A (AWS)"
ax.text(0.98, 0.02, metadata_text, transform=ax.transAxes, fontsize=9,
        verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

# Add Inset Map (Top Right)
print("--- Step 3: Adding Inset Map ---")
ax_inset = fig.add_axes([0.68, 0.65, 0.18, 0.18])
try:
    ethiopia = gpd.read_file(ethiopia_gpkg)
    ethiopia.plot(ax=ax_inset, color='lightgray', edgecolor='black', linewidth=0.5)
    
    # Convert Gamo-Gofa bounds back to 4326 for the inset red box
    transformer_4326 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    min_lon, min_lat = transformer_4326.transform(extent_3857[0], extent_3857[2])
    max_lon, max_lat = transformer_4326.transform(extent_3857[1], extent_3857[3])
    
    rect = Rectangle((min_lon, min_lat), 
                     max_lon - min_lon, 
                     max_lat - min_lat,
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

print("--- Step 4: Saving Ultra-High Resolution Map ---")
# Saving at 600 DPI
plt.savefig(output_png, bbox_inches='tight', pad_inches=0.3, facecolor='white')
plt.close()

print(f"[SUCCESS] Ultra-High Res map saved to: {output_png}")
