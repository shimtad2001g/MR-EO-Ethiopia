import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT_CHART = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\gamo_gofa_carbon_maps\Figure4_StatisticalChart.png"

print("--- Building Statistical Chart (Figure 4) ---")

# Data derived from the Zonal Statistics (GamoGofa_Statistics.csv)
classes = ["Bare Soil /\nBuilt-up", "Cropland /\nSparse Veg", "Water", "Dense Forest", "Bright Soil /\nWater (Abaya)"]
percentages = [10.65, 40.79, 10.84, 24.67, 13.06]
colors = ['#b15928', '#33a02c', '#1f78b4', '#006400', '#ffff99']

fig, ax = plt.subplots(figsize=(10, 6))

# Create the bar chart
bars = ax.bar(classes, percentages, color=colors, edgecolor='black', linewidth=1.2, width=0.7)

# Add titles and labels
ax.set_ylabel("Percentage of Total Area (%)", fontsize=14, fontweight='bold')
ax.set_xlabel("Land Cover Class", fontsize=14, fontweight='bold')
ax.set_ylim(0, 50) # Set y-axis limit a bit above the highest bar

# Add the exact numbers on top of the bars
for bar, pct in zip(bars, percentages):
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{pct}%", ha='center', va='bottom', fontsize=12, fontweight='bold')

# Add grid lines for readability
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

# Add a neatline (border)
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('black')

# Ensure the layout is tight
fig.tight_layout()

print("--- Saving Chart ---")
os.makedirs(os.path.dirname(OUT_CHART), exist_ok=True)
fig.savefig(OUT_CHART, dpi=300, bbox_inches="tight")
print("[SUCCESS] Figure 4 saved to:", OUT_CHART)
