import os, sys
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe
import pyproj
import geopandas as gpd
from matplotlib_scalebar.scalebar import ScaleBar
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

ENV = r"C:\Users\SHIMELES_TADESSE\.conda\envs\geospatial_auditor"
os.environ["GDAL_DATA"] = os.path.join(ENV, r"Library\share\gdal")
os.environ["PROJ_LIB"] = os.path.join(ENV, r"Library\share\proj")
os.environ["PROJ_DATA"] = os.environ["PROJ_LIB"]

BASEMAP_PATH = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
CARBON_PATH = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_map.tif"
OUT_PNG = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Reference_Style.png"

print("--- Loading Basemap ---")
with rasterio.open(BASEMAP_PATH) as src:
    rgb = src.read([4, 3, 2]).astype("float32")
    # Strict swath mask
    valid_mask = np.max(rgb, axis=0) > 5 
    
    p2, p98 = np.percentile(rgb[:, valid_mask], 2), np.percentile(rgb[:, valid_mask], 98)
    rgb = np.clip((rgb - p2) / (p98 - p2 + 1e-9), 0, 1)
    rgb = np.transpose(rgb, (1, 2, 0))
    
    rgba = np.zeros((rgb.shape[0], rgb.shape[1], 4))
    rgba[..., :3] = rgb
    rgba[..., 3] = np.where(valid_mask, 1.0, 0.0)
    
    b = src.bounds
    extent = [b.left, b.right, b.bottom, b.top]
    crs = src.crs
    target_shape = src.shape
    target_transform = src.transform

print("--- Resampling Carbon Raster ---")
with rasterio.open(CARBON_PATH) as src:
    carbon_src = src.read(1).astype("float32")
    carbon_src = np.where((carbon_src <= 0) | (carbon_src > 1000), np.nan, carbon_src)
    carbon_resampled = np.full(target_shape, np.nan, dtype="float32")
    
    reproject(
        source=carbon_src, destination=carbon_resampled,
        src_transform=src.transform, src_crs=src.crs,
        dst_transform=target_transform, dst_crs=crs,
        resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan
    )

print("--- Dynamic Scaling & Masking ---")
# 1. Kill the Phantom Block
carbon_resampled[~valid_mask] = np.nan

# 2. Calculate dynamic percentiles for the color scale to make the map "pop"
valid_carbon = carbon_resampled[~np.isnan(carbon_resampled)]
vmin = np.percentile(valid_carbon, 2)  # Lowest 2% (Deep Red)
vmax = np.percentile(valid_carbon, 98) # Highest 2% (Deep Green)
print(f"Dynamic Scale: {vmin:.1f} to {vmax:.1f} tons/ha")

# 3. Strict Lake Masking (using a huge 0.15 degree buffer to guarantee coverage)
transformer_inv = pyproj.Transformer.from_crs("EPSG:4326", crs, always_xy=True)
lake_pts = [gpd.points_from_xy([37.55], [5.83])[0], gpd.points_from_xy([37.80], [6.30])[0]] 
lakes_gdf = gpd.GeoDataFrame(geometry=[p.buffer(0.15) for p in lake_pts], crs="EPSG:4326")
lakes_utm = lakes_gdf.to_crs(crs)

cols = np.arange(target_shape[1])
rows = np.arange(target_shape[0])
X, Y = np.meshgrid(
    b.left + (cols + 0.5) * (b.right - b.left) / target_shape[1],
    b.top - (rows + 0.5) * (b.top - b.bottom) / target_shape[0]
)

for geom in lakes_utm.geometry:
    minx, miny, maxx, maxy = geom.bounds
    lake_mask = (X >= minx) & (X <= maxx) & (Y >= miny) & (Y <= maxy)
    carbon_resampled[lake_mask] = np.nan

print("--- Building Map ---")
fig = plt.figure(figsize=(15, 10))
ax = fig.add_axes([0.05, 0.08, 0.65, 0.84]) 

ax.imshow(rgba, extent=extent)
# Use the dynamic vmin/vmax for maximum contrast
im = ax.imshow(carbon_resampled, extent=extent, cmap="RdYlGn", alpha=0.65, vmin=vmin, vmax=vmax, interpolation="bicubic")

ax.set_xlim(b.left, b.right)
ax.set_ylim(b.bottom, b.top)
ax.set_aspect("equal")

for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

transformer = pyproj.Transformer.from_crs(crs, "EPSG:4326", always_xy=True)

# Annotated Labels
labels = {
    "Arba Minch": (6.0333, 37.5500),
    "Lake Chamo": (5.8333, 37.5500),
    "Lake Abaya": (6.3000, 37.8000)
}
for name, (lat, lon) in labels.items():
    x, y = transformer_inv.transform(lon, lat)
    if b.left <= x <= b.right and b.bottom <= y <= b.top:
        ax.scatter(x, y, color='red', s=40, zorder=5, edgecolor='white', linewidth=0.8)
        ax.text(x, y + 1500, name, fontsize=11, fontweight='bold', color='black', ha='center',
                path_effects=[pe.withStroke(linewidth=3.5, foreground="white")], zorder=6)

# Graticule
x_ticks = np.linspace(b.left, b.right, 6)
y_ticks = np.linspace(b.bottom, b.top, 6)
lon_labels = [f"{transformer.transform(x, b.bottom)[0]:.2f}°E" for x in x_ticks]
lat_labels = [f"{transformer.transform(b.left, y)[1]:.2f}°N" for y in y_ticks]

ax.set_xticks(x_ticks)
ax.set_yticks(y_ticks)
ax.set_xticklabels(lon_labels, fontsize=11, fontweight='bold')
ax.set_yticklabels(lat_labels, fontsize=11, fontweight='bold')
ax.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.4)

ax.set_title("Gamo-Gofa Carbon Biomass Prediction (True-Color Satellite Basemap)", fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel("Longitude", fontsize=12, fontweight='bold')
ax.set_ylabel("Latitude", fontsize=12, fontweight='bold')

# Colorbar
cax = fig.add_axes([0.85, 0.3, 0.02, 0.4])
cbar = fig.colorbar(im, cax=cax)
cbar.set_label("Predicted Carbon Biomass (tons/ha)", fontsize=12, fontweight='bold', rotation=270, labelpad=25)

# Scalebar
ax.add_artist(ScaleBar(1.0, units="m", location="lower left", length_fraction=0.15, 
                       font_properties={'size': 10, 'weight': 'bold'}, pad=0.5))

# North Arrow
ax.annotate("N", xy=(0.95, 0.15), xytext=(0.95, 0.05), xycoords="axes fraction",
            ha="center", va="center", fontsize=16, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color="black", lw=3))

# Metadata Box
metadata_text = (
    "Projection: WGS 84 (EPSG:4326)\n"
    "Basemap: Local Sentinel-2 True Color\n"
    "Model: 12-Band ResNet18\n"
    "Scale: Dynamically Stretched\n"
    "Masking: Strict Swath & Large Lakes"
)
ax.text(0.02, 0.60, metadata_text, fontsize=10, family='sans-serif',
        va='top', ha='left', transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor="black", alpha=1.0))

# Inset Map
try:
    url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    gdf = gpd.read_file(url)
    eth = gdf[gdf['NAME'] == 'Ethiopia']
    
    axins = inset_axes(ax, width="22%", height="22%", loc='upper left', borderpad=1)
    eth.plot(ax=axins, color='#e0e0e0', edgecolor='black', linewidth=0.5)
    axins.set_xticks([])
    axins.set_yticks([])
    axins.set_title("Ethiopia Context", fontsize=9, fontweight='bold')
    
    lon_min, lat_min = transformer.transform(b.left, b.bottom)
    lon_max, lat_max = transformer.transform(b.right, b.top)
    rect = Rectangle((lon_min, lat_min), lon_max - lon_min, lat_max - lat_min, 
                     fill=False, edgecolor='red', linewidth=2)
    axins.add_patch(rect)
    axins.set_aspect("equal")
except Exception:
    pass

print("--- Saving Map ---")
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("[SUCCESS] Dynamic, High-Contrast Map saved.")
