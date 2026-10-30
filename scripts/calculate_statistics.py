import os, sys
import numpy as np
import rasterio
from rasterio.windows import Window
from sklearn.cluster import KMeans
import pandas as pd

ENV = r"C:\Users\SHIMELES_TADESSE\.conda\envs\geospatial_auditor"
os.environ["GDAL_DATA"] = os.path.join(ENV, r"Library\share\gdal")
os.environ["PROJ_LIB"] = os.path.join(ENV, r"Library\share\proj")
os.environ["PROJ_DATA"] = os.environ["PROJ_LIB"]

RASTER_PATH = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\raw\gamo_gofa_sentinel_2\gamo_gofa_sample_s2.tif"
CARBON_PATH = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_map.tif"
OUT_CSV = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Statistics.csv"

N_CLUSTERS = 5
RANDOM_SEED = 42
N_SAMPLE = 200000
CHUNK_ROWS = 512

print("--- Step 1: Re-running K-Means to get Class Array ---")
with rasterio.open(RASTER_PATH) as src:
    H, W = src.height, src.width
    transform = src.transform
    # Calculate pixel area (assuming square pixels)
    pixel_area_m2 = abs(transform[0] * transform[4])
    pixel_area_ha = pixel_area_m2 / 10000.0

# Fit K-Means
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

# Stream predict and count pixels
class_counts = np.zeros(N_CLUSTERS, dtype=np.int64)
valid_pixels = 0

with rasterio.open(RASTER_PATH) as src:
    for row0 in range(0, H, CHUNK_ROWS):
        h = min(CHUNK_ROWS, H - row0)
        block = src.read(window=Window(0, row0, W, h)).astype("float32")
        blk = block.reshape(block.shape[0], -1).T
        ok = np.isfinite(blk).all(axis=1) & ~(blk == 0).all(axis=1)
        if ok.any():
            pred = km.predict((blk[ok] - mu) / sd)
            mapped_pred = lut[pred]
            counts = np.bincount(mapped_pred, minlength=N_CLUSTERS)
            class_counts += counts
            valid_pixels += np.sum(ok)

print("--- Step 2: Calculating Class Areas ---")
class_names = [
    "Bare Soil / Built-up (NDBI)", 
    "Cropland / Sparse Veg (SAVI)", 
    "Water (NDWI)", 
    "Dense Forest (EVI)", 
    "Bright Soil / Water (Abaya)"
]

total_area_ha = valid_pixels * pixel_area_ha
stats_list = []

for i in range(N_CLUSTERS):
    area_ha = class_counts[i] * pixel_area_ha
    percent = (area_ha / total_area_ha) * 100
    stats_list.append({
        "Class Index": i,
        "Land Cover Class": class_names[i],
        "Pixel Count": class_counts[i],
        "Area (Hectares)": round(area_ha, 2),
        "Area (km2)": round(area_ha / 100, 2),
        "Percentage (%)": round(percent, 2)
    })

print("--- Step 3: Calculating Total Carbon Stock ---")
with rasterio.open(CARBON_PATH) as src_carb:
    carbon_data = src_carb.read(1).astype("float32")
    carb_transform = src_carb.transform
    carb_pixel_area_m2 = abs(carb_transform[0] * carb_transform[4])
    
    # Mask out invalid carbon values
    carbon_data = np.where((carbon_data <= 0) | (carbon_data > 1000), np.nan, carbon_data)
    
    # Calculate total carbon: (Sum of tons/ha) * (pixel area in ha)
    carbon_pixel_area_ha = carb_pixel_area_m2 / 10000.0
    total_carbon_tons = np.nansum(carbon_data) * carbon_pixel_area_ha
    
    mean_carbon = np.nanmean(carbon_data)

print(f"\nTotal Analyzed Area: {total_area_ha:,.2f} Hectares ({total_area_ha/100:,.2f} km²)")
print(f"Total Carbon Stock: {total_carbon_tons:,.2f} Metric Tons")
print(f"Mean Carbon Density: {mean_carbon:,.2f} tons/ha\n")

# Add Carbon stats to the table
stats_list.append({
    "Class Index": "N/A",
    "Land Cover Class": "TOTAL CARBON STOCK",
    "Pixel Count": "N/A",
    "Area (Hectares)": "N/A",
    "Area (km2)": "N/A",
    "Percentage (%)": "N/A"
})
stats_list.append({
    "Class Index": "N/A",
    "Land Cover Class": "Total Biomass (Tons)",
    "Pixel Count": f"{total_carbon_tons:,.2f}",
    "Area (Hectares)": "N/A",
    "Area (km2)": "N/A",
    "Percentage (%)": "N/A"
})

print("--- Step 4: Exporting to CSV ---")
df = pd.DataFrame(stats_list)
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
df.to_csv(OUT_CSV, index=False)

print(df.to_string(index=False))
print(f"\n[SUCCESS] Statistics saved to: {OUT_CSV}")
