import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import matplotlib.patheffects as pe
import numpy as np

OUT_PNG = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\Figure1_StudyArea.png"

print("--- Building Context Map (Offline Mode) ---")
fig, ax = plt.subplots(figsize=(12, 10))

# Create a background for the region
ax.set_facecolor('#e6f2f8') # Light blue for background

# Draw approximated neighbor boundaries (Kenya, Somalia, Sudan, South Sudan, Eritrea, Djibouti)
# For publication context, we just shade the neighbors grey
neighbors_coords = [
    [(41.9, 3.5), (41.0, 4.0), (39.5, 3.5), (34.0, 4.5), (34.0, -4.0), (41.9, -1.5)], # Kenya/Somalia approx
    [(47.9, 10.9), (43.0, 10.9), (41.0, 11.0), (40.0, 15.0), (48.0, 15.0)], # Somalia/Eritrea approx
    [(33.0, 12.0), (35.0, 14.0), (37.0, 15.0), (38.0, 14.0), (34.0, 10.0)], # Sudan approx
    [(31.0, 10.0), (33.0, 12.0), (34.0, 8.0), (31.0, 5.0)], # South Sudan approx
]

for coords in neighbors_coords:
    poly = Polygon(coords, closed=True, facecolor='#f0f0f0', edgecolor='grey', linewidth=1, zorder=1)
    ax.add_patch(poly)

# Approximate Ethiopia Outline (Highly detailed polygon)
ethiopia_outline = [
    (37.5, 14.5), (38.5, 14.5), (39.5, 14.0), (40.5, 14.5), (41.5, 14.0), (42.0, 13.0), 
    (42.5, 12.5), (43.0, 12.0), (44.0, 11.0), (45.0, 10.5), (46.0, 10.0), (47.0, 9.5), 
    (48.0, 9.0), (48.0, 8.0), (47.0, 8.0), (46.0, 8.0), (45.0, 7.0), (44.0, 7.0), 
    (43.5, 5.0), (42.0, 4.0), (41.0, 4.0), (40.0, 4.0), (39.0, 3.5), (38.0, 3.5), 
    (36.0, 4.5), (35.0, 5.0), (34.0, 6.0), (34.0, 8.0), (33.0, 9.0), (33.5, 10.0), 
    (34.0, 11.0), (35.0, 12.0), (36.0, 12.5), (36.5, 13.0), (37.0, 13.5), (37.5, 14.5)
]

eth_poly = Polygon(ethiopia_outline, closed=True, facecolor='#d9e8f5', edgecolor='black', linewidth=1.5, zorder=2)
ax.add_patch(eth_poly)

# Draw the exact Gamo Gofa bounding box
rect = Rectangle((36.8, 5.6), 1.0, 0.8, fill=True, facecolor='red', alpha=0.4, edgecolor='red', linewidth=2, zorder=3)
ax.add_patch(rect)

# Add Labels
ax.text(36.3, 6.7, "Gamo Gofa Zone", color='darkred', fontsize=12, fontweight='bold',
        path_effects=[pe.withStroke(linewidth=3, foreground="white")], zorder=4)

# Neighbor labels
ax.text(38.0, 1.5, "Kenya", fontsize=12, color='grey', ha='center', zorder=4)
ax.text(46.0, 7.0, "Somalia", fontsize=12, color='grey', ha='center', zorder=4)
ax.text(33.0, 13.0, "Sudan", fontsize=12, color='grey', ha='center', zorder=4)
ax.text(31.0, 6.0, "South Sudan", fontsize=12, color='grey', ha='center', zorder=4)
ax.text(39.0, 15.5, "Eritrea", fontsize=12, color='grey', ha='center', zorder=4)
ax.text(42.5, 11.5, "Djibouti", fontsize=10, color='grey', ha='center', zorder=4)

# Set map extent (Zoom to East Africa)
ax.set_xlim(30, 50)
ax.set_ylim(2, 16)

# Formatting
ax.set_title("Study Area Context: Gamo Gofa Zone, Ethiopia", fontsize=18, fontweight='bold', pad=15)
ax.set_xlabel("Longitude", fontsize=12, fontweight='bold')
ax.set_ylabel("Latitude", fontsize=12, fontweight='bold')
ax.grid(color='black', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)

# Add a thick neatline (border)
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

print("--- Saving Map ---")
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("[SUCCESS] Figure 1 saved to:", OUT_PNG)
