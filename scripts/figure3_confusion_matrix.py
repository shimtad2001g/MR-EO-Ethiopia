import matplotlib.pyplot as plt
import numpy as np
import os

print("Generating Figure 3: Confusion Matrix Heatmap...")

# Your actual results
cm = np.array([[12, 1], 
               [6, 11]])
classes = ['Vegetation', 'Urban']

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
ax.figure.colorbar(im, ax=ax)

# Add labels and ticks
ax.set(xticks=np.arange(cm.shape[1]),
       yticks=np.arange(cm.shape[0]),
       xticklabels=classes, yticklabels=classes,
       title='Figure 3: AI Confusion Matrix (XGBoost)',
       ylabel='True Class (ESA WorldCover)',
       xlabel='Predicted Class (AI)')

# Loop over data dimensions and create text annotations
thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=16, fontweight='bold')

plt.tight_layout()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_3_Confusion_Matrix.png"
plt.savefig(out_path, dpi=300)
print(f"✅ Figure 3 successfully saved to: {out_path}")