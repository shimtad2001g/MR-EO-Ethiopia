import matplotlib.pyplot as plt
import numpy as np

print("Generating Publication-Ready Figure 5: Bar Chart...")

# Data
metrics = ['Overall Accuracy (OA)', 'Kappa Coefficient (x100)']
scores = [76.67, 54.55] # Kappa multiplied by 100 for visual scaling
colors = ['#1f77b4', '#2ca02c'] # Blue for OA, Green for Kappa

fig, ax = plt.subplots(figsize=(10, 7))

# Create bars
bars = ax.bar(metrics, scores, color=colors, width=0.5, edgecolor='black', linewidth=1.5)

# Add exact data labels on top of bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.2f}%', 
            ha='center', va='bottom', fontsize=15, fontweight='bold')

# Add the 80% target line
ax.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Target Accuracy (80%)')

# Formatting
ax.set_ylim(0, 100)
ax.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold')
ax.set_title('Figure 5: AI Model Performance Metrics (XGBoost)', fontsize=18, fontweight='bold', pad=20)

# Add grid lines for readability
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

# Legend
ax.legend(fontsize=12, loc='upper right', framealpha=0.9, edgecolor='black')

# Remove top and right spines for a cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_5_Publication_Barchart.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Figure 5 successfully saved to: {out_path}")