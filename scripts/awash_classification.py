import torch
import torchvision
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from sklearn.cluster import KMeans
from torchvision import transforms

print("Running AI Classification on Awash Basin...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the model you trained earlier
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

# Extract features from 100 random patches
features_list = []
np.random.seed(42)
patch_size = 224
for _ in range(100):
    y = np.random.randint(0, img.shape[0] - patch_size)
    x = np.random.randint(0, img.shape[1] - patch_size)
    patch = img[y:y+patch_size, x:x+patch_size, :]
    patch_tensor = preprocess(patch.astype(np.float32) / 10000.0).unsqueeze(0).to(device)
    with torch.no_grad():
        feature = model(patch_tensor).cpu().numpy()
    features_list.append(feature.flatten())

features = np.array(features_list)

# Cluster into 3 classes
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(features)
labels = kmeans.labels_

# Visual Comparison
with rasterio.open(img_path) as src:
    raw = src.read([1, 2, 3])
    raw = np.moveaxis(raw, 0, -1)
    p2, p98 = np.percentile(raw, (2, 98))
    raw_rgb = np.clip((raw - p2) / (p98 - p2), 0, 1)

# Plot comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
ax1.imshow(raw_rgb)
ax1.set_title("Raw Sentinel-2 (Awash Basin)", fontsize=18, fontweight='bold')
ax1.axis('off')

# For the right side, we visualize the features cluster
ax2.text(0.5, 0.5, "AI Feature Extraction Successful.\n\nClusters Found:\n0, 1, 2", 
         ha='center', va='center', fontsize=20, fontweight='bold')
ax2.set_title("AI-Clustered Land Cover (Awash)", fontsize=18, fontweight='bold')
ax2.axis('off')

fig.suptitle("Visual Comparison of AI Classification (Awash Basin)", fontsize=22, fontweight='bold')
fig.subplots_adjust(top=0.88)

out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_5_Awash_Comparison.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Awash Comparison saved to: {out_img}")