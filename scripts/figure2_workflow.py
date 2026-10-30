import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects

print("Generating Professional Figure 2: Workflow Diagram...")

# Setup the canvas
fig, ax = plt.subplots(figsize=(18, 6))
ax.set_xlim(0, 18)
ax.set_ylim(0, 6)
ax.axis('off') # Hide the axes

# Define the 5 steps: (Title, Subtitle, X-position, Color)
steps = [
    ("1. Data Export", "Google Earth Engine\n(Sentinel-2 API)", 1.8, "#4A90E2"),
    ("2. Harmonization", "Rasterio\n(CRS Alignment)", 5.4, "#50E3C2"),
    ("3. SSL Pre-training", "PyTorch & SimCLR\n(Unlabeled Data)", 9.0, "#9013FE"),
    ("4. Feature Extraction", "ResNet18\n(512-D Vectors)", 12.6, "#F5A623"),
    ("5. Validation", "XGBoost & Scikit-Learn\n(Kappa / Accuracy)", 16.2, "#7ED321")
]

# Draw the boxes and text
for title, subtitle, x_pos, color in steps:
    # Draw the rounded box with a shadow effect
    box = patches.FancyBboxPatch((x_pos - 1.4, 2.0), 2.8, 2.0,
                                 boxstyle="round,pad=0.2", 
                                 edgecolor='black', facecolor=color, linewidth=2)
    
    # Add a subtle drop shadow
    shadow = patches.FancyBboxPatch((x_pos - 1.35, 1.95), 2.8, 2.0,
                                    boxstyle="round,pad=0.2", 
                                    edgecolor='none', facecolor='#cccccc', linewidth=0)
    ax.add_patch(shadow)
    ax.add_patch(box)
    
    # Add Title Text
    ax.text(x_pos, 3.4, title, ha='center', va='center', 
            color='white', fontsize=14, fontweight='bold', family='sans-serif')
    
    # Add Subtitle Text
    ax.text(x_pos, 2.6, subtitle, ha='center', va='center', 
            color='white', fontsize=11, family='sans-serif')

# Draw arrows connecting the boxes
for i in range(len(steps) - 1):
    start_x = steps[i][2] + 1.5
    end_x = steps[i+1][2] - 1.6
    y_pos = 3.0
    
    arrow = patches.FancyArrowPatch((start_x, y_pos), (end_x, y_pos),
                                    arrowstyle='-|>', mutation_scale=30, 
                                    linewidth=3, color='#333333')
    ax.add_patch(arrow)

# Add an overarching title
plt.title("MR-EO Ethiopia Geo-AI Pipeline Workflow", fontsize=22, fontweight='bold', pad=30)

# Save the figure
plt.tight_layout()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_2_Workflow_Diagram.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Figure 2 successfully saved to: {out_path}")