import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

print("--- Reading and Masking Data ---")
input_tif = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\gamo_gofa_carbon_12band_FINAL.tif"
output_png = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\GamoGofa_Carbon_Map_Matplotlib.png"

with rasterio.open(input_tif) as src:
    data = src.read(1)
    
# Mask NoData (-9999) values so they don't render
data = np.ma.masked_where(data == -9999, data)

print("--- Rendering with Matplotlib ---")
fig, ax = plt.subplots(figsize=(12, 8), dpi=200)

# Use the built-in RdYlGn colormap
cmap = plt.get_cmap('RdYlGn')
cmap.set_bad(color='white') # Set masked NoData to white

# Plot the data
im = ax.imshow(data, cmap=cmap, vmin=0, vmax=np.max(data))

# Clean up the axes
ax.axis('off')

# Add a colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Predicted Carbon (tons/ha)', rotation=270, labelpad=15)

# Add title
plt.title('Gamo-Gofa 12-Band Carbon Biomass Prediction', fontsize=16, pad=20)

# Save the figure
plt.savefig(output_png, bbox_inches='tight', pad_inches=0.1, transparent=False, facecolor='white')
plt.close()

print(f"[SUCCESS] Flawless map saved to: {output_png}")
