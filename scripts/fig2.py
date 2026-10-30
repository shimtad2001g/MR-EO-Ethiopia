import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_PNG = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\Figure2_Methodology.png"

print("--- Building Methodological Framework Flowchart ---")
fig, ax = plt.subplots(figsize=(14, 9))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off') # Hide axes

# Define colors
color_data = '#f4f4f4'    # Light grey
color_kmeans = '#d9e8f5'  # Light blue
color_carbon = '#e6f5d9'  # Light green
color_stats = '#fce4d6'   # Light orange
color_out = '#e2e2e2'     # Darker grey

# Helper functions for drawing boxes and arrows
def draw_box(ax, text, xy, width, height, color, text_color='black'):
    x, y = xy
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.1,rounding_size=0.2",
                         edgecolor='black', facecolor=color, linewidth=1.5, zorder=2)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=11, fontweight='bold', color=text_color, zorder=3)

def draw_arrow(ax, start, end):
    arrow = FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=20, 
                            linewidth=2, color='#333333', zorder=1)
    ax.add_patch(arrow)

# --- 1. Top Node: Input Data ---
draw_box(ax, "Data Acquisition\n(12-Band Sentinel-2 Level-2A Imagery)", xy=(5, 9), width=5, height=1, color=color_data)

# --- 2. Second Row: Two Parallel Processes ---
draw_box(ax, "K-Means Unsupervised Classification\n(200,000 Sampled Pixels, K=5)", xy=(2.5, 6.5), width=4, height=1.2, color=color_kmeans)
draw_box(ax, "ResNet18 Deep Learning Model\n(Carbon Biomass Prediction)", xy=(7.5, 6.5), width=4, height=1.2, color=color_carbon)

# Arrows from Top Node to Second Row
draw_arrow(ax, (3.5, 8.5), (2.5, 7.1))
draw_arrow(ax, (6.5, 8.5), (7.5, 7.1))

# --- 3. Third Row: Outputs of processes ---
draw_box(ax, "Land Cover Classes\n(Bare, Cropland, Water, Forest)", xy=(2.5, 4), width=4, height=1, color=color_kmeans)
draw_box(ax, "Continuous Carbon Raster\n(Resampled to 10m Grid)", xy=(7.5, 4), width=4, height=1, color=color_carbon)

# Arrows from Second to Third Row
draw_arrow(ax, (2.5, 5.9), (2.5, 4.5))
draw_arrow(ax, (7.5, 5.9), (7.5, 4.5))

# --- 4. Fourth Row: Masking and Statistics ---
draw_box(ax, "Strict Swath & Geometric Lake Masking\n(Scientific Integrity Verification)", xy=(7.5, 2), width=4.5, height=1, color=color_stats)
draw_box(ax, "Zonal Statistics Calculation\n(Hectares, km², Percentages)", xy=(2.5, 2), width=4.5, height=1, color=color_stats)

# Arrows from Third to Fourth Row
draw_arrow(ax, (2.5, 3.5), (2.5, 2.5))
draw_arrow(ax, (7.5, 3.5), (7.5, 2.5))

# --- 5. Bottom Row: Final Integration & Outputs ---
draw_box(ax, "Total Carbon Stock Estimation\n(3,236,359.25 Metric Tons)", xy=(5, 0.2), width=5, height=0.8, color=color_out)

# Arrows merging into the bottom node
draw_arrow(ax, (2.5, 1.5), (4.0, 0.6))
draw_arrow(ax, (7.5, 1.5), (6.0, 0.6))

# Title
ax.set_title("Methodological Framework: Land Cover Classification & Carbon Biomass Estimation", fontsize=16, fontweight='bold', pad=20)

print("--- Saving Flowchart ---")
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
print("[SUCCESS] Figure 2 (Methodology Flowchart) saved to:", OUT_PNG)
