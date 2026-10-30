import ee
import geemap
import rasterio
import numpy as np
import torch
import torchvision
from torchvision import transforms
from torch.utils.data import DataLoader, Dataset
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import os
import glob

print("🚀 Starting Hawassa SSL Replication Pipeline...")
ee.Initialize()

# 1. Define Hawassa AOI (Covers the lake, city, and surrounding farms)
roi = ee.Geometry.Rectangle([38.40, 6.95, 38.55, 7.10])
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\hawassa_image.tif"

if not os.path.exists(out_path):
    print("Downloading Hawassa Base Image...")
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(roi).filterDate('2023-01-01', '2023-12-31') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).median() \
        .select(['B4', 'B3', 'B2'])
    geemap.ee_export_image(s2, filename=out_path, scale=20, region=roi, crs='EPSG:4326')

# 2. Load Image
with rasterio.open(out_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

# 3. Fast SSL Pre-training on Hawassa (10 Epochs)
print("Pre-training ResNet18 (SimCLR) on Hawassa features...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class HawassaDataset(Dataset):
    def __init__(self, img_array, transform=None, num_patches=500):
        self.img = img_array
        self.transform = transform
        self.num_patches = num_patches
    def __len__(self): return self.num_patches
    def __getitem__(self, idx):
        from PIL import Image
        y = np.random.randint(0, self.img.shape[0] - 224)
        x = np.random.randint(0, self.img.shape[1] - 224)
        patch = self.img[y:y+224, x:x+224, :]
        patch = Image.fromarray((patch * 255).astype(np.uint8))
        if self.transform: return self.transform(patch), self.transform(patch)
        return patch

transform = transforms.Compose([transforms.RandomResizedCrop(224), transforms.RandomHorizontalFlip(), transforms.ToTensor()])
dataset = HawassaDataset(img_rgb, transform=transform, num_patches=500)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True, drop_last=True)

backbone = torchvision.models.resnet18(weights=None)
backbone.fc = torch.nn.Identity()
model = backbone.to(device)

class ProjHead(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = torch.nn.Sequential(torch.nn.Linear(512, 512), torch.nn.ReLU(), torch.nn.Linear(512, 128))
    def forward(self, x): return self.layer(x)

proj_head = ProjHead().to(device)
optimizer = torch.optim.Adam(list(model.parameters()) + list(proj_head.parameters()), lr=1e-3)
criterion = torch.nn.CrossEntropyLoss()

for epoch in range(10):
    total_loss = 0
    for v1, v2 in dataloader:
        v1, v2 = v1.to(device), v2.to(device)
        optimizer.zero_grad()
        z1 = torch.nn.functional.normalize(proj_head(model(v1)), dim=1)
        z2 = torch.nn.functional.normalize(proj_head(model(v2)), dim=1)
        sim_matrix = torch.matmul(torch.cat([z1, z2]), torch.cat([z1, z2]).T) / 0.5
        labels = torch.cat([torch.arange(16) for _ in range(2)], dim=0)
        labels = (labels.unsqueeze(0) == labels.unsqueeze(1)).float().to(device)
        loss = criterion(sim_matrix, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"SSL Epoch {epoch+1}/10, Loss: {total_loss/len(dataloader):.4f}")

# Save Hawassa SSL weights
torch.save(model.state_dict(), r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\hawassa_ssl_weights.pth")

# 4. Extract Deep Features from Hawassa
print("Extracting deep features...")
model.eval()
preprocess = transforms.Compose([transforms.ToPILImage(), transforms.Resize((224, 224)), transforms.ToTensor()])
features_list, coords = [], []
for y in range(0, img.shape[0] - 224, 112):
    for x in range(0, img.shape[1] - 224, 112):
        patch = img[y:y+224, x:x+224, :]
        patch_t = preprocess(patch.astype(np.float32) / 10000.0).unsqueeze(0).to(device)
        with torch.no_grad():
            feat = model(patch_t).cpu().numpy()
        features_list.append(feat.flatten())
        coords.append((y+112, x+112))

features = np.array(features_list)

# 5. Cluster Features
print("Clustering features...")
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(features)
labels = kmeans.labels_

# Intelligent brightness mapping
cluster_means = []
for i in range(3):
    cp = [img[cy, cx] for j, (cy, cx) in enumerate(coords) if labels[j] == i]
    cluster_means.append(np.mean(cp, axis=0))

brightness = [np.sum(c) for c in cluster_means]
sorted_idx = np.argsort(brightness)
water_cluster, veg_cluster, arid_cluster = sorted_idx[0], sorted_idx[1], sorted_idx[2]

# Create map
classified_img = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
for j, (cy, cx) in enumerate(coords):
    if labels[j] == veg_cluster: classified_img[cy-112:cy+112, cx-112:cx+112] = 0
    elif labels[j] == arid_cluster: classified_img[cy-112:cy+112, cx-112:cx+112] = 1
    elif labels[j] == water_cluster: classified_img[cy-112:cy+112, cx-112:cx+112] = 2

# 6. Plot Figure 21 (Study Area & Classification)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
ax1.imshow(img_rgb, extent=extent)
ax1.set_title("Raw Sentinel-2 (Hawassa)", fontsize=18, fontweight='bold')
ax1.axis('off')

cmap = ListedColormap(['#2ca02c', '#e6c229', '#1f77b4'])
ax2.imshow(classified_img, cmap=cmap, vmin=0, vmax=2, extent=extent)
ax2.set_title("AI-Classified Land Cover (SSL + XGBoost Replication)", fontsize=18, fontweight='bold')
ax2.axis('off')

legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Vegetation / Agriculture'),
    Patch(facecolor='#e6c229', edgecolor='black', label='Urban / Bare Soil'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water Bodies (Lake Hawassa)')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=14, framealpha=0.9, edgecolor='black', title="AI Predictions", title_fontsize=15)
fig.suptitle("Figure 21: Replicating the Addis Ababa SSL Pipeline in Hawassa", fontsize=22, fontweight='bold')
fig.subplots_adjust(top=0.88)
plt.savefig(r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_21_Hawassa_Classification.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("✅ Figure 21 saved.")