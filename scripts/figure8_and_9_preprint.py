import matplotlib.pyplot as plt
import numpy as np

print("Generating Pre-print Figure 8 (Pie Chart) and Figure 9 (Bar Chart)...")

# ==========================================
# FIGURE 8: LAND COVER PIE CHART
# ==========================================
labels = ['Vegetation', 'Urban / Bare Soil', 'Water Bodies']
sizes = [34.4, 46.6, 19.0]
colors = ['#2ca02c', '#7f7f7f', '#1f77b4']

fig1, ax1 = plt.subplots(figsize=(10, 7))
wedges, texts, autotexts = ax1.pie(
    sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, 
    textprops={'fontsize': 15, 'fontweight': 'bold'},
    wedgeprops={'edgecolor': 'black', 'linewidth': 1.5}
)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(16)

ax1.set_title('AI Land Cover Distribution (Addis Ababa)', fontsize=18, fontweight='bold', pad=20)
ax1.axis('equal')
plt.tight_layout()
out_pie = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_8_Preprint_PieChart.png"
plt.savefig(out_pie, dpi=300, bbox_inches='tight')
print(f"✅ Figure 8 saved to: {out_pie}")
plt.close(fig1)

# ==========================================
# FIGURE 9: ACCURACY METRICS BAR CHART
# ==========================================
metrics = ['Overall Accuracy (OA)', 'Kappa Coefficient (x100)']
scores = [76.67, 54.55]
colors_bar = ['#1f77b4', '#2ca02c']

fig2, ax2 = plt.subplots(figsize=(10, 7))
bars = ax2.bar(metrics, scores, color=colors_bar, width=0.5, edgecolor='black', linewidth=1.5)

for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.2f}%', 
            ha='center', va='bottom', fontsize=16, fontweight='bold')

ax2.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Target Accuracy (80%)')
ax2.set_ylim(0, 100)
ax2.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold')
ax2.set_title('AI Model Performance Metrics (XGBoost)', fontsize=18, fontweight='bold', pad=20)
ax2.yaxis.grid(True, linestyle='--', alpha=0.7)
ax2.set_axisbelow(True)
ax2.legend(fontsize=12, loc='upper right', framealpha=0.9, edgecolor='black')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout()
out_bar = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_9_Preprint_BarChart.png"
plt.savefig(out_bar, dpi=300, bbox_inches='tight')
print(f"✅ Figure 9 saved to: {out_bar}")