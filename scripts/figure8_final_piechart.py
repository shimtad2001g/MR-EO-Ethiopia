import matplotlib.pyplot as plt

print("Generating Publication-Ready Figure 8: Pie Chart...")

# Exact percentages derived from the AI classification
labels = ['Vegetation\n(34.4%)', 'Urban / Bare Soil\n(46.6%)', 'Water Bodies\n(19.0%)']
sizes = [34.4, 46.6, 19.0]
colors = ['#2ca02c', '#7f7f7f', '#1f77b4'] # Green, Gray, Blue

# Setup the figure
fig, ax = plt.subplots(figsize=(10, 8))

# Create the pie chart with white borders, a slight separation, and a shadow
wedges, texts, autotexts = ax.pie(
    sizes, 
    labels=labels, 
    colors=colors,
    autopct='%1.1f%%', 
    startangle=140, 
    textprops={'fontsize': 14, 'fontweight': 'bold'},
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}, # White borders between slices
    explode=(0.03, 0.03, 0.03), # Slightly pull the slices apart
    shadow=True # Adds a professional depth effect
)

# Make the percentage text white and bold for visibility
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(16)

# Add Title
plt.title('Figure 8: AI Land Cover Distribution\n(Addis Ababa, Ethiopia)', 
          fontsize=20, fontweight='bold', pad=25)

# Ensure it is a perfect circle
ax.axis('equal') 

plt.tight_layout()

out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_8_Publication_PieChart.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 8 successfully saved to: {out_img}")