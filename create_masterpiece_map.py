import os
import numpy as np
import rasterio

# THE CRITICAL FIX: Tell Qt where the Windows fonts are BEFORE importing QGIS
os.environ['QT_QPA_FONTDIR'] = 'C:/Windows/Fonts'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from qgis.core import (
    QgsApplication, QgsProject, QgsRasterLayer, QgsVectorLayer,
    QgsPrintLayout, QgsLayoutItemMap, QgsLayoutItemLegend,
    QgsLayoutItemScaleBar, QgsLayoutItemPicture, QgsLayoutItemLabel,
    QgsLayoutExporter, QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes,
    QgsSingleBandPseudoColorRenderer, QgsRasterShader, 
    QgsColorRampShader, QgsStyle, QgsLayoutItemMapOverview,
    QgsLayoutMeasurement, QgsFillSymbol, QgsLayoutItemMapGrid,
    QgsCoordinateReferenceSystem, QgsSingleSymbolRenderer, QgsRectangle
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import QRectF

# Initialize QGIS
qgs = QgsApplication([], False)
qgs.initQgis()

print("--- Step 1: Masking NoData Values ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
temp_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\temp_layout_map.tif"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Masterpiece_PRO.png"

with rasterio.open(input_tif) as src:
    data = src.read(1)
    profile = src.profile

data = data.astype(np.float32)
data[(data == -9999) | (data <= 1.0)] = np.nan
profile.update(dtype=rasterio.float32, nodata=np.nan)

with rasterio.open(temp_tif, 'w', **profile) as dst:
    dst.write(data, 1)

print("--- Step 2: Initializing QGIS Project ---")
project = QgsProject.instance()

# Load Main Raster
raster_layer = QgsRasterLayer(temp_tif, "Carbon Biomass", "gdal")
project.addMapLayer(raster_layer)

# Apply Symbology
provider = raster_layer.dataProvider()
style = QgsStyle.defaultStyle()
ramp = style.colorRamp('RdYlGn')
shader = QgsColorRampShader(1.0, 30.0, ramp, QgsColorRampShader.Interpolated)
shader.classifyColorRamp()
raster_shader = QgsRasterShader()
raster_shader.setRasterShaderFunction(shader)
renderer = QgsSingleBandPseudoColorRenderer(provider, 1, raster_shader)
renderer.setClassificationMin(1.0)
renderer.setClassificationMax(30.0)
raster_layer.setRenderer(renderer)

# Load Inset Layer (Ethiopia Boundary)
aoi_path = r"D:\GamoGofa_Carbon_Assessment\02_Data\01_Boundaries\Processed\Ethiopia_ADM2_Zone_Boundary.gpkg"
inset_layer = QgsVectorLayer(aoi_path, "Ethiopia Zones", "ogr")

# Style the Inset Map (Light Gray Fill, Dark Gray Outline)
inset_symbol = QgsFillSymbol.createSimple({'color': '220,220,220', 'outline_color': '100,100,100', 'outline_width': '0.2'})
inset_layer.setRenderer(QgsSingleSymbolRenderer(inset_symbol))
project.addMapLayer(inset_layer)

print("--- Step 3: Building Cartographic Layout ---")
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName("Carbon Map Layout")

# Page Settings (A4 Landscape)
layout.pageCollection().page(0).setPageSize(QgsLayoutSize(297, 210, QgsUnitTypes.LayoutMillimeters))

# 1. Title
title = QgsLayoutItemLabel(layout)
title.setText("Gamo-Gofa 12-Band Carbon Biomass Prediction")
title.setFont(QFont("Arial", 18))
title.setRect(QRectF(0, 8, 297, 15))
title.setHAlign(1) # Center align
layout.addLayoutItem(title)

# 2. Main Map
map_item = QgsLayoutItemMap(layout)
map_item.setRect(QRectF(15, 25, 267, 160))
map_item.setLayers([raster_layer])
map_item.zoomToExtent(raster_layer.extent())
map_item.setFrameEnabled(True) # Neatline
map_item.setFrameStrokeColor(QColor(0, 0, 0))
map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.4)) 
layout.addLayoutItem(map_item)

# 3. Grid (Graticule / Lat-Long)
grid = map_item.grid()
grid.setEnabled(True)
grid.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
grid.setIntervalX(0.05)
grid.setIntervalY(0.05)
grid.setStyle(QgsLayoutItemMapGrid.Cross)
grid.setAnnotationEnabled(True)
grid.setAnnotationFormat(QgsLayoutItemMapGrid.DecimalWithSuffix)
grid.setAnnotationPrecision(2)
grid.setAnnotationFont(QFont("Arial", 8))
grid.setFrameStyle(QgsLayoutItemMapGrid.Zebra) 
grid.setFrameWidth(0.5)

# 4. Legend
legend = QgsLayoutItemLegend(layout)
legend.setTitle("Carbon (tons/ha)")
legend.setLinkedMap(map_item)
legend.setRect(QRectF(245, 100, 35, 70))
legend.setBackgroundColor(QColor(255, 255, 255, 220))
legend.setFrameEnabled(True)
legend.setFrameStrokeColor(QColor(0, 0, 0))
legend.setFrameStrokeWidth(QgsLayoutMeasurement(0.2))
layout.addLayoutItem(legend)

# 5. Scale Bar
scalebar = QgsLayoutItemScaleBar(layout)
scalebar.setStyle('Line Ticks Up')
scalebar.setLinkedMap(map_item)
scalebar.applyDefaultSize()
scalebar.setRect(QRectF(20, 170, 50, 10))
scalebar.setUnitLabel("km")
scalebar.setFont(QFont("Arial", 8))
layout.addLayoutItem(scalebar)

# 6. North Arrow
north = QgsLayoutItemPicture(layout)
north.setPicturePath(r"C:\PROGRA~1\QGIS33~1.0\apps\qgis\svg\arrows\NorthArrow_02.svg")
north.setRect(QRectF(25, 35, 12, 12))
layout.addLayoutItem(north)

# 7. Projection Info
proj_label = QgsLayoutItemLabel(layout)
proj_label.setText("Projection: EPSG:4326 - WGS 84\nData Source: Sentinel-2 L2A (AWS Earth Search)\nModel: 12-Band ResNet18 (RMSE: 2.20 t/ha)")
proj_label.setFont(QFont("Arial", 8))
proj_label.setRect(QRectF(15, 185, 100, 15))
layout.addLayoutItem(proj_label)

# 8. Inset Map (Ethiopia Context) - FIXED ZOOM EXTENT
inset_map = QgsLayoutItemMap(layout)
inset_map.setRect(QRectF(235, 35, 45, 45))
inset_map.setLayers([inset_layer])
# Set Ethiopia's exact bounding box: X: 32.9 to 47.9, Y: 3.4 to 14.8
ethiopia_extent = QgsRectangle(32.9, 3.4, 47.9, 14.8)
inset_map.zoomToExtent(ethiopia_extent)
inset_map.setFrameEnabled(True)
inset_map.setBackgroundColor(QColor(255, 255, 255))
layout.addLayoutItem(inset_map)

# Add Overview Box (Red box showing Gamo-Gofa extent)
overview = QgsLayoutItemMapOverview("overview", inset_map)
overview.setLinkedMap(map_item)
overview_symbol = QgsFillSymbol.createSimple({'color': 'transparent', 'outline_color': 'red', 'outline_width': '0.6'})
overview.setFrameSymbol(overview_symbol)
inset_map.overviews().addOverview(overview)

print("--- Step 4: Exporting to PNG ---")
exporter = QgsLayoutExporter(layout)
settings = QgsLayoutExporter.ImageExportSettings()
settings.dpi = 300 # High resolution

exporter.exportToImage(output_png, settings)

print(f"[SUCCESS] Masterpiece map saved to: {output_png}")

qgs.exitQgis()

if os.path.exists(temp_tif):
    os.remove(temp_tif)
