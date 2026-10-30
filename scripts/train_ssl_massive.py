import torch
import torchvision
from torchvision import transforms
from torch.utils.data import DataLoader, Dataset
import rasterio
import numpy as np
import os
import glob
from PIL import Image

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device} (This will take 2-3 hours on CPU)")

class MassivePatchDataset(Dataset):
    def __init__(self, folder_path, transform=None, num_patches=2000):
        self.image_paths = glob.glob(os.path.join(folder_path, '*.tif'))
        self.transform = transform
        self.num_patches = num_patches
        
    def __len__(self):
        return self.num_patches
        
    def __getitem__(self, idx):
        np.random.seed(idx)
        img_path = self.image_paths[np.random.randint(len(self.image_paths))]
        with rasterio.open(img_path) as src:
            w, h = src.width, src.height
            x = np.random.randint(0, w - 224)
            y = np.random.randint(0, h - 224)
            window = rasterio.windows.Window(x, y, 224, 224)
            img = src.read([1, 2, 3], window=window)
            img = np.moveaxis(img, 0, -1)
            img = img.astype(np.float32) / 10000.0
            img = np.clip(img, 0, 1)
        img = Image.fromarray((img * 255).astype(np.uint8))
        if self.transform:
            return self.transform(img), self.transform(img)

transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4),
    transforms.ToTensor()
])

data_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\SSL_Large_Patches"
dataset = MassivePatchDataset(data_path, transform=transform, num_patches=2000)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True, drop_last=True)

backbone = torchvision.models.resnet18(weights=None)
backbone.fc = torch.nn.Identity() 
model = backbone.to(device)

class ProjectionHead(torch.nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.layer = torch.nn.Sequential(
            torch.nn.Linear(in_dim, in_dim), torch.nn.ReLU(), torch.nn.Linear(in_dim, out_dim))
    def forward(self, x): return self.layer(x)

projection_head = ProjectionHead(512, 128).to(device)
optimizer = torch.optim.Adam(list(model.parameters()) + list(projection_head.parameters()), lr=1e-3)
criterion = torch.nn.CrossEntropyLoss()

print("Starting Local MASSIVE SSL Pre-training...")
epochs = 30
for epoch in range(epochs):
    total_loss = 0
    for view1, view2 in dataloader:
        view1, view2 = view1.to(device), view2.to(device)
        optimizer.zero_grad()
        
        z1 = projection_head(model(view1))
        z2 = projection_head(model(view2))
        z1 = torch.nn.functional.normalize(z1, dim=1)
        z2 = torch.nn.functional.normalize(z2, dim=1)
        
        representations = torch.cat([z1, z2], dim=0)
        similarity_matrix = torch.matmul(representations, representations.T)
        
        batch_size = view1.size(0)
        labels = torch.cat([torch.arange(batch_size) for i in range(2)], dim=0)
        labels = (labels.unsqueeze(0) == labels.unsqueeze(1)).float().to(device)
        similarity_matrix = similarity_matrix / 0.5 
        
        loss = criterion(similarity_matrix, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        
    print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}")

out_weights = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\massive_ssl_weights.pth"
torch.save(model.state_dict(), out_weights)
print(f"✅ Massive Training Complete! Weights saved to {out_weights}")