import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

print("Generating Pre-print Standard Figure 2: Workflow Diagram...")

# Set up the canvas (professional aspect ratio)
fig, ax = plt.subplots(figsize=(18, 6))
ax.set_xlim(0, 18)
ax.set_ylim(0, 6)
ax.axis('off') # Hide axes

# Define the 5 steps: (Title, Subtitle, X-position, Color)
steps = [
    ("1. Data Export", "Google Earth Engine\n(Sentinel-2 API)", 1.8, "#1f4e79"),
    ("2. Harmonization", "Rasterio\n(CRS Alignment)", 5.4, "#2e75b6"),
    ("3. SSL Pre-training", "PyTorch & SimCLR\n(Unlabeled Data)", 9.0, "#2ca02c"),
    ("4. Feature Extraction", "ResNet18\n(512-D Vectors)", 12.6, "#ff7f0e"),
    ("5. Validation", "XGBoost & WorldCover\n(Kappa / Accuracy)", 16.2, "#c00000")
]

# Draw the boxes and text
for title, subtitle, x_pos, color in steps:
    # Draw the rounded box
    box = patches.FancyBboxPatch((x_pos - 1.4, 2.0), 2.8, 2.0,
                                 boxstyle="round,pad=0.2", 
                                 edgecolor='black', facecolor=color, linewidth=1.5)
    ax.add_patch(box)
    
    # Add Title Text (White, Bold)
    ax.text(x_pos, 3.4, title, ha='center', va='center', 
            color='white', fontsize=15, fontweight='bold', family='sans-serif')
    
    # Add Subtitle Text (White, Regular)
    ax.text(x_pos, 2.6, subtitle, ha='center', va='center', 
            color='white', fontsize=12, family='sans-serif')

# Draw arrows connecting the boxes
for i in range(len(steps) - 1):
    start_x = steps[i][2] + 1.5
    end_x = steps[i+1][2] - 1.6
    y_pos = 3.0
    
    # Draw a sleek, modern arrow
    arrow = patches.FancyArrowPatch((start_x, y_pos), (end_x, y_pos),
                                    arrowstyle='-|>', mutation_scale=25, 
                                    linewidth=2.5, color='#333333')
    ax.add_patch(arrow)

# Add an overarching title
plt.title("Sequential Workflow of the Geo-AI Pipeline", fontsize=22, fontweight='bold', pad=30)

plt.tight_layout()

# Save high-resolution image
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_2_Preprint_Workflow.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Figure 2 successfully saved to: {out_path}")