import os, sys
import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pyproj
import geopandas as gpd
import matplotlib.patheffects as pe
from matplotlib_scalebar.scalebar import ScaleBar
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

ENV = r"C:\Users\SHIMELES_TADESSE\.conda\envs\geospatial_auditor"
os.environ["GDAL_DATA"] = os.path.join(ENV, r"Library\share\gdal")
os.environ["PROJ_LIB"] = os.path.join(ENV, r"Library\share\proj")
os.environ["PROJ_DATA"] = os.environ["PROJ_LIB"]

OUT_PNG = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\Figure1_StudyArea.png"
DATA_DIR = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data"
COUNTRIES_PATH = os.path.join(DATA_DIR, "ne_50m_countries.geojson")
BASEMAP_PATH = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"

print("--- Loading Satellite Basemap ---")
with rasterio.open(BASEMAP_PATH) as src:
    rgb = src.read([4, 3, 2]).astype("float32")
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

print("--- Building Main Study Area Map ---")
fig = plt.figure(figsize=(12, 10))
ax = fig.add_axes([0.08, 0.08, 0.85, 0.85]) 

# Plot the true-color satellite image
ax.imshow(rgba, extent=extent)
ax.set_aspect("equal")
ax.set_xlim(b.left, b.right)
ax.set_ylim(b.bottom, b.top)

# Coordinate Transformers
transformer = pyproj.Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
transformer_inv = pyproj.Transformer.from_crs("EPSG:4326", crs, always_xy=True)

# Add Labels for Towns and Lakes
labels = {
    "Arba Minch": (6.0333, 37.5500, 'red'),
    "Lake Chamo": (5.8333, 37.5500, 'blue'),
    "Lake Abaya": (6.3000, 37.8000, 'blue')
}

for name, (lat, lon, color) in labels.items():
    x, y = transformer_inv.transform(lon, lat)
    if b.left <= x <= b.right and b.bottom <= y <= b.top:
        ax.scatter(x, y, color=color, s=60, zorder=5, edgecolor='white', linewidth=1.5)
        ax.text(x, y + 1500, name, fontsize=12, fontweight='bold', color='black', ha='center',
                path_effects=[pe.withStroke(linewidth=3.5, foreground="white")], zorder=6)

# Formatting
ax.set_title("Study Area: Gamo Gofa Zone (True-Color Satellite Basemap)", fontsize=18, fontweight='bold', pad=15)
ax.set_xlabel("UTM Easting (m)", fontsize=12, fontweight='bold')
ax.set_ylabel("UTM Northing (m)", fontsize=12, fontweight='bold')
ax.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)

# Neatline
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

# Scalebar and North Arrow
ax.add_artist(ScaleBar(1.0, units="m", location="lower left", length_fraction=0.15, 
                       font_properties={'size': 10, 'weight': 'bold'}, pad=0.5))
ax.annotate("N", xy=(0.95, 0.15), xytext=(0.95, 0.05), xycoords="axes fraction",
            ha="center", va="center", fontsize=16, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color="black", lw=3))

print("--- Building Inset Map ---")
gdf_countries = gpd.read_file(COUNTRIES_PATH)
ethiopia = gdf_countries[gdf_countries['NAME'] == 'Ethiopia']

axins = inset_axes(ax, width="25%", height="25%", loc='upper left', borderpad=1)
ethiopia.plot(ax=axins, color='#d9e8f5', edgecolor='black', linewidth=0.8)

# Draw the red box in the inset
lon_min, lat_min = transformer.transform(b.left, b.bottom)
lon_max, lat_max = transformer.transform(b.right, b.top)
rect_inset = Rectangle((lon_min, lat_min), lon_max - lon_min, lat_max - lat_min, 
                       fill=True, facecolor='red', alpha=0.4, edgecolor='red', linewidth=2)
axins.add_patch(rect_inset)

axins.set_xticks([])
axins.set_yticks([])
axins.set_title("Ethiopia Context", fontsize=10, fontweight='bold')
axins.set_aspect("equal")

print("--- Saving Map ---")
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("[SUCCESS] True Figure 1 saved to:", OUT_PNG)
