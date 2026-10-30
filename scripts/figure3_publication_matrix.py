import matplotlib.pyplot as plt
import numpy as np

print("Generating Publication-Ready Figure 3: Confusion Matrix...")

# Define the actual data from your XGBoost model
cm = np.array([[12, 1],
               [6, 11]])
classes = ['Vegetation (0)', 'Urban (1)']

# Setup the plot
fig, ax = plt.subplots(figsize=(8, 7))

# Create heatmap with a professional colormap
im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)

# Add colorbar
cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.ax.set_ylabel("Number of Patches", rotation=-90, va="bottom", fontsize=12, fontweight='bold')

# Add axis labels and title
ax.set(xticks=np.arange(cm.shape[1]),
       yticks=np.arange(cm.shape[0]),
       xticklabels=classes, yticklabels=classes,
       title='Figure 3: AI Confusion Matrix (XGBoost)',
       ylabel='True Class (ESA WorldCover)',
       xlabel='Predicted Class (AI)')

# Tweak label appearance
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=12, fontweight='bold')
plt.setp(ax.get_yticklabels(), fontsize=12, fontweight='bold')
ax.title.set_size(16)
ax.title.set_weight('bold')

# Loop over data dimensions and create text annotations
thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=18, fontweight='bold')

# Add a summary metrics box below the plot
metrics_text = "Overall Accuracy (OA): 76.67%   |   Kappa Coefficient: 0.5455"
plt.figtext(0.5, -0.05, metrics_text, ha="center", fontsize=14, fontweight='bold',
            bbox={"facecolor": "#f0f0f0", "alpha": 1.0, "pad": 10, "edgecolor": "black", "linewidth": 2})

plt.tight_layout()

# Save high-resolution figure
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_3_Publication_Matrix.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Figure 3 successfully saved to: {out_path}")