# File: train_12band_carbon.py
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import config_gamo_gofa as config

class Dataset12Bands(Dataset):
    def __init__(self, patch_dir, label_csv):
        self.patch_files = list(patch_dir.glob("*.npy"))
        self.labels_df = pd.read_csv(label_csv)
        self.label_dict = dict(zip(self.labels_df['Patch_File'], self.labels_df['Carbon_AGBD']))
        
    def __len__(self):
        return len(self.patch_files)
    
    def __getitem__(self, idx):
        patch_path = self.patch_files[idx]
        patch = np.load(patch_path)
        
        # Normalize all 12 bands (Sentinel-2 data is 0-10000)
        all_bands = patch / 10000.0 
        
        label = self.label_dict.get(patch_path.name, 0.0)
        return torch.tensor(all_bands, dtype=torch.float32), torch.tensor([label], dtype=torch.float32)

def perform_model_surgery(model):
    print("--- Performing Model Surgery (3 Bands -> 12 Bands) ---")
    original_conv1 = model.conv1
    
    # Create a new Convolutional layer expecting 12 input channels
    new_conv1 = nn.Conv2d(12, 64, kernel_size=7, stride=2, padding=3, bias=False)
    
    # Copy the original RGB weights into the new channels
    with torch.no_grad():
        new_conv1.weight[:, 0:3, :, :] = original_conv1.weight
        new_conv1.weight[:, 3:6, :, :] = original_conv1.weight
        new_conv1.weight[:, 6:9, :, :] = original_conv1.weight
        new_conv1.weight[:, 9:12, :, :] = original_conv1.weight
        
    model.conv1 = new_conv1
    print("Successfully upgraded conv1 to accept 12 bands!")
    return model

def train():
    print("--- Starting 12-Band Carbon Regression Training ---")
    
    label_csv = config.OUT_CARBON_MAPS / "carbon_labels.csv"
    dataset = Dataset12Bands(config.PROCESSED_DIR, label_csv)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    model = models.resnet18()
    state_dict = torch.load(config.MASSIVE_WEIGHTS, map_location='cpu')
    model.load_state_dict(state_dict, strict=False)
    
    # Perform the surgery!
    model = perform_model_surgery(model)
    
    # Replace regression head
    model.fc = nn.Linear(model.fc.in_features, 1)
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    epochs = 10
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for inputs, labels in dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        epoch_loss = running_loss / len(dataloader)
        rmse = np.sqrt(epoch_loss)
        print(f"Epoch {epoch+1}/{epochs} | 12-Band MSE Loss: {epoch_loss:.2f} | RMSE: {rmse:.2f} tons/ha")
        
    out_weights = config.BASE_DIR / "gamo_gofa_12band_carbon.pth"
    torch.save(model.state_dict(), out_weights)
    print(f"\n[SUCCESS] 12-Band Model saved to: {out_weights}")

if __name__ == "__main__":
    train()
