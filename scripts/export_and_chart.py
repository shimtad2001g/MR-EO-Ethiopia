import os, sys
import numpy as np
import rasterio
from rasterio.windows import Window
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

ENV = r"C:\Users\SHIMELES_TADESSE\.conda\envs\geospatial_auditor"
os.environ["GDAL_DATA"] = os.path.join(ENV, r"Library\share\gdal")
os.environ["PROJ_LIB"] = os.path.join(ENV, r"Library\share\proj")
os.environ["PROJ_DATA"] = os.environ["PROJ_LIB"]

RASTER_PATH = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
OUT_TIF = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Classified_Map.tif"
OUT_CHART = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Area_Chart.png"

N_CLUSTERS = 5
RANDOM_SEED = 42
N_SAMPLE = 200000
CHUNK_ROWS = 512

print("--- Step 1: Running K-Means & Exporting GeoTIFF ---")
with rasterio.open(RASTER_PATH) as src:
    H, W = src.height, src.width
    transform = src.transform
    crs = src.crs

# Fit K-Means (Same exact logic as before)
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
lut = np.zeros(N_CLUSTERS, dtype="int32")
for new, old in enumerate(order): lut[old] = new

# Create a new GeoTIFF to save the classes
with rasterio.open(
    OUT_TIF, 'w',
    driver='GTiff',
    height=H,
    width=W,
    count=1,
    dtype='int32',
    crs=crs,
    transform=transform,
    nodata=-1
) as dst:
    # Stream predict and write directly to the file
    with rasterio.open(RASTER_PATH) as src:
        for row0 in range(0, H, CHUNK_ROWS):
            h = min(CHUNK_ROWS, H - row0)
            block = src.read(window=Window(0, row0, W, h)).astype("float32")
            blk = block.reshape(block.shape[0], -1).T
            
            # Default to -1 (NoData) for background/empty pixels
            out = np.full(blk.shape[0], -1, dtype="int32")
            
            ok = np.isfinite(blk).all(axis=1) & ~(blk == 0).all(axis=1)
            if ok.any():
                pred = km.predict((blk[ok] - mu) / sd)
                out[ok] = lut[pred]
                
            out_2d = out.reshape(h, W)
            dst.write(out_2d, 1, window=Window(0, row0, W, h))

print(f"[SUCCESS] GeoTIFF saved to: {OUT_TIF}")

print("--- Step 2: Generating Statistical Bar Chart ---")
# Data from our previous calculation
classes = [
    "Bare Soil /\nBuilt-up", 
    "Cropland /\nSparse Veg", 
    "Water", 
    "Dense Forest", 
    "Bright Soil /\nWater (Abaya)"
]
percentages = [10.65, 40.79, 10.84, 24.67, 13.06]
colors = ['#b15928', '#33a02c', '#1f78b4', '#006400', '#ffff99']

fig, ax = plt.subplots(figsize=(10, 6))

# Create the bar chart
bars = ax.bar(classes, percentages, color=colors, edgecolor='black', linewidth=1.2)

# Add titles and labels
ax.set_title("Gamo Gofa Land Cover Distribution (Percentage of Total Area)", fontsize=16, fontweight='bold', pad=20)
ax.set_ylabel("Percentage of Total Area (%)", fontsize=14, fontweight='bold')
ax.set_xlabel("Land Cover Class", fontsize=14, fontweight='bold')
ax.set_ylim(0, 50) # Set y-axis limit a bit above the highest bar

# Add the exact numbers on top of the bars
for bar, pct in zip(bars, percentages):
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{pct}%", ha='center', va='bottom', fontsize=12, fontweight='bold')

# Add grid lines for readability
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

# Save the chart
os.makedirs(os.path.dirname(OUT_CHART), exist_ok=True)
fig.savefig(OUT_CHART, dpi=300, bbox_inches="tight")
print(f"[SUCCESS] Bar Chart saved to: {OUT_CHART}")
