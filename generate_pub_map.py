import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.patches as mpatches
import os

fig = plt.figure(figsize=(14, 10))

# ==========================================
# 1. MAIN MAP: Ethiopia and 5 Validation Zones
# ==========================================
ax_main = fig.add_axes([0.05, 0.05, 0.65, 0.85], projection=ccrs.PlateCarree())
ax_main.set_extent([32, 48, 2, 16], crs=ccrs.PlateCarree())

# USE REAL SATELLITE/ELEVATION BASEMAP
ax_main.stock_img()

# Add borders and coastlines on top
ax_main.add_feature(cfeature.BORDERS, linestyle='-', edgecolor='black', linewidth=1.2)
ax_main.add_feature(cfeature.COASTLINE, linewidth=1.2)

# Define the 5 Zones with Radius (in degrees) to simulate bounding boxes
zones = {
    'Z1: Wurch\n(Afro-alpine)': {'lat': 13.2, 'lon': 38.2, 'color': '#800080', 'radius': 0.8},
    'Z2: Dega\n(Highland)': {'lat': 9.0, 'lon': 39.0, 'color': '#008000', 'radius': 1.0},
    'Z3: Weyna Dega\n(Mid-alt)': {'lat': 7.5, 'lon': 38.5, 'color': '#FFD700', 'radius': 1.0},
    'Z4: Kolla\n(Lowland)': {'lat': 11.5, 'lon': 40.0, 'color': '#FF8C00', 'radius': 1.2},
    'Z5: Bereha\n(Arid)': {'lat': 5.0, 'lon': 43.0, 'color': '#FF0000', 'radius': 1.5}
}

for name, data in zones.items():
    # Add a semi-transparent circle to simulate the zone area
    circle = mpatches.Circle((data['lon'], data['lat']), radius=data['radius'], 
                             facecolor=data['color'], alpha=0.3, edgecolor='black', linewidth=1.5, zorder=4)
    ax_main.add_patch(circle)
    
    # Add a distinct central point
    ax_main.scatter(data['lon'], data['lat'], s=150, c=data['color'], edgecolor='black', zorder=5, label=name.replace('\n', ' '))
    
    # Add text labels with a clean background box
    ax_main.text(data['lon'] + data['radius'] + 0.2, data['lat'] + 0.2, name, fontsize=11, fontweight='bold', va='bottom', zorder=6,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.9))

# Gridlines
gl = ax_main.gridlines(draw_labels=True, linewidth=0.5, color='white', alpha=0.5, linestyle='--')
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 12, 'weight': 'bold'}
gl.ylabel_style = {'size': 12, 'weight': 'bold'}

# Title and Legend
ax_main.set_title('Study Area: Five Agro-Ecological Validation Zones in Ethiopia', fontsize=18, fontweight='bold', pad=20)
ax_main.legend(loc='lower left', fontsize=11, framealpha=1, edgecolor='black', bbox_to_anchor=(0.01, 0.01))

# ==========================================
# 2. INSET MAP: Africa (Top Right)
# ==========================================
ax_inset = fig.add_axes([0.75, 0.6, 0.2, 0.3], projection=ccrs.PlateCarree())
ax_inset.set_extent([-20, 55, -35, 40], crs=ccrs.PlateCarree())
ax_inset.add_feature(cfeature.OCEAN, facecolor='#D4E6F1')
ax_inset.add_feature(cfeature.LAND, facecolor='#EAECEE')
ax_inset.add_feature(cfeature.BORDERS, linestyle='-', edgecolor='gray', linewidth=0.5)
ax_inset.add_feature(cfeature.COASTLINE, linewidth=0.8)

shp_path = shpreader.natural_earth(resolution='110m', category='cultural', name='admin_0_countries')
reader = shpreader.Reader(shp_path)

for record in reader.records():
    if record.attributes['NAME'] == 'Ethiopia':
        ax_inset.add_geometries([record.geometry], ccrs.PlateCarree(), facecolor='#E67E22', edgecolor='black', linewidth=1)
        
ax_inset.set_title('Africa', fontsize=12, fontweight='bold')

# ==========================================
# 3. SAVE THE MAP
# ==========================================
target_dir = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia"
output_path = os.path.join(target_dir, "Publication_Study_Area_Map.png")
plt.savefig(output_path, dpi=600)
print(f"Success! Final publication-grade map saved to: {output_path}")
