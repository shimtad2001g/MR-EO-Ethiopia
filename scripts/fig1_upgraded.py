import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import geopandas as gpd
import matplotlib.patheffects as pe

OUT_PNG = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\Figure1_StudyArea.png"

print("--- 1. Downloading Country Boundaries (50m) ---")
url_countries = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
gdf_countries = gpd.read_file(url_countries)

print("--- 2. Downloading Ethiopia Regions (110m) ---")
url_regions = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_1_states_provinces.geojson"
gdf_regions = gpd.read_file(url_regions)

# Filter data
ethiopia = gdf_countries[gdf_countries['NAME'] == 'Ethiopia']
eth_regions = gdf_regions[gdf_regions['admin'] == 'Ethiopia']

# Neighbors for context
neighbors = gdf_countries[gdf_countries['NAME'].isin(['Kenya', 'Somalia', 'Sudan', 'South Sudan', 'Eritrea', 'Djibouti'])]

print("--- 3. Building Map ---")
fig, ax = plt.subplots(figsize=(12, 10))

# Plot neighboring countries
neighbors.plot(ax=ax, color='#f0f0f0', edgecolor='grey', linewidth=0.5)

# Plot Ethiopia
ethiopia.plot(ax=ax, color='#d9e8f5', edgecolor='black', linewidth=1.5)

# Plot Ethiopian internal regions (dashed)
eth_regions.plot(ax=ax, color='none', edgecolor='grey', linewidth=0.8, linestyle='--')

# Draw the exact Gamo Gofa bounding box
# Gamo Gofa is roughly Longitude 36.5 to 38.0, Latitude 5.5 to 6.5
rect = Rectangle((36.8, 5.6), 1.0, 0.8, fill=True, facecolor='red', alpha=0.4, edgecolor='red', linewidth=2)
ax.add_patch(rect)

# Add Labels
ax.text(36.2, 6.6, "Gamo Gofa Zone", color='darkred', fontsize=12, fontweight='bold',
        path_effects=[pe.withStroke(linewidth=3, foreground="white")])

# Neighbor labels
ax.text(38.0, 1.5, "Kenya", fontsize=12, color='grey', ha='center')
ax.text(45.0, 6.0, "Somalia", fontsize=12, color='grey', ha='center')
ax.text(33.0, 10.0, "Sudan", fontsize=12, color='grey', ha='center')
ax.text(31.0, 6.0, "South Sudan", fontsize=12, color='grey', ha='center')
ax.text(39.0, 15.0, "Eritrea", fontsize=12, color='grey', ha='center')
ax.text(42.5, 11.8, "Djibouti", fontsize=10, color='grey', ha='center')

# Set map extent (Zoom to East Africa)
ax.set_xlim(32, 48)
ax.set_ylim(2, 16)

# Formatting
ax.set_title("Study Area Context: Gamo Gofa Zone, Ethiopia", fontsize=18, fontweight='bold', pad=15)
ax.set_xlabel("Longitude", fontsize=12, fontweight='bold')
ax.set_ylabel("Latitude", fontsize=12, fontweight='bold')
ax.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)

# Add a thick neatline (border)
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

print("--- 4. Saving Map ---")
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("[SUCCESS] Figure 1 saved to:", OUT_PNG)
