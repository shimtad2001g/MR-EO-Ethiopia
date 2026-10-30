import ee
import geemap
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

print("Generating Pre-print Standard Figure 12: Awash 3D Elevation...")

ee.Initialize()
# Upper Awash Basin AOI
wgs84_bounds = [39.75, 8.85, 39.90, 9.00]
roi = ee.Geometry.Rectangle(wgs84_bounds)

# Fetch SRTM DEM
dem = ee.Image('USGS/SRTMGL1_003').clip(roi)
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\srtm_awash.tif"

if not os.path.exists(out_path):
    print("Downloading DEM from GEE...")
    geemap.ee_export_image(dem, filename=out_path, scale=30, region=roi, crs='EPSG:4326')

with rasterio.open(out_path) as src:
    elevation = src.read(1)
    bounds = src.bounds
    
    # Downsample slightly for faster rendering
    elevation = elevation[::3, ::3] 
    lon = np.linspace(bounds.left, bounds.right, elevation.shape[1])
    lat = np.linspace(bounds.bottom, bounds.top, elevation.shape[0])
    X, Y = np.meshgrid(lon, lat)

fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

# Plot surface with terrain colormap
surf = ax.plot_surface(X, Y, elevation, cmap='terrain', linewidth=0, antialiased=True, alpha=0.9)

cbar = fig.colorbar(surf, shrink=0.6, aspect=15, pad=0.08)
cbar.set_label('Elevation (meters)', fontsize=14, fontweight='bold', labelpad=15)
cbar.ax.tick_params(labelsize=12)

ax.set_title('3D Topographic Elevation Model\n(Upper Awash Basin, Ethiopia)', fontsize=18, fontweight='bold', pad=20)
ax.set_xlabel('Longitude (°E)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('Latitude (°N)', fontsize=12, fontweight='bold', labelpad=10)
ax.set_zlabel('Elevation (m)', fontsize=12, fontweight='bold', labelpad=10)

# Adjust viewing angle for best perspective
ax.view_init(elev=50, azim=135)

# Clean background
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.set_facecolor('white')
ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

plt.tight_layout()
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_12_Awash_3D_Elevation.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ SUCCESS! Figure 12 saved to: {out_img}")