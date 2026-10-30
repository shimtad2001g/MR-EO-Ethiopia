# ============================================================================
# ULTIMATE ONE-CLICK GAMO-GOFA PIPELINE
# Orchestrates AWS Download, PyTorch Training, Geospatial Stitching, and 
# 600 DPI Cartographic Rendering.
# ============================================================================

# Stop execution if any step fails
$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Magenta
Write-Host " STARTING ULTIMATE ONE-CLICK CARBON PIPELINE " -ForegroundColor Magenta
Write-Host "===================================================" -ForegroundColor Magenta

# Ensure required Python packages are installed
Write-Host "
[0/7] Checking Dependencies..." -ForegroundColor Yellow
pip install rasterio numpy pandas geopandas matplotlib contextily pyproj pystac-client planetary-computer rioxarray torch torchvision --quiet

# 1. Data Acquisition
Write-Host "
[1/7] Downloading 12-Band Sentinel-2 Data from AWS..." -ForegroundColor Cyan
python download_s2_data.py
if ($LASTEXITCODE -ne 0) { throw "Data download failed." }

# 2. Data Engineering
Write-Host "
[2/7] Preprocessing and Tiling Imagery..." -ForegroundColor Cyan
python preprocess_gamo_gofa.py
if ($LASTEXITCODE -ne 0) { throw "Preprocessing failed." }

# 3. Label Generation
Write-Host "
[3/7] Generating Proxy Labels..." -ForegroundColor Cyan
python generate_ndvi_carbon.py
if ($LASTEXITCODE -ne 0) { throw "Label generation failed." }

# 4. Deep Learning Training (Model Surgery + 10 Epochs)
Write-Host "
[4/7] Training 12-Band ResNet18 Model..." -ForegroundColor Cyan
python train_12band_carbon.py
if ($LASTEXITCODE -ne 0) { throw "Model training failed." }

# 5. Inference and GeoTIFF Stitching
Write-Host "
[5/7] Running Inference on 840 Patches..." -ForegroundColor Cyan
python inference_12band.py
if ($LASTEXITCODE -ne 0) { throw "Inference failed." }

Write-Host "
[6/7] Stitching Predictions into GeoTIFF..." -ForegroundColor Cyan
python stitch_carbon_12band.py
if ($LASTEXITCODE -ne 0) { throw "Stitching failed." }

# 6. High-Standard Cartography Rendering
Write-Host "
[7/7] Rendering 600 DPI Cartographic Masterpiece..." -ForegroundColor Cyan
python create_perfect_map.py
if ($LASTEXITCODE -ne 0) { throw "Cartography rendering failed." }

# 7. Open the Final Map
$finalMap = "C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Perfect_Map.png"
if (Test-Path $finalMap) {
    Write-Host "
===================================================" -ForegroundColor Green
    Write-Host " PIPELINE COMPLETE! OPENING FINAL MAP... " -ForegroundColor Green
    Write-Host "===================================================" -ForegroundColor Green
    Start-Process $finalMap
} else {
    Write-Host "
[ERROR] Pipeline finished, but final map was not found." -ForegroundColor Red
}
