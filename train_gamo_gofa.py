# File: train_gamo_gofa.py
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import config_gamo_gofa as config

class GamoGofaDataset(Dataset):
    def __init__(self, patch_dir, label_csv):
        self.patch_files = list(patch_dir.glob("*.npy"))
        self.labels_df = pd.read_csv(label_csv)
        self.label_dict = dict(zip(self.labels_df['Patch_File'], self.labels_df['Pseudo_Label']))
        
    def __len__(self):
        return len(self.patch_files)
    
    def __getitem__(self, idx):
        patch_path = self.patch_files[idx]
        patch = np.load(patch_path)
        rgb_patch = patch[:3, :, :] / 10000.0
        label = self.label_dict.get(patch_path.name, 0) # Default to 0 if missing
        return torch.tensor(rgb_patch, dtype=torch.float32), torch.tensor(label, dtype=torch.long)

def fine_tune():
    print("--- Starting Gamo-Gofa Model Training (10 Epochs) ---")
    
    label_csv = config.OUT_CROP_MAPS / "pseudo_labels.csv"
    dataset = GamoGofaDataset(config.PROCESSED_DIR, label_csv)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    model = models.resnet18()
    state_dict = torch.load(config.MASSIVE_WEIGHTS, map_location='cpu')
    model.load_state_dict(state_dict, strict=False)
    
    # Replace head for 5 classes
    model.fc = nn.Linear(model.fc.in_features, 5)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    epochs = 10
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
        epoch_loss = running_loss / len(dataloader)
        accuracy = 100 * correct / total
        print(f"Epoch {epoch+1}/{epochs} | Loss: {epoch_loss:.4f} | Accuracy: {accuracy:.2f}%")
        
    print(f"\n[SUCCESS] Training complete. Saving model...")
    torch.save(model.state_dict(), config.GAMO_GOFA_OUTPUT_WEIGHTS)
    print(f"Saved to: {config.GAMO_GOFA_OUTPUT_WEIGHTS}")

if __name__ == "__main__":
    fine_tune()
