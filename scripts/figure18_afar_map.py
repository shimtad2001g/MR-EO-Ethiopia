import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

print("Generating Figure 18: Afar Study Area Map...")
img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\afar_image.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    crs = src.crs
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

fig, ax = plt.subplots(figsize=(12, 10))
ax.imshow(img_rgb, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

ax.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')
plt.title("Study Area: Afar Region (Arid Zone), Ethiopia\nSentinel-2 True Color Composite", fontsize=18, fontweight='bold', pad=20)

deg_per_km = 1.0 / 111.32 
x_start = bounds.right - (bounds.right - bounds.left) * 0.1
y_pos = bounds.bottom + (bounds.top - bounds.bottom) * 0.05
x_end = x_start - deg_per_km

ax.plot([x_end, x_start], [y_pos, y_pos], color='black', linewidth=6, zorder=10)
ax.plot([x_end, x_end + (deg_per_km/2)], [y_pos, y_pos], color='white', linewidth=6, zorder=10)
ax.text(x_start - (deg_per_km/2), y_pos + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'), zorder=10)

ax.annotate('N', xy=(0.95, 0.95), xytext=(0.95, 0.87), arrowprops=dict(facecolor='black', width=5, headwidth=15), ha='center', va='center', fontsize=18, fontweight='bold', xycoords=ax.transAxes, zorder=10)

ax.legend(handles=[Rectangle((0,0), 1, 1, facecolor='#FF0000', label='Band 4'), Rectangle((0,0), 1, 1, facecolor='#00FF00', label='Band 3'), Rectangle((0,0), 1, 1, facecolor='#0000FF', label='Band 2')], loc='upper left', title="Sentinel-2 Bands", framealpha=0.9)

ax.text(0.02, 0.98, f"Projection: {crs.to_string()}\nData Source: Sentinel-2 SR (GEE)\nAuthor: Shimeles T. Zelelew", transform=ax.transAxes, fontsize=11, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.9, edgecolor='black'), fontfamily='monospace', zorder=10)

ax.grid(color='white', linestyle='--', alpha=0.4)
ax.add_patch(Rectangle((bounds.left, bounds.bottom), bounds.right - bounds.left, bounds.top - bounds.bottom, fill=False, edgecolor='black', linewidth=2))

plt.tight_layout()
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_18_Afar_Map.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 18 saved to: {out_img}")