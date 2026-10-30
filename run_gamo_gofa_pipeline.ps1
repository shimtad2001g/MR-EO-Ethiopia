# ============================================================================
# MASTER AUTOMATION SCRIPT: Gamo-Gofa Carbon Pipeline
# ============================================================================

Write-Host "===================================================" -ForegroundColor Magenta
Write-Host " STARTING END-TO-END GAMO-GOFA AUTOMATION PIPELINE " -ForegroundColor Magenta
Write-Host "===================================================" -ForegroundColor Magenta

# 1. Define Paths
$venvPython = "C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\venv\Scripts\python.exe"
$qgisProcess = "C:\Program Files\QGIS 3.32.0\apps\qgis\bin\qgis_process.exe"
$baseDir = "C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia"

# 2. Execute Deep Learning Pipeline
Write-Host "
[1/3] Training Carbon Regression Model..." -ForegroundColor Cyan
& $venvPython "train_carbon_regression.py"

Write-Host "
[2/3] Running Carbon Inference..." -ForegroundColor Cyan
& $venvPython "inference_carbon.py"

Write-Host "
[3/3] Stitching Carbon GeoTIFF Map..." -ForegroundColor Cyan
& $venvPython "stitch_carbon_map.py"

# 3. Execute QGIS Headless Geoprocessing (Single Line Formatting)
Write-Host "
[QGIS] Clipping Map to Gamo-Gofa AOI..." -ForegroundColor Yellow

$inputRaster = "$baseDir\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_map.tif"
$maskVector = "D:\GamoGofa_Carbon_Assessment\03_Processing\AOI\EarthEngine_Upload\GamoGofa_AOI_WGS84.shp"
$outputRaster = "$baseDir\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_map_FINAL.tif"

& $qgisProcess run gdal:cliprasterbymasklayer -- INPUT="$inputRaster" MASK="$maskVector" SOURCE_CRS="EPSG:4326" TARGET_CRS="EPSG:4326" NODATA=-9999 OUTPUT="$outputRaster"

Write-Host "
===================================================" -ForegroundColor Green
Write-Host " PIPELINE COMPLETE! " -ForegroundColor Green
Write-Host " Final Map Saved To: $outputRaster" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
