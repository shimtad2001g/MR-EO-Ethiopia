# File: train_carbon_regression.py
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import config_gamo_gofa as config

class CarbonDataset(Dataset):
    def __init__(self, patch_dir, label_csv):
        self.patch_files = list(patch_dir.glob("*.npy"))
        self.labels_df = pd.read_csv(label_csv)
        self.label_dict = dict(zip(self.labels_df['Patch_File'], self.labels_df['Carbon_AGBD']))
        
    def __len__(self):
        return len(self.patch_files)
    
    def __getitem__(self, idx):
        patch_path = self.patch_files[idx]
        patch = np.load(patch_path)
        rgb_patch = patch[:3, :, :] / 10000.0
        
        # Label is now a continuous float (Carbon value)
        label = self.label_dict.get(patch_path.name, 0.0)
        return torch.tensor(rgb_patch, dtype=torch.float32), torch.tensor([label], dtype=torch.float32)

def train_regression():
    print("--- Starting Carbon Regression Training ---")
    
    label_csv = config.OUT_CARBON_MAPS / "carbon_labels.csv"
    dataset = CarbonDataset(config.PROCESSED_DIR, label_csv)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    # Load Base Model
    model = models.resnet18()
    state_dict = torch.load(config.MASSIVE_WEIGHTS, map_location='cpu')
    model.load_state_dict(state_dict, strict=False)
    
    # Replace head for REGRESSION (1 output node)
    model.fc = nn.Linear(model.fc.in_features, 1)
    
    # Use Mean Squared Error Loss for regression
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
        # Note: MSE Loss is in squared units. RMSE is easier to interpret.
        rmse = np.sqrt(epoch_loss)
        print(f"Epoch {epoch+1}/{epochs} | MSE Loss: {epoch_loss:.2f} | RMSE: {rmse:.2f} tons/ha")
        
    # Save the Regression Model
    out_weights = config.BASE_DIR / "gamo_gofa_carbon_regression.pth"
    torch.save(model.state_dict(), out_weights)
    print(f"\n[SUCCESS] Carbon Regression model saved to: {out_weights}")

if __name__ == "__main__":
    train_regression()
