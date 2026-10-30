# File: auto_style_map.py
import os
from qgis.core import (
    QgsApplication, QgsProject, QgsRasterLayer,
    QgsSingleBandPseudoColorRenderer, QgsRasterShader,
    QgsColorRampShader, QgsStyle, QgsRasterBandStats
)

qgs = QgsApplication([], False)
qgs.initQgis()

raster_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
project_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Viewer.qgs"

layer = QgsRasterLayer(raster_path, "Gamo-Gofa Carbon 12-Band", "gdal")
if not layer.isValid():
    print("[ERROR] Layer failed to load!")
    qgs.exitQgis()
    exit()

provider = layer.dataProvider()
stats = provider.bandStatistics(1, QgsRasterBandStats.All)
min_val = stats.minimumValue
max_val = stats.maximumValue

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

project = QgsProject.instance()
project.addMapLayer(layer)
project.write(project_path)

print(f"[SUCCESS] Styled map and project saved to: {project_path}")
qgs.exitQgis()
