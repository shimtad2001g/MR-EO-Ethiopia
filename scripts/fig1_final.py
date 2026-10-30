import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import geopandas as gpd
import matplotlib.patheffects as pe

OUT_PNG = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\Figure1_StudyArea.png"
DATA_DIR = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data"
COUNTRIES_PATH = os.path.join(DATA_DIR, "ne_50m_countries.geojson")

print("--- Loading Data ---")
gdf_countries = gpd.read_file(COUNTRIES_PATH)
ethiopia = gdf_countries[gdf_countries['NAME'] == 'Ethiopia']
neighbors = gdf_countries[gdf_countries['NAME'].isin(['Kenya', 'Somalia', 'Sudan', 'South Sudan', 'Eritrea', 'Djibouti'])]

print("--- Building Map ---")
fig, ax = plt.subplots(figsize=(12, 10))

# Plot neighbors and Ethiopia
neighbors.plot(ax=ax, color='#f4f4f4', edgecolor='#888888', linewidth=0.8)
ethiopia.plot(ax=ax, color='#d9e8f5', edgecolor='black', linewidth=2.0)

# Draw the Gamo Gofa bounding box
rect = Rectangle((36.7, 5.5), 1.3, 1.0, fill=True, facecolor='red', alpha=0.3, edgecolor='darkred', linewidth=2.5)
ax.add_patch(rect)

# Add Labels with white strokes for readability
ax.text(36.8, 6.7, "Gamo Gofa Zone", color='darkred', fontsize=13, fontweight='bold',
        path_effects=[pe.withStroke(linewidth=3.5, foreground="white")])

# Neighbor labels (Adjusted positions to prevent overlapping and cutoff)
ax.text(38.5, 2.5, "Kenya", fontsize=12, color='#555555', ha='center', fontweight='bold')
ax.text(46.0, 6.5, "Somalia", fontsize=12, color='#555555', ha='center', fontweight='bold')
ax.text(34.0, 12.0, "Sudan", fontsize=12, color='#555555', ha='center', fontweight='bold')
ax.text(32.0, 7.5, "South\nSudan", fontsize=12, color='#555555', ha='center', fontweight='bold')
ax.text(39.5, 15.2, "Eritrea", fontsize=12, color='#555555', ha='center', fontweight='bold')
ax.text(42.8, 11.5, "Djibouti", fontsize=10, color='#555555', ha='center', fontweight='bold')

# Set map extent (Zoom to East Africa to fit all text)
ax.set_xlim(30, 48)
ax.set_ylim(2, 16)

# Fix the aspect ratio (makes it visually accurate for Lat/Lon)
ax.set_aspect(1) 

# Formatting
ax.set_title("Study Area Context: Gamo Gofa Zone, Ethiopia", fontsize=18, fontweight='bold', pad=15)
ax.set_xlabel("Longitude", fontsize=12, fontweight='bold')
ax.set_ylabel("Latitude", fontsize=12, fontweight='bold')
ax.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3)

# Neatline
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

print("--- Saving Map ---")
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("[SUCCESS] Final Publication-Ready Figure 1 saved to:", OUT_PNG)
