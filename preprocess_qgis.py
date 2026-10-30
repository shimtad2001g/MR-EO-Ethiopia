# preprocess_qgis.py
from qgis.core import QgsApplication, QgsRasterLayer
import processing

# Initialize QGIS (headless)
qgs = QgsApplication([], False)
qgs.initQgis()

# Run QGIS's native "gdal:tile" or "gdal:translate" algorithm
# Example: Tile the Sentinel-2 image into 256x256 patches
processing.run("gdal:translate", {
    'INPUT': 'C:/Users/SHIMELES_TADESSE/MR-EO-Ethiopia/data/raw/gamo_gofa_sentinel_2/gamo_gofa_sample_s2.tif',
    'OUTPUT': 'C:/Users/SHIMELES_TADESSE/MR-EO-Ethiopia/data/processed/gamo_gofa_patches_256x256/patches.tif'
})

qgs.exitQgis()
