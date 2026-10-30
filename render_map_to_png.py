import os
from osgeo import gdal
gdal.UseExceptions() # Suppress the FutureWarning
from qgis.core import (
    QgsApplication, QgsRasterLayer, QgsMapSettings, 
    QgsMapRendererParallelJob, QgsSingleBandPseudoColorRenderer, 
    QgsRasterShader, QgsColorRampShader, QgsStyle, QgsRasterBandStats
)
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor

# Initialize QGIS
qgs = QgsApplication([], False)
qgs.initQgis()

print("--- Loading Raster for Rendering ---")
raster_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Map.png"

layer = QgsRasterLayer(raster_path, "Gamo-Gofa Carbon 12-Band", "gdal")
if not layer.isValid():
    print("[ERROR] Layer failed to load!")
    qgs.exitQgis()
    exit()

# Apply Symbology
print("--- Applying RdYlGn Symbology ---")
provider = layer.dataProvider()
stats = provider.bandStatistics(1, QgsRasterBandStats.All)
min_val, max_val = stats.minimumValue, stats.maximumValue

style = QgsStyle.defaultStyle()
ramp = style.colorRamp('RdYlGn')
if not ramp:
    ramp = style.colorRamp('Greens')

color_ramp_shader = QgsColorRampShader(min_val, max_val, ramp, QgsColorRampShader.Interpolated)
color_ramp_shader.classifyColorRamp()

raster_shader = QgsRasterShader()
raster_shader.setRasterShaderFunction(color_ramp_shader)

renderer = QgsSingleBandPseudoColorRenderer(provider, 1, raster_shader)
renderer.setClassificationMin(min_val)
renderer.setClassificationMax(max_val)
layer.setRenderer(renderer)

# Setup Map Renderer
print("--- Rendering Map to PNG ---")
settings = QgsMapSettings()
settings.setLayers([layer])
settings.setBackgroundColor(QColor(255, 255, 255))
settings.setOutputSize(QSize(1920, 1080)) # Full HD resolution
settings.setExtent(layer.extent())

# Execute Render Job
render_job = QgsMapRendererParallelJob(settings)
render_job.start()
render_job.waitForFinished()

image = render_job.renderedImage()
image.save(output_png, "png")

print(f"[SUCCESS] Map successfully saved to: {output_png}")
qgs.exitQgis()
