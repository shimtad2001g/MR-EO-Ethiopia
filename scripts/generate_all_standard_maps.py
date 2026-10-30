import rasterio
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np
import os
import geopandas as gpd

# Try to load the world map for the inset
try:
    import geodatasets
    world = gpd.read_file(geodatasets.get_path('naturalearth.land'))
    ethiopia = world[world.name == 'Ethiopia']
except Exception as e:
    print(f"Warning: Could not load naturalearth data for inset map. {e}")
    ethiopia = None

def create_standard_map(image_path, region_name, out_filename, bounds_center):
    print(f"Generating Global Standard Map for {region_name}...")
    
    with rasterio.open(image_path) as src:
        img = src.read([1, 2, 3])
        img = np.moveaxis(img, 0, -1)
        bounds = src.bounds
        crs = src.crs
        
        # Contrast Stretch
        p2, p98 = np.percentile(img, (2, 98))
        img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 1. Plot Main Image
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    ax.imshow(img_rgb, extent=extent)

    # 2. Axis Labels & Grid
    ax.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
    ax.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')
    ax.grid(color='white', linestyle='--', linewidth=1, alpha=0.6, zorder=5)

    # 3. Title (NO "Figure X:" prefix)
    plt.title(f"Study Area: {region_name}, Ethiopia\nSentinel-2 True Color Composite", 
              fontsize=18, fontweight='bold', pad=20)

    # 4. Custom Scale Bar (1 km)
    deg_per_km = 1.0 / 111.32 
    x_start = bounds.right - (bounds.right - bounds.left) * 0.1
    y_pos = bounds.bottom + (bounds.top - bounds.bottom) * 0.05
    x_end = x_start - deg_per_km

    ax.plot([x_end, x_start], [y_pos, y_pos], color='black', linewidth=6, solid_capstyle='butt', zorder=10)
    ax.plot([x_end, x_end + (deg_per_km/2)], [y_pos, y_pos], color='white', linewidth=6, solid_capstyle='butt', zorder=10)
    ax.text(x_start - (deg_per_km/2), y_pos + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2), zorder=10)

    # 5. North Arrow
    x, y, arrow_length = 0.95, 0.95, 0.08
    ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
                arrowprops=dict(facecolor='black', width=5, headwidth=15),
                ha='center', va='center', fontsize=18, fontweight='bold', 
                xycoords=ax.transAxes, zorder=10)

    # 6. Legend (Spectral Bands)
    legend_elements = [
        Rectangle((0,0), 1, 1, facecolor='#FF0000', edgecolor='black', label='Band 4 (Red)'),
        Rectangle((0,0), 1, 1, facecolor='#00FF00', edgecolor='black', label='Band 3 (Green)'),
        Rectangle((0,0), 1, 1, facecolor='#0000FF', edgecolor='black', label='Band 2 (Blue)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=12, 
              title="Sentinel-2 Bands", title_fontsize=13, framealpha=0.9, edgecolor='black')

    # 7. Metadata Box
    metadata_text = (
        f"Projection: {crs.to_string()}\n"
        f"Data Source: Sentinel-2 SR (GEE)\n"
        f"Author: Shimeles Tadesse Zelelew\n"
        f"Date: October 2026"
    )
    ax.text(0.02, 0.02, metadata_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='black'),
            color='black', fontfamily='monospace', zorder=10)

    # 8. Neatline (Border)
    ax.add_patch(Rectangle((bounds.left, bounds.bottom), 
                           bounds.right - bounds.left, 
                           bounds.top - bounds.bottom, 
                           fill=False, edgecolor='black', linewidth=2, zorder=11))

    # 9. INSET MAP (Top Right)
    if ethiopia is not None:
        # Create inset axes [left, bottom, width, height]
        ax_inset = fig.add_axes([0.68, 0.68, 0.18, 0.18])
        
        # Plot Ethiopia
        ethiopia.plot(ax=ax_inset, color='#e0e0e0', edgecolor='black')
        
        # Plot the specific region as a red star or dot
        center_lon, center_lat = bounds_center
        ax_inset.plot(center_lon, center_lat, marker='*', color='red', markersize=15, markeredgecolor='black')
        
        # Clean up inset
        ax_inset.set_title("Location in Ethiopia", fontsize=10, fontweight='bold')
        ax_inset.set_xticks([])
        ax_inset.set_yticks([])
        ax_inset.set_xlim(32, 48) # Ethiopia Longitude bounds
        ax_inset.set_ylim(3, 15)  # Ethiopia Latitude bounds
        ax_inset.set_facecolor('#f0f8ff')
        ax_inset.spines['top'].set_visible(True)
        ax_inset.spines['right'].set_visible(True)

    plt.tight_layout()
    out_path = os.path.join(r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs", out_filename)
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Saved: {out_path}")

# --- EXECUTE FOR ALL 5 REGIONS ---

# 1. Addis Ababa
create_standard_map(
    image_path=r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif",
    region_name="Addis Ababa (Urban)",
    out_filename="Map_Standard_Addis_Ababa.png",
    bounds_center=(38.76, 9.01)
)

# 2. Awash Basin
create_standard_map(
    image_path=r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\awash_image.tif",
    region_name="Awash Basin (Agriculture)",
    out_filename="Map_Standard_Awash_Basin.png",
    bounds_center=(39.85, 8.95)
)

# 3. Gambella
create_standard_map(
    image_path=r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\gambella_image.tif",
    region_name="Gambella (Forestry)",
    out_filename="Map_Standard_Gambella.png",
    bounds_center=(34.60, 7.90)
)

# 4. Afar
create_standard_map(
    image_path=r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\afar_image.tif",
    region_name="Afar (Arid Zone)",
    out_filename="Map_Standard_Afar.png",
    bounds_center=(40.90, 11.70)
)

# 5. Hawassa
create_standard_map(
    image_path=r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\hawassa_image.tif",
    region_name="Hawassa (Rift Valley)",
    out_filename="Map_Standard_Hawassa.png",
    bounds_center=(38.48, 7.05)
)

print("\n🎉 ALL 5 STANDARD MAPS GENERATED SUCCESSFULLY!")