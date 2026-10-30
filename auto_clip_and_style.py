import os
from osgeo import gdal
from qgis.core import (
    QgsApplication, QgsProject, QgsRasterLayer,
    QgsSingleBandPseudoColorRenderer, QgsRasterShader,
    QgsColorRampShader, QgsStyle, QgsRasterBandStats
)

qgs = QgsApplication([], False)
qgs.initQgis()

print("--- Step 1: Clipping Raster using GDAL ---")
input_raster = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_map_12band.tif"
mask_vector = r"D:\GamoGofa_Carbon_Assessment\03_Processing\AOI\EarthEngine_Upload\GamoGofa_AOI_WGS84.shp"
output_raster = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"

ds = gdal.Warp(output_raster, input_raster, cutlineDSName=mask_vector, cropToCutline=True, dstNodata=-9999)
if ds:
    ds = None
    print(f"Clipping complete. Saved to: {output_raster}")
else:
    print("[ERROR] GDAL Warp failed.")
    qgs.exitQgis()
    exit()

print("\n--- Step 2: Styling the Map ---")
project_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Viewer.qgs"

layer = QgsRasterLayer(output_raster, "Gamo-Gofa Carbon 12-Band", "gdal")
if not layer.isValid():
    print("[ERROR] The clipped layer failed to load in QGIS!")
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

print(f"[SUCCESS] Project saved to: {project_path}")
qgs.exitQgis()
