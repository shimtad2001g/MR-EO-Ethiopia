import os
from osgeo import gdal
gdal.UseExceptions()
from qgis.core import (
    QgsApplication, QgsRasterLayer, QgsMapSettings, 
    QgsMapRendererParallelJob, QgsSingleBandPseudoColorRenderer, 
    QgsRasterShader, QgsColorRampShader, QgsStyle, QgsRasterBandStats
)
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor

qgs = QgsApplication([], False)
qgs.initQgis()

print("--- Loading Raster for Rendering ---")
raster_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Map_Clean.png"

layer = QgsRasterLayer(raster_path, "Gamo-Gofa Carbon 12-Band", "gdal")
if not layer.isValid():
    print("[ERROR] Layer failed to load!")
    qgs.exitQgis()
    exit()

print("--- Applying RdYlGn Symbology (Fixing NoData) ---")
provider = layer.dataProvider()
# Explicitly tell the provider that -9999 is NoData
provider.setNoDataValue(1, -9999) 

stats = provider.bandStatistics(1, QgsRasterBandStats.All)
min_val = 0.0  # Start the color ramp at 0, not -9999
max_val = stats.maximumValue

style = QgsStyle.defaultStyle()
ramp = style.colorRamp('RdYlGn')
if not ramp:
    ramp = style.colorRamp('Greens')

color_ramp_shader = QgsColorRampShader(min_val, max_val, ramp, QgsColorRampShader.Interpolated)
color_ramp_shader.classifyColorRamp()

# THE FIX: Manually add a transparent color for the -9999 NoData value
transparent_color = QColor(0, 0, 0, 0) # R, G, B, Alpha (0 alpha = fully transparent)
nodata_item = QgsColorRampShader.ColorRampItem(-9999, transparent_color, "NoData")
items = color_ramp_shader.colorRampItemList()
items.insert(0, nodata_item)
color_ramp_shader.setColorRampItemList(items)

raster_shader = QgsRasterShader()
raster_shader.setRasterShaderFunction(color_ramp_shader)

renderer = QgsSingleBandPseudoColorRenderer(provider, 1, raster_shader)
renderer.setClassificationMin(min_val)
renderer.setClassificationMax(max_val)
layer.setRenderer(renderer)

print("--- Rendering Map to PNG ---")
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
