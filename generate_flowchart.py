import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

fig, ax = plt.subplots(figsize=(16, 8), facecolor='white')
ax.set_xlim(0, 16)
ax.set_ylim(0, 8)
ax.axis('off')

# ==========================================
# Main Title and Cloud Bounding Box
# ==========================================
ax.text(8, 7.7, "Cloud-Ready Self-Supervised Learning (SSL) Framework", 
        ha='center', va='center', fontsize=20, fontweight='bold', color='#2C3E50')

cloud_box = mpatches.FancyBboxPatch((0.2, 0.2), 15.6, 7.0, boxstyle="round,pad=0.1", 
                                     edgecolor='#7F8C8D', facecolor='#F8F9F9', 
                                     linestyle='--', linewidth=3)
ax.add_patch(cloud_box)
ax.text(0.5, 6.7, "Cloud Infrastructure (AWS Open Data + Docker + Nextflow)", 
        ha='left', va='center', fontsize=12, fontweight='bold', color='#7F8C8D', style='italic')

# ==========================================
# Helper function for drawing boxes
# ==========================================
def draw_box(x, y, w, h, title, text_lines, color, title_color='white'):
    box = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", 
                                  edgecolor='black', facecolor=color, linewidth=2)
    ax.add_patch(box)
    # Title background
    title_bg = mpatches.Rectangle((x, y + h - 0.8), w, 0.8, facecolor='#2C3E50', edgecolor='none')
    ax.add_patch(title_bg)
    ax.text(x + w/2, y + h - 0.4, title, ha='center', va='center', fontsize=14, fontweight='bold', color=title_color)
    
    # Text lines
    for i, line in enumerate(text_lines):
        ax.text(x + w/2, y + h - 1.4 - (i * 0.6), line, ha='center', va='center', fontsize=11, color='black')

# ==========================================
# Stage Boxes
# ==========================================
draw_box(0.8, 2.2, 3.0, 3.5, "Stage 1:\nData Ingestion", 
         ["AWS Open Data (S3)", "Google Earth Engine", "Sentinel-2 L2A (10 m)", "120,000 Unlabelled Patches"], 
         '#D6EAF8')

draw_box(4.5, 2.2, 3.0, 3.5, "Stage 2:\nMAE Pre-training", 
         ["ViT-Base Encoder", "75% Masking Ratio", "Reconstruction Loss", "200 Epochs (72 GPU-hrs)"], 
         '#D5F5E3')

draw_box(8.2, 2.2, 3.0, 3.5, "Stage 3:\nFine-tuning", 
         ["Pre-trained Encoder", "≤500 Labels / Zone", "Downstream Classification", "U-Net / RF Baselines"], 
         '#FDEBD0')

draw_box(11.9, 2.2, 3.0, 3.5, "Stage 4:\nInference", 
         ["Land Cover Maps", "1,250 km² / GPU-hour", "OA: 87.3% – 92.6%", "Docker / Nextflow"], 
         '#E8DAEF')

# ==========================================
# Arrows and Labels (Positioned for zero overlap)
# ==========================================
arrow_props = dict(arrowstyle="->", color='#2C3E50', linewidth=3, mutation_scale=20)

# Arrow 1 -> 2
ax.annotate("", xy=(4.4, 3.95), xytext=(3.9, 3.95), arrowprops=arrow_props)
ax.text(4.15, 4.2, "Extract\nPatches", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#2C3E50')

# Arrow 2 -> 3
ax.annotate("", xy=(8.1, 3.95), xytext=(7.6, 3.95), arrowprops=arrow_props)
ax.text(7.85, 4.2, "Transfer\nWeights", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#2C3E50')

# Arrow 3 -> 4
ax.annotate("", xy=(11.8, 3.95), xytext=(11.3, 3.95), arrowprops=arrow_props)
ax.text(11.55, 4.2, "Predict\n& Map", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#2C3E50')

# Feedback loop arrow (Perfectly spaced below boxes)
ax.annotate("", xy=(9.7, 1.8), xytext=(13.4, 1.8), 
            arrowprops=dict(arrowstyle="->", color='#E74C3C', linewidth=2.5, linestyle='dashed', mutation_scale=20))
ax.annotate("", xy=(9.7, 2.05), xytext=(9.7, 1.8), 
            arrowprops=dict(arrowstyle="->", color='#E74C3C', linewidth=2.5, linestyle='dashed', mutation_scale=20))
ax.text(11.55, 1.4, "Continual Learning (New Labels)", ha='center', va='center', fontsize=11, fontweight='bold', color='#E74C3C')

plt.tight_layout()
output_path = os.path.join(r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia", "Figure_2_Framework_Flowchart.png")
plt.savefig(output_path, dpi=600, bbox_inches='tight')
print(f"Success! Perfect publication-grade flowchart saved to: {output_path}")
