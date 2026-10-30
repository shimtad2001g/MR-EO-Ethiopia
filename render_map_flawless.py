import os
import numpy as np
import rasterio
from osgeo import gdal
gdal.UseExceptions()
from qgis.core import (
    QgsApplication, QgsRasterLayer, QgsMapSettings, 
    QgsMapRendererParallelJob, QgsSingleBandPseudoColorRenderer, 
    QgsRasterShader, QgsColorRampShader, QgsStyle, QgsRasterBandStats
)
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor

print("--- Step 1: Converting NoData (-9999) to NaN ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
temp_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\temp_nan_map.tif"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Map_Flawless.png"

# Read the original TIFF
with rasterio.open(input_tif) as src:
    data = src.read(1)
    profile = src.profile

# Convert -9999 to NaN
data = data.astype(np.float32)
data[data == -9999] = np.nan

# Save the temporary TIFF with NaN as NoData
profile.update(dtype=rasterio.float32, nodata=np.nan)
with rasterio.open(temp_tif, 'w', **profile) as dst:
    dst.write(data, 1)
print("Temporary NaN map created.")

print("--- Step 2: Initializing QGIS ---")
qgs = QgsApplication([], False)
qgs.initQgis()

layer = QgsRasterLayer(temp_tif, "Gamo-Gofa Carbon", "gdal")
if not layer.isValid():
    print("[ERROR] Layer failed to load!")
    qgs.exitQgis()
    exit()

print("--- Step 3: Applying RdYlGn Symbology ---")
provider = layer.dataProvider()
stats = provider.bandStatistics(1, QgsRasterBandStats.All)
min_val = 0.0 
max_val = stats.maximumValue

style = QgsStyle.defaultStyle()
ramp = style.colorRamp('RdYlGn')

color_ramp_shader = QgsColorRampShader(min_val, max_val, ramp, QgsColorRampShader.Interpolated)
color_ramp_shader.classifyColorRamp()

raster_shader = QgsRasterShader()
raster_shader.setRasterShaderFunction(color_ramp_shader)

renderer = QgsSingleBandPseudoColorRenderer(provider, 1, raster_shader)
renderer.setClassificationMin(min_val)
renderer.setClassificationMax(max_val)
layer.setRenderer(renderer)

print("--- Step 4: Rendering Map to PNG ---")
settings = QgsMapSettings()
settings.setLayers([layer])
settings.setBackgroundColor(QColor(255, 255, 255)) # White background
settings.setOutputSize(QSize(1920, 1080))
settings.setExtent(layer.extent())

render_job = QgsMapRendererParallelJob(settings)
render_job.start()
render_job.waitForFinished()

image = render_job.renderedImage()
image.save(output_png, "png")

print(f"[SUCCESS] Map successfully saved to: {output_png}")
qgs.exitQgis()

# Clean up the temporary file
if os.path.exists(temp_tif):
    os.remove(temp_tif)
    print("Temporary file cleaned up.")
