import torch
import torchvision
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from sklearn.cluster import KMeans
from torchvision import transforms

print("Generating Smooth, High-Resolution AI Map for Awash Basin...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the model
model = torchvision.models.resnet18(weights=None)
model.fc = torch.nn.Identity()
weights_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\ssl_backbone_weights.pth"
model.load_state_dict(torch.load(weights_path, map_location=device))
model = model.to(device)
model.eval()

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\awash_image.tif"
with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)

preprocess = transforms.Compose([transforms.ToPILImage(), transforms.Resize((224, 224)), transforms.ToTensor()])

# We will use a much smaller stride to make the map smooth
patch_size = 224
stride = 32 
features_list = []
coords = []

print("Extracting features (this will take 2-3 minutes on CPU)...")
for y in range(0, img.shape[0] - patch_size, stride):
    for x in range(0, img.shape[1] - patch_size, stride):
        patch = img[y:y+patch_size, x:x+patch_size, :]
        patch_tensor = preprocess(patch.astype(np.float32) / 10000.0).unsqueeze(0).to(device)
        with torch.no_grad():
            feature = model(patch_tensor).cpu().numpy()
        features_list.append(feature.flatten())
        coords.append((y, x))

features = np.array(features_list)

# Cluster features
print(f"Clustering {len(features)} overlapping patches...")
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(features)
labels = kmeans.labels_

# Create a classified image (start with a blank canvas)
classified_img = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)

# Paint the patches onto the canvas
for i, (y, x) in enumerate(coords):
    # For the center of the patch, assign the label
    classified_img[y+112:y+112+stride, x+112:x+112+stride] = labels[i]

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

# Raw Image
p2, p98 = np.percentile(img, (2, 98))
raw_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)
ax1.imshow(raw_rgb)
ax1.set_title("Raw Sentinel-2 (Awash Basin)", fontsize=18, fontweight='bold')
ax1.axis('off')

# Classified Map
# Colors: 0=Green(Agri), 1=Yellow(Arid), 2=Blue(Water)
cmap = ListedColormap(['#2ca02c', '#e6c229', '#1f77b4'])
ax2.imshow(classified_img, cmap=cmap, vmin=0, vmax=2)
ax2.set_title("AI-Classified Land Cover (High-Resolution)", fontsize=18, fontweight='bold')
ax2.axis('off')

# Legend
legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Vegetation / Agriculture'),
    Patch(facecolor='#e6c229', edgecolor='black', label='Arid / Bare Soil'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water Bodies (Koka Reservoir)')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=14, 
           framealpha=0.9, edgecolor='black', title="AI Predictions", title_fontsize=15)

fig.suptitle("Visual Comparison of AI Classification (Awash Basin)", fontsize=22, fontweight='bold')
fig.subplots_adjust(top=0.88)

out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_5_Awash_Smooth_Map.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Smooth Awash Map saved to: {out_img}")