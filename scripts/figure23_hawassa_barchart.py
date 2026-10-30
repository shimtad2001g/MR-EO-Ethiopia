import matplotlib.pyplot as plt

print("Generating Final Hawassa Bar Chart...")

# Data extracted from your Hawassa Validation script
metrics = ['Overall Accuracy (OA)', 'Kappa Coefficient (x100)']
scores = [72.73, 56.00] # Kappa multiplied by 100 for visual scaling
colors = ['#1f77b4', '#2ca02c']

fig, ax = plt.subplots(figsize=(10, 7))

# Create bars
bars = ax.bar(metrics, scores, color=colors, width=0.5, edgecolor='black', linewidth=1.5)

# Add exact data labels on top of bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.2f}%', 
            ha='center', va='bottom', fontsize=16, fontweight='bold')

# Add the 80% target line
ax.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Target Accuracy (80%)')

# Formatting
ax.set_ylim(0, 115) # High limit to prevent text overlap
ax.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold')

# REMOVED "Figure 23:" from the title
ax.set_title('AI Model Performance Metrics (Hawassa Replication)', fontsize=18, fontweight='bold', pad=20)

# Add grid lines for readability
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

# Legend
ax.legend(fontsize=12, loc='upper right', framealpha=0.9, edgecolor='black')

# Remove top and right spines for a cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

# Save high-resolution image
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_23_Hawassa_BarChart_Final.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 23 successfully saved to: {out_img}")