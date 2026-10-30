import matplotlib.pyplot as plt

print("Generating Academic-Standard Figure 8...")

# Clean labels (no redundant percentages)
labels = ['Vegetation', 'Urban / Bare Soil', 'Water Bodies']
sizes = [34.4, 46.6, 19.0]
colors = ['#2ca02c', '#7f7f7f', '#1f77b4'] # Green, Gray, Blue

fig, ax = plt.subplots(figsize=(10, 7))

# Create a FLAT (no shadow, no explode) pie chart
wedges, texts, autotexts = ax.pie(
    sizes, 
    labels=labels, 
    colors=colors,
    autopct='%1.1f%%', 
    startangle=140, 
    textprops={'fontsize': 15, 'fontweight': 'bold'},
    wedgeprops={'edgecolor': 'black', 'linewidth': 1.5} # Black borders for crispness
)

# Make the percentage text white
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(16)

# Clean Title (No "Figure 8" in the image itself)
plt.title('AI Land Cover Distribution (Addis Ababa)', 
          fontsize=18, fontweight='bold', pad=20)

ax.axis('equal') # Ensure perfect circle
plt.tight_layout()

out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_8_Final_Academic.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 8 successfully saved to: {out_img}")