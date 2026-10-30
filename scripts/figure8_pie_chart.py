import rasterio
import numpy as np
import matplotlib.pyplot as plt

print("Generating Figure 8: Class Distribution Pie Chart...")

# Load the classified map you generated earlier
class_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\landcover_classified.tif"

with rasterio.open(class_path) as src:
    classified = src.read(1)
    
# Count pixels for each class (0=Veg, 1=Urban, 2=Water)
unique, counts = np.unique(classified, return_counts=True)
class_counts = dict(zip(unique, counts))

# Map to names
labels = ['Vegetation', 'Urban/Bare', 'Water']
sizes = [class_counts.get(0, 0), class_counts.get(1, 0), class_counts.get(2, 0)]
colors = ['#2ca02c', '#7f7f7f', '#1f77b4']

# Filter out classes with 0 pixels to avoid ugly charts
filtered_labels = []
filtered_sizes = []
filtered_colors = []
for l, s, c in zip(labels, sizes, colors):
    if s > 0:
        filtered_labels.append(l)
        filtered_sizes.append(s)
        filtered_colors.append(c)

fig, ax = plt.subplots(figsize=(10, 8))
ax.pie(filtered_sizes, labels=filtered_labels, colors=filtered_colors, 
       autopct='%1.1f%%', startangle=140, textprops={'fontsize': 14, 'fontweight': 'bold'})

ax.set_title('Figure 8: AI Land Cover Distribution (Addis Ababa)', fontsize=16, fontweight='bold')

plt.tight_layout()
out_path_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_8_Pie_Chart.png"
plt.savefig(out_path_img, dpi=300)
print(f"✅ Figure 8 saved to: {out_path_img}")