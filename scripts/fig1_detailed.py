import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import geopandas as gpd
import matplotlib.patheffects as pe
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import rasterio

OUT_PNG = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\Figure1_StudyArea.png"
DATA_DIR = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data"
COUNTRIES_PATH = os.path.join(DATA_DIR, "ne_50m_countries.geojson")
RASTER_PATH = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"

print("--- Loading Data ---")
gdf_countries = gpd.read_file(COUNTRIES_PATH)
ethiopia = gdf_countries[gdf_countries['NAME'] == 'Ethiopia']

# Get the exact bounding box of your satellite data
with rasterio.open(RASTER_PATH) as src:
    b = src.bounds
    # Convert UTM bounds to WGS84 (Lat/Lon)
    import pyproj
    transformer = pyproj.Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True)
    lon_min, lat_min = transformer.transform(b.left, b.bottom)
    lon_max, lat_max = transformer.transform(b.right, b.top)

print("--- Building Map ---")
fig, ax = plt.subplots(figsize=(12, 10))

# 1. Plot Ethiopia as background (light grey)
ethiopia.plot(ax=ax, color='#f4f4f4', edgecolor='black', linewidth=1.5)

# 2. Draw a red box around the detailed study area
rect = Rectangle((lon_min, lat_min), lon_max - lon_min, lat_max - lat_min, 
                 fill=False, edgecolor='red', linewidth=3)
ax.add_patch(rect)

# 3. Set the map extent to ZOOM IN exactly to the study area (with a small buffer)
ax.set_xlim(lon_min - 0.1, lon_max + 0.1)
ax.set_ylim(lat_min - 0.1, lat_max + 0.1)

# 4. Add Labels for the towns and lakes
ax.scatter(37.55, 6.03, color='red', s=50, zorder=5, edgecolor='white')
ax.text(37.55, 6.05, "Arba Minch", fontsize=12, fontweight='bold', ha='center', va='bottom',
        path_effects=[pe.withStroke(linewidth=3, foreground="white")])

ax.scatter(37.55, 5.83, color='blue', s=50, zorder=5, edgecolor='white')
ax.text(37.55, 5.85, "Lake Chamo", fontsize=12, fontweight='bold', ha='center', va='bottom', color='darkblue',
        path_effects=[pe.withStroke(linewidth=3, foreground="white")])

ax.scatter(37.80, 6.30, color='blue', s=50, zorder=5, edgecolor='white')
ax.text(37.80, 6.32, "Lake Abaya", fontsize=12, fontweight='bold', ha='center', va='bottom', color='darkblue',
        path_effects=[pe.withStroke(linewidth=3, foreground="white")])

# 5. Formatting
ax.set_title("Study Area: Gamo Gofa Zone, Ethiopia", fontsize=18, fontweight='bold', pad=15)
ax.set_xlabel("Longitude", fontsize=12, fontweight='bold')
ax.set_ylabel("Latitude", fontsize=12, fontweight='bold')
ax.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)
ax.set_aspect("equal")

# Neatline
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

# 6. Create the Inset Map (Ethiopia Context)
print("--- Building Inset Map ---")
axins = inset_axes(ax, width="25%", height="25%", loc='upper left', borderpad=1)
ethiopia.plot(ax=axins, color='#d9e8f5', edgecolor='black', linewidth=0.8)

# Draw the same red box in the inset
rect_inset = Rectangle((lon_min, lat_min), lon_max - lon_min, lat_max - lat_min, 
                       fill=False, edgecolor='red', linewidth=2)
axins.add_patch(rect_inset)

axins.set_xticks([])
axins.set_yticks([])
axins.set_title("Ethiopia Context", fontsize=10, fontweight='bold')
axins.set_aspect("equal")

print("--- Saving Map ---")
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("[SUCCESS] Detailed Figure 1 saved to:", OUT_PNG)
