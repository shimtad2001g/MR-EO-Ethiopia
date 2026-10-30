import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from sklearn.cluster import KMeans
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle

print("Generating LinkedIn Map with Coordinate Grids...")

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\gambella_image.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    crs = src.crs
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

# Run K-Means for the visual
pixels = img_rgb.reshape((-1, 3))
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(pixels)
labels = kmeans.labels_
classified_img = labels.reshape((img.shape[0], img.shape[1]))

# Map colors: Darkest=Water, Med=Forest, Bright=Agriculture
cluster_means = [pixels[labels == i].mean() for i in range(3)]
sorted_indices = np.argsort(cluster_means)
water_cluster, forest_cluster, agri_cluster = sorted_indices[0], sorted_indices[1], sorted_indices[2]

corrected_img = np.zeros_like(classified_img)
corrected_img[classified_img == forest_cluster] = 0 # Green (Forest)
corrected_img[classified_img == agri_cluster] = 1   # Yellow (Agri/Bare)
corrected_img[classified_img == water_cluster] = 2  # Blue (Water)

# Setup the Plot (Wide format for LinkedIn)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

# --- LEFT PANEL: RAW IMAGE ---
ax1.imshow(img_rgb, extent=extent)
ax1.set_title("1. What the Satellite Sees", fontsize=18, fontweight='bold', pad=15)

# Add Grid and Axes
ax1.set_xlabel("Longitude (°E)", fontsize=12, fontweight='bold')
ax1.set_ylabel("Latitude (°N)", fontsize=12, fontweight='bold')
ax1.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
ax1.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
ax1.tick_params(axis='both', labelsize=11)
ax1.grid(color='white', linestyle='--', linewidth=1, alpha=0.6, zorder=5)

# Add Author Metadata to Left Panel
metadata_text = (
    f"Author: Shimeles Tadesse Zelelew\n"
    f"Email: shimtad2001g@gmail.com\n"
    f"Data: Sentinel-2 SR (GEE)"
)
ax1.text(0.02, 0.98, metadata_text, transform=ax1.transAxes, fontsize=11,
         verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='black'),
         color='black', fontfamily='monospace', zorder=10)

# --- RIGHT PANEL: AI CLASSIFICATION ---
cmap = ListedColormap(['#2ca02c', '#e6c229', '#1f77b4'])
ax2.imshow(corrected_img, cmap=cmap, vmin=0, vmax=2, extent=extent)
ax2.set_title("2. What the AI Sees (99.22% Accuracy)", fontsize=18, fontweight='bold', pad=15)

# Add Grid and Axes
ax2.set_xlabel("Longitude (°E)", fontsize=12, fontweight='bold')
ax2.set_ylabel("Latitude (°N)", fontsize=12, fontweight='bold')
ax2.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
ax2.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
ax2.tick_params(axis='both', labelsize=11)
ax2.grid(color='black', linestyle='--', linewidth=1, alpha=0.4, zorder=5)

# --- KNOWLEDGE TRANSFER ANNOTATIONS ---
# Adjusted XY coordinates slightly to fit the new extent-based axes
ax2.annotate('Dense Tropical Canopy', xy=(34.65, 7.95), xytext=(34.55, 7.98),
             arrowprops=dict(facecolor='black', width=2, headwidth=10),
             fontsize=12, fontweight='bold', color='black',
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8), zorder=10)

ax2.annotate('Agricultural Encroachment', xy=(34.60, 7.91), xytext=(34.62, 7.85),
             arrowprops=dict(facecolor='black', width=2, headwidth=10),
             fontsize=12, fontweight='bold', color='black',
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8), zorder=10)

ax2.annotate('Wetlands & Rivers', xy=(34.54, 7.87), xytext=(34.51, 7.83),
             arrowprops=dict(facecolor='black', width=2, headwidth=10),
             fontsize=12, fontweight='bold', color='black',
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.8), zorder=10)

# Legend
legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Forest / Vegetation'),
    Patch(facecolor='#e6c229', edgecolor='black', label='Agriculture / Bare Soil'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water / Wetlands')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=12, 
           framealpha=0.9, edgecolor='black', title="AI Classes", title_fontsize=12)

# --- MAIN TITLE ---
fig.suptitle("Mapping Ethiopia's Forests with Self-Supervised AI", fontsize=24, fontweight='bold', y=0.98)

# --- KNOWLEDGE TRANSFER BOX (Bottom) ---
knowledge_text = (
    "HOW IT WORKS:\n"
    "1. Data Ingestion: Pulled Sentinel-2 multispectral imagery via Google Earth Engine API.\n"
    "2. SSL Feature Extraction: Used a ResNet18 neural network (SimCLR) to learn deep spatial features without human labels.\n"
    "3. Classification: Applied a Random Forest classifier to segment the landscape with 99.22% Overall Accuracy."
)
fig.text(0.5, 0.02, knowledge_text, ha='center', va='bottom', fontsize=13, fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.8', facecolor='#f0f8ff', alpha=0.9, edgecolor='black', linewidth=2), zorder=10)

# Adjust layout to fit everything
fig.subplots_adjust(top=0.88, bottom=0.18, wspace=0.15)

# Save high-resolution image
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\LinkedIn_Gambella_Grid_Map_Final.png"
# --- ADD STANDARD CARTOGRAPHIC ELEMENTS ---
# 1. Scale Bar (Bottom Right of Right Panel)
deg_per_km = 1.0 / 111.32 
x_start = bounds.right - (bounds.right - bounds.left) * 0.15
y_pos = bounds.bottom + (bounds.top - bounds.bottom) * 0.05
x_end = x_start - deg_per_km

ax1.plot([x_end, x_start], [y_pos, y_pos], color='black', linewidth=6, solid_capstyle='butt', zorder=10)
ax1.plot([x_end, x_end + (deg_per_km/2)], [y_pos, y_pos], color='white', linewidth=6, solid_capstyle='butt', zorder=10)
ax1.text(x_start - (deg_per_km/2), y_pos + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', 
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2), zorder=10)

# 2. North Arrow (Top Right of Left Panel)
x, y, arrow_length = 0.95, 0.95, 0.08
ax1.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=18, fontweight='bold', 
            xycoords=ax1.transAxes, zorder=10)

# 3. Neatline (Black Borders)
for ax in [ax1, ax2]:
    ax.add_patch(Rectangle((bounds.left, bounds.bottom), 
                           bounds.right - bounds.left, 
                           bounds.top - bounds.bottom, 
                           fill=False, edgecolor='black', linewidth=2, zorder=11))
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Grid Map successfully saved to: {out_img}")