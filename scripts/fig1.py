import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import geopandas as gpd

OUT_PNG = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\Figure1_StudyArea.png"

url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
gdf = gpd.read_file(url)
eth = gdf[gdf['NAME'] == 'Ethiopia']

fig, ax = plt.subplots(figsize=(8, 8))
eth.plot(ax=ax, color='#e0e0e0', edgecolor='black', linewidth=1)

# Add a red box over Gamo Gofa (approx bounds)
# UTM Bounds: x: 310000 to 375000, y: 630000 to 700000 -> Lat/Lon approx
rect = Rectangle((36.5, 5.5), 1.5, 1.0, fill=False, edgecolor='red', linewidth=3)
ax.add_patch(rect)
ax.text(37.25, 5.3, "Gamo Gofa Zone", ha='center', color='red', fontweight='bold', fontsize=12)

ax.set_title("Ethiopia Context: Gamo Gofa Study Area", fontsize=16, fontweight='bold')
ax.set_xticks([])
ax.set_yticks([])

os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("[SUCCESS] Figure 1 (Study Area) saved to:", OUT_PNG)
