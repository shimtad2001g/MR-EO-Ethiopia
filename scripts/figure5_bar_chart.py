import matplotlib.pyplot as plt
import numpy as np

print("Generating Figure 5: Accuracy Bar Chart...")

metrics = ['Overall Accuracy (OA)', 'Kappa Coefficient']
scores = [76.67, 54.55] # Kappa is multiplied by 100 for visual scaling
colors = ['#2ca02c', '#1f77b4']

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(metrics, scores, color=colors, width=0.5)

# Add text annotations on top of bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval}%', 
            ha='center', va='bottom', fontsize=14, fontweight='bold')

ax.set_ylim(0, 100)
ax.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold')
ax.set_title('Figure 5: AI Model Performance Metrics (XGBoost)', fontsize=16, fontweight='bold')
ax.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Target Accuracy (80%)')
ax.legend()

plt.tight_layout()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_5_Accuracy_Chart.png"
plt.savefig(out_path, dpi=300)
print(f"✅ Figure 5 saved to: {out_path}")