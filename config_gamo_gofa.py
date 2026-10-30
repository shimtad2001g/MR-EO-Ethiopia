# File: config_gamo_gofa.py
import os
from pathlib import Path

# --- Base Directories ---
BASE_DIR = Path(r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia")

# --- Input Data Directories ---
RAW_S2_DIR = BASE_DIR / "data" / "raw" / "gamo_gofa_sentinel_2"
RAW_S1_DIR = BASE_DIR / "data" / "raw" / "gamo_gofa_sentinel_1"
RAW_DEM_DIR = BASE_DIR / "data" / "raw" / "gamo_gofa_dem"
PROCESSED_DIR = BASE_DIR / "data" / "processed" / "gamo_gofa_patches_256x256"

# --- Output Directories ---
OUT_CROP_MAPS = BASE_DIR / "outputs" / "gamo_gofa_crop_maps"
OUT_BIOMASS_MAPS = BASE_DIR / "outputs" / "gamo_gofa_biomass_maps"
OUT_FEED_RISK = BASE_DIR / "outputs" / "gamo_gofa_feed_risk"
OUT_CARBON_MAPS = BASE_DIR / "outputs" / "gamo_gofa_carbon_maps"

# --- Existing Assets (D: Drive) ---
D_DRIVE_CARBON = Path(r"D:\GamoGofa_Carbon_Assessment")
AOI_SHAPEFILE = D_DRIVE_CARBON / "03_Processing" / "AOI" / "EarthEngine_Upload" / "GamoGofa_AOI_WGS84.shp"

# --- Model Parameters ---
PATCH_SIZE = 256
BANDS_S2 = 13
BANDS_S1 = 2
BANDS_DEM = 1

# --- Base Weights ---
MASSIVE_WEIGHTS = BASE_DIR / "massive_ssl_weights.pth"
HAWASSA_WEIGHTS = BASE_DIR / "hawassa_ssl_weights.pth"
GAMO_GOFA_OUTPUT_WEIGHTS = BASE_DIR / "gamo_gofa_ssl_weights.pth"
