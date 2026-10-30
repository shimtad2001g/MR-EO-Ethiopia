import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import os

print("Generating Publication-Ready Figure 4: Spatial Distribution...")

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    crs = src.crs
    
    # Apply Contrast Stretch for visibility
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

# Recreate the exact 100 random coordinates used in validation
np.random.seed(42)
patch_size = 224
coords = []
for _ in range(100):
    y = np.random.randint(0, img.shape[0] - patch_size)
    x = np.random.randint(0, img.shape[1] - patch_size)
    coords.append((x + patch_size//2, y + patch_size//2))
coords = np.array(coords)

# Convert pixel coordinates to geographic coordinates (Longitude/Latitude)
# X_map = bounds.left + (x_pixel / width) * (bounds.right - bounds.left)
# Y_map = bounds.top - (y_pixel / height) * (bounds.top - bounds.bottom)
x_geo = bounds.left + (coords[:, 0] / img.shape[1]) * (bounds.right - bounds.left)
y_geo = bounds.top - (coords[:, 1] / img.shape[0]) * (bounds.top - bounds.bottom)

fig, ax = plt.subplots(figsize=(12, 10))
ax.imshow(img_rgb, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

# Plot the validation patches (Gold/Red points with white edges)
scatter = ax.scatter(x_geo, y_geo, c='#FF4500', s=70, marker='o', 
                     edgecolors='white', linewidths=1.5, label='Validation Patch (100)', alpha=0.9, zorder=5)

# Labels and Title
ax.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')
plt.title("Figure 4: Spatial Distribution of Validation Patches\n(Addis Ababa, Ethiopia)", 
          fontsize=18, fontweight='bold', pad=20)

# --- CUSTOM SCALE BAR (1 km) ---
deg_per_km = 1.0 / 111.32 
x_start = bounds.right - (bounds.right - bounds.left) * 0.1
y_pos = bounds.bottom + (bounds.top - bounds.bottom) * 0.05
x_end = x_start - deg_per_km
ax.plot([x_end, x_start], [y_pos, y_pos], color='black', linewidth=6, solid_capstyle='butt', zorder=10)
ax.plot([x_end, x_end + (deg_per_km/2)], [y_pos, y_pos], color='white', linewidth=6, solid_capstyle='butt', zorder=10)
ax.text(x_start - (deg_per_km/2), y_pos + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', 
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=2), zorder=10)

# North Arrow
x, y, arrow_length = 0.95, 0.95, 0.08
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=18, fontweight='bold', 
            xycoords=ax.transAxes, zorder=10)

# Legend
ax.legend(loc='lower left', fontsize=12, framealpha=0.9, edgecolor='black', 
          facecolor='white', title="AI Validation Data", title_fontsize=12)

ax.grid(color='white', linestyle='--', linewidth=1, alpha=0.3)
ax.add_patch(Rectangle((bounds.left, bounds.bottom), 
                       bounds.right - bounds.left, 
                       bounds.top - bounds.bottom, 
                       fill=False, edgecolor='black', linewidth=2))

plt.tight_layout()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_4_Publication_Patches.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Figure 4 successfully saved to: {out_path}")