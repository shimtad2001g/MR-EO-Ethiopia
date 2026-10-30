import os, sys
import numpy as np
import rasterio
from rasterio.windows import Window
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from matplotlib.colors import ListedColormap
from matplotlib_scalebar.scalebar import ScaleBar
from sklearn.cluster import KMeans
import pyproj
import geopandas as gpd
import matplotlib.patheffects as pe
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

ENV = r"C:\Users\SHIMELES_TADESSE\.conda\envs\geospatial_auditor"
os.environ["GDAL_DATA"] = os.path.join(ENV, r"Library\share\gdal")
os.environ["PROJ_LIB"] = os.path.join(ENV, r"Library\share\proj")
os.environ["PROJ_DATA"] = os.environ["PROJ_LIB"]

RASTER_PATH = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
OUT_PNG = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Final_Professional_Map.png"
N_CLUSTERS = 5
RANDOM_SEED = 42
N_SAMPLE = 200000
CHUNK_ROWS = 512

print("--- Step 1: Loading Data ---")
with rasterio.open(RASTER_PATH) as src:
    raster_crs = src.crs
    H, W = src.height, src.width
    b = src.bounds
    extent = [b.left, b.right, b.bottom, b.top]

print("--- Step 2: Running K-Means Classification ---")
rng = np.random.default_rng(RANDOM_SEED)
frac = N_SAMPLE / float(H * W)
samples = []

with rasterio.open(RASTER_PATH) as src:
    for row0 in range(0, H, CHUNK_ROWS):
        h = min(CHUNK_ROWS, H - row0)
        block = src.read(window=Window(0, row0, W, h)).astype("float32")
        blk = block.reshape(block.shape[0], -1).T
        ok = np.isfinite(blk).all(axis=1) & ~(blk == 0).all(axis=1)
        idx_ok = np.where(ok)[0]
        if len(idx_ok) == 0: continue
        n = max(1, int(np.ceil(frac * h * W)))
        samples.append(blk[rng.choice(idx_ok, min(n, len(idx_ok)), replace=False)])

Xfit = np.concatenate(samples, axis=0)
mu, sd = Xfit.mean(0), Xfit.std(0) + 1e-9
km = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_SEED, n_init=10)
raw_fit = km.fit_predict((Xfit - mu) / sd)
order = np.argsort([Xfit[raw_fit == k, 0].mean() for k in range(N_CLUSTERS)])
lut = np.zeros(N_CLUSTERS, dtype="float32")
for new, old in enumerate(order): lut[old] = new

class_img = np.full((H, W), np.nan, dtype="float32")
with rasterio.open(RASTER_PATH) as src:
    for row0 in range(0, H, CHUNK_ROWS):
        h = min(CHUNK_ROWS, H - row0)
        block = src.read(window=Window(0, row0, W, h)).astype("float32")
        blk = block.reshape(block.shape[0], -1).T
        ok = np.isfinite(blk).all(axis=1) & ~(blk == 0).all(axis=1)
        out = np.full(blk.shape[0], np.nan, dtype="float32")
        if ok.any():
            pred = km.predict((blk[ok] - mu) / sd)
            out[ok] = lut[pred]
        class_img[row0:row0 + h, :] = out.reshape(h, W)

print("--- Step 3: Building Standard Cartography ---")
fig = plt.figure(figsize=(15, 10))
ax = fig.add_axes([0.05, 0.08, 0.65, 0.84]) 

colors = ['#b15928', '#33a02c', '#1f78b4', '#006400', '#ffff99']
cmap = ListedColormap(colors)
im = ax.imshow(class_img, extent=extent, cmap=cmap, interpolation="nearest")
ax.set_aspect("equal")

for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

transformer = pyproj.Transformer.from_crs(raster_crs, "EPSG:4326", always_xy=True)
transformer_inv = pyproj.Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)

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

ax.set_title("Gamo Gofa - Land Classification (Spectral Indices)", fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel("Longitude", fontsize=12, fontweight='bold')
ax.set_ylabel("Latitude", fontsize=12, fontweight='bold')

# Legend
names = [
    "Bare Soil / Built-up (NDBI)", 
    "Cropland / Sparse Veg (SAVI)", 
    "Water (NDWI)", 
    "Dense Forest (EVI)", 
    "Bright Soil / Water (Abaya)"
]
handles = [Patch(facecolor=cmap(i), label=names[i]) for i in range(N_CLUSTERS)]
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 0.95), 
          title="Land Cover Classes", framealpha=1.0, fontsize=11, title_fontsize=12)

# Colorbar
cax = fig.add_axes([0.85, 0.3, 0.02, 0.4])
cbar = fig.colorbar(im, cax=cax)
cbar.set_label("Class Index", fontsize=12, fontweight='bold')

# Scalebar (Bottom Left, completely unobstructed now)
ax.add_artist(ScaleBar(1.0, units="m", location="lower left", length_fraction=0.15, 
                       font_properties={'size': 10, 'weight': 'bold'}, pad=0.5))

# North Arrow
ax.annotate("N", xy=(0.95, 0.15), xytext=(0.95, 0.05), xycoords="axes fraction",
            ha="center", va="center", fontsize=16, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color="black", lw=3))

# Metadata Box (Moved higher up, below the inset map)
metadata_text = (
    "CRS: UTM Zone 37N (EPSG:32637)\n"
    "Grid: WGS 84 (EPSG:4326)\n"
    "Source: Sentinel-2 (Copernicus)\n"
    "Method: K-Means Unsupervised Classification\n"
    "Indices: NDWI, NDBI, SAVI, NDVI, EVI"
)
ax.text(0.02, 0.60, metadata_text, fontsize=9, family='monospace',
        va='top', ha='left', transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor="black", alpha=1.0))

# Inset Map
print("Loading Ethiopia boundary...")
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
except Exception as e:
    print("Could not load inset map:", e)

print("--- Saving Map ---")
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("[SUCCESS] Professional Map saved to:", OUT_PNG)
