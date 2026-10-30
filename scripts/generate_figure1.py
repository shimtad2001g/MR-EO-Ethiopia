import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

print("Generating Figure 1: Conceptual Workflow Diagram...")

fig, ax = plt.subplots(figsize=(14, 6))
ax.set_xlim(0, 15)
ax.set_ylim(0, 6)
ax.axis('off') # Hide axes

# Define the steps
steps = [
    ("Step 1\nExport Data\n(GEE API)", 1.5, 3, "#4CAF50"),
    ("Step 2\nHarmonize Grids\n(Rasterio)", 4.5, 3, "#2196F3"),
    ("Step 3\nSSL Pre-training\n(PyTorch)", 7.5, 3, "#9C27B0"),
    ("Step 4\nFeature Extraction\n(PyTorch)", 10.5, 3, "#FF9800"),
    ("Step 5\nXGBoost Validation\n(Scikit-Learn)", 13.5, 3, "#F44336")
]

# Draw boxes and text
for text, x, y, color in steps:
    # Draw rounded box
    box = patches.FancyBboxPatch((x - 1.1, y - 0.8), 2.2, 1.6,
                                 boxstyle="round,pad=0.2", 
                                 edgecolor='black', facecolor=color, linewidth=2)
    ax.add_patch(box)
    # Add text
    ax.text(x, y, text, ha='center', va='center', color='white', 
            fontsize=12, fontweight='bold', family='sans-serif')

# Draw arrows between boxes
for i in range(len(steps) - 1):
    x_start = steps[i][1] + 1.2
    x_end = steps[i+1][1] - 1.2
    y = 3
    ax.annotate('', xy=(x_end, y), xytext=(x_start, y),
                arrowprops=dict(arrowstyle='-|>', color='black', lw=3))

# Add overarching title
plt.title("MR-EO Ethiopia Geo-AI Pipeline Workflow", fontsize=18, fontweight='bold', pad=20)

# Save the figure
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_1_Workflow.png"
plt.tight_layout()
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Figure 1 successfully saved to: {out_path}")