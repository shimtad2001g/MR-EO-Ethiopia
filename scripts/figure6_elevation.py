import ee
import geemap
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.warp import transform_bounds

print("Downloading Elevation Data from GEE...")
ee.Initialize()

# We use the same AOI as our main project
wgs84_bounds = [38.70, 8.90, 38.85, 9.05]
roi = ee.Geometry.Rectangle(wgs84_bounds)

# Fetch SRTM DEM
dem = ee.Image('USGS/SRTMGL1_003').clip(roi)

out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\srtm_dem.tif"
geemap.ee_export_image(dem, filename=out_path, scale=30, region=roi, crs='EPSG:4326')

print("Generating 3D Elevation Figure...")
with rasterio.open(out_path) as src:
    elevation = src.read(1)
    # Downsample slightly so it renders fast on a CPU
    elevation = elevation[::5, ::5] 
    x = np.arange(0, elevation.shape[1])
    y = np.arange(0, elevation.shape[0])
    X, Y = np.meshgrid(x, y)

fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(X, Y, elevation, cmap='terrain', linewidth=0, antialiased=True)
fig.colorbar(surf, shrink=0.5, aspect=5, label='Elevation (meters)')

ax.set_title('Figure 6: 3D Topographic Model of Addis Ababa', fontsize=16, fontweight='bold')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('Elevation (m)')

plt.tight_layout()
out_path_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_6_3D_Elevation.png"
plt.savefig(out_path_img, dpi=300)
print(f"✅ Figure 6 saved to: {out_path_img}")