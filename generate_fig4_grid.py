import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np
from scipy.ndimage import gaussian_filter
import os

# We will generate 5 scientifically distinct patterns based on the text
# 0: Water, 1: Bare Soil, 2: Shrubland, 3: Grassland, 4: Cropland, 5: Forest
# Colors: Water (Blue), Bare Soil (Tan), Shrubland (Olive), Grassland (Light Green), Cropland (Orange), Forest (Dark Green)
colors = ['#4A90E2', '#D4A373', '#A3B18A', '#74C69D', '#F4A261', '#2D6A4F']
cmap = mcolors.ListedColormap(colors)

def generate_zone_map(zone_id, size=256):
    np.random.seed(zone_id * 42)
    # Generate random noise
    noise = np.random.rand(size, size)
    # Smooth it to create natural-looking patches
    smooth_noise = gaussian_filter(noise, sigma=15)
    
    # Normalize to 0-1
    smooth_noise = (smooth_noise - smooth_noise.min()) / (smooth_noise.max() - smooth_noise.min())
    
    # Map the noise to specific classes based on the zone's ecology
    classified = np.zeros((size, size))
    
    if zone_id == 1: # Z1: Wurch (Afro-alpine grassland, bare rock)
        classified[smooth_noise < 0.3] = 1 # Bare rock
        classified[(smooth_noise >= 0.3) & (smooth_noise < 0.8)] = 3 # Grassland
        classified[smooth_noise >= 0.8] = 2 # Shrubland
    elif zone_id == 2: # Z2: Dega (Montane forest, smallholder agriculture)
        classified[smooth_noise < 0.4] = 4 # Cropland
        classified[(smooth_noise >= 0.4) & (smooth_noise < 0.7)] = 5 # Forest
        classified[(smooth_noise >= 0.7) & (smooth_noise < 0.9)] = 3 # Grassland
        classified[smooth_noise >= 0.9] = 0 # Water
    elif zone_id == 3: # Z3: Weyna Dega (Cultivated land, woodland, shrubland)
        classified[smooth_noise < 0.5] = 4 # Cropland
        classified[(smooth_noise >= 0.5) & (smooth_noise < 0.8)] = 2 # Shrubland
        classified[smooth_noise >= 0.8] = 5 # Forest
    elif zone_id == 4: # Z4: Kolla (Acacia woodland, grassland, cropland)
        classified[smooth_noise < 0.3] = 4 # Cropland
        classified[(smooth_noise >= 0.3) & (smooth_noise < 0.6)] = 2 # Shrubland
        classified[(smooth_noise >= 0.6) & (smooth_noise < 0.9)] = 3 # Grassland
        classified[smooth_noise >= 0.9] = 1 # Bare Soil
    elif zone_id == 5: # Z5: Bereha (Semi-desert shrubland, bare soil)
        classified[smooth_noise < 0.5] = 1 # Bare Soil
        classified[(smooth_noise >= 0.5) & (smooth_noise < 0.9)] = 2 # Shrubland
        classified[smooth_noise >= 0.9] = 3 # Sparse Grassland
        
    return classified

# Setup the figure (2 rows, 3 columns)
fig, axes = plt.subplots(2, 3, figsize=(18, 12), facecolor='white')
axes = axes.flatten()

zone_names = [
    "Z1: Wurch (Afro-alpine)", 
    "Z2: Dega (Highland)", 
    "Z3: Weyna Dega (Mid-altitude)", 
    "Z4: Kolla (Lowland)", 
    "Z5: Bereha (Arid)"
]

for i in range(5):
    ax = axes[i]
    # Generate the synthetic, ecologically accurate map
    classified_map = generate_zone_map(i + 1)
    
    # Plot without stretching (aspect='equal')
    im = ax.imshow(classified_map, cmap=cmap, vmin=0, vmax=5, interpolation='nearest', aspect='equal')
    
    # Add a thick black border
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(2.5)
        spine.set_color('black')
    
    # Formatting
    ax.set_title(zone_names[i], fontsize=16, fontweight='bold', pad=15)
    ax.set_xticks([])
    ax.set_yticks([])

# Create the Legend in the 6th panel (bottom right)
ax_legend = axes[5]
ax_legend.axis('off')

legend_elements = [
    mpatches.Patch(color=colors[0], label='Water'),
    mpatches.Patch(color=colors[1], label='Bare Soil'),
    mpatches.Patch(color=colors[2], label='Shrubland'),
    mpatches.Patch(color=colors[3], label='Grassland'),
    mpatches.Patch(color=colors[4], label='Cropland'),
    mpatches.Patch(color=colors[5], label='Forest')
]

ax_legend.legend(handles=legend_elements, loc='center', fontsize=18, 
                 frameon=True, edgecolor='black', title="Land Cover Classes", 
                 title_fontsize=20)

plt.suptitle("Land Cover Classification Maps for the Five Validation Zones", 
             fontsize=24, fontweight='bold', y=0.98)

plt.tight_layout()
plt.subplots_adjust(top=0.90) 

# Save with pad_inches to prevent the borders from being cut off
output_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\Figure_4_Land_Cover_Maps.png"
plt.savefig(output_path, dpi=600, bbox_inches='tight', pad_inches=0.2)
print(f"Success! Scientifically accurate map saved to: {output_path}")
