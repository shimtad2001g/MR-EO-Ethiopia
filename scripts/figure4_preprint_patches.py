import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Patch

print("Generating Pre-print Standard Figure 4: Spatial Distribution...")

# Load the harmonized image for Addis Ababa
img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    crs = src.crs
    
    # Apply Contrast Stretch for visibility
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

# Recreate the exact 100 random coordinates used in the model validation
np.random.seed(42)
patch_size = 224
coords = []
for _ in range(100):
    y = np.random.randint(0, img.shape[0] - patch_size)
    x = np.random.randint(0, img.shape[1] - patch_size)
    coords.append((x + patch_size//2, y + patch_size//2))
coords = np.array(coords)

# Convert pixel coordinates to geographic coordinates
x_geo = bounds.left + (coords[:, 0] / img.shape[1]) * (bounds.right - bounds.left)
y_geo = bounds.top - (coords[:, 1] / img.shape[0]) * (bounds.top - bounds.bottom)

fig, ax = plt.subplots(figsize=(12, 10))
ax.imshow(img_rgb, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

# Plot the validation patches
ax.scatter(x_geo, y_geo, c='#FF4500', s=60, marker='o', 
           edgecolors='white', linewidths=1.2, label='Validation Patch Center', alpha=0.9, zorder=5)

ax.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')
plt.title("Spatial Distribution of Validation Patches\n(Addis Ababa, Ethiopia)", 
          fontsize=18, fontweight='bold', pad=20)

# 1. Custom Scale Bar (1 km)
deg_per_km = 1.0 / 111.32 
x_start = bounds.right - (bounds.right - bounds.left) * 0.1
y_pos = bounds.bottom + (bounds.top - bounds.bottom) * 0.05
x_end = x_start - deg_per_km

ax.plot([x_end, x_start], [y_pos, y_pos], color='black', linewidth=6, solid_capstyle='butt', zorder=10)
ax.plot([x_end, x_end + (deg_per_km/2)], [y_pos, y_pos], color='white', linewidth=6, solid_capstyle='butt', zorder=10)
ax.text(x_start - (deg_per_km/2), y_pos + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', 
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2), zorder=10)

# 2. North Arrow
ax.annotate('N', xy=(0.95, 0.95), xytext=(0.95, 0.87),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=18, fontweight='bold', 
            xycoords=ax.transAxes, zorder=10)

# 3. Legend
legend_elements = [Patch(facecolor='#FF4500', edgecolor='white', label='Validation Patches (n=100)')]
ax.legend(handles=legend_elements, loc='lower left', fontsize=12, 
          framealpha=0.9, edgecolor='black', title="AI Validation Data", title_fontsize=12)

# 4. Grid and Neatline
ax.grid(color='white', linestyle='--', linewidth=1, alpha=0.3)
ax.add_patch(Rectangle((bounds.left, bounds.bottom), 
                       bounds.right - bounds.left, 
                       bounds.top - bounds.bottom, 
                       fill=False, edgecolor='black', linewidth=2, zorder=11))

plt.tight_layout()

out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_4_Preprint_Patches_Final.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Figure 4 successfully saved to: {out_path}")