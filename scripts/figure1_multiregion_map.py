import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

print("Generating Pre-print Standard Multi-Region Study Area Map...")

# Paths to the two images
addis_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"
awash_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\awash_image.tif"

def load_and_stretch(path):
    with rasterio.open(path) as src:
        img = src.read([1, 2, 3])
        img = np.moveaxis(img, 0, -1)
        bounds = src.bounds
        crs = src.crs
        # Contrast Stretch
        p2, p98 = np.percentile(img, (2, 98))
        img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)
        return img_rgb, bounds, crs

addis_rgb, addis_bounds, addis_crs = load_and_stretch(addis_path)
awash_rgb, awash_bounds, awash_crs = load_and_stretch(awash_path)

# Setup side-by-side figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# ==========================================
# LEFT PANEL: ADDIS ABABA
# ==========================================
ax1.imshow(addis_rgb, extent=[addis_bounds.left, addis_bounds.right, addis_bounds.bottom, addis_bounds.top])
ax1.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax1.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')
ax1.set_title("A: Addis Ababa (Urban Testbed)", fontsize=16, fontweight='bold', pad=15)

# Scale Bar (Addis)
deg_per_km = 1.0 / 111.32 
x_start = addis_bounds.right - (addis_bounds.right - addis_bounds.left) * 0.1
y_pos = addis_bounds.bottom + (addis_bounds.top - addis_bounds.bottom) * 0.05
x_end = x_start - deg_per_km
ax1.plot([x_end, x_start], [y_pos, y_pos], color='black', linewidth=6, zorder=10)
ax1.plot([x_end, x_end + (deg_per_km/2)], [y_pos, y_pos], color='white', linewidth=6, zorder=10)
ax1.text(x_start - (deg_per_km/2), y_pos + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'), zorder=10)

# North Arrow (Addis)
ax1.annotate('N', xy=(0.95, 0.95), xytext=(0.95, 0.87), arrowprops=dict(facecolor='black', width=5, headwidth=15), ha='center', va='center', fontsize=16, fontweight='bold', xycoords=ax1.transAxes, zorder=10)

ax1.grid(color='white', linestyle='--', linewidth=1, alpha=0.4)
ax1.add_patch(Rectangle((addis_bounds.left, addis_bounds.bottom), addis_bounds.right - addis_bounds.left, addis_bounds.top - addis_bounds.bottom, fill=False, edgecolor='black', linewidth=2))

# ==========================================
# RIGHT PANEL: AWASH BASIN
# ==========================================
ax2.imshow(awash_rgb, extent=[awash_bounds.left, awash_bounds.right, awash_bounds.bottom, awash_bounds.top])
ax2.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax2.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')
ax2.set_title("B: Awash Basin (Agricultural/Arid Testbed)", fontsize=16, fontweight='bold', pad=15)

# Scale Bar (Awash)
x_start_awash = awash_bounds.right - (awash_bounds.right - awash_bounds.left) * 0.1
y_pos_awash = awash_bounds.bottom + (awash_bounds.top - awash_bounds.bottom) * 0.05
x_end_awash = x_start_awash - deg_per_km
ax2.plot([x_end_awash, x_start_awash], [y_pos_awash, y_pos_awash], color='black', linewidth=6, zorder=10)
ax2.plot([x_end_awash, x_end_awash + (deg_per_km/2)], [y_pos_awash, y_pos_awash], color='white', linewidth=6, zorder=10)
ax2.text(x_start_awash - (deg_per_km/2), y_pos_awash + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'), zorder=10)

# North Arrow (Awash)
ax2.annotate('N', xy=(0.95, 0.95), xytext=(0.95, 0.87), arrowprops=dict(facecolor='black', width=5, headwidth=15), ha='center', va='center', fontsize=16, fontweight='bold', xycoords=ax2.transAxes, zorder=10)

ax2.grid(color='white', linestyle='--', linewidth=1, alpha=0.4)
ax2.add_patch(Rectangle((awash_bounds.left, awash_bounds.bottom), awash_bounds.right - awash_bounds.left, awash_bounds.top - awash_bounds.bottom, fill=False, edgecolor='black', linewidth=2))

# ==========================================
# SHARED ELEMENTS
# ==========================================
# Main Overarching Title
fig.suptitle("Figure 1: Multi-Region Study Area Map (Ethiopia)\nSentinel-2 True Color Composite", fontsize=20, fontweight='bold', y=1.02)

# Metadata Box (Bottom left of the whole figure)
metadata_text = (
    f"Projection: EPSG:4326 (WGS 84)\n"
    f"Data Source: Sentinel-2 SR (GEE)\n"
    f"Author: Shimeles T. Zelelew\n"
    f"Date: October 2026"
)
fig.text(0.01, -0.05, metadata_text, fontsize=12, 
         bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='black'),
         color='black', fontfamily='monospace')

plt.tight_layout()
# Adjust for the suptitle
fig.subplots_adjust(top=0.88, bottom=0.1)

out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_1_MultiRegion_Map.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Multi-Region Map successfully saved to: {out_img}")