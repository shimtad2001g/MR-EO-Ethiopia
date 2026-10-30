# File: extract_real_labels.py
import os
import glob
import pandas as pd
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import rowcol
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models
from torch.utils.data import Dataset, DataLoader
import config_gamo_gofa as config

# --- 1. Find and Match Coordinates to Patches ---
def extract_labels():
    print("--- Scanning D: Drive for Ground-Truth Data ---")
    search_dir = config.D_DRIVE_CARBON
    extensions = ["*.csv", "*.gpkg", "*.shp", "*.xlsx"]
    
    found_files = []
    for ext in extensions:
        found_files.extend(glob.glob(os.path.join(search_dir, "**", ext), recursive=True))
        
    # Filter out irrelevant files
    found_files = [f for f in found_files if "AfriClimate" not in f and "GamoGofa_AOI" not in f and "Ethiopia_ADM2" not in f]
    
    if not found_files:
        print("[ERROR] No potential training files found.")
        return False

    print(f"Found {len(found_files)} potential files. Inspecting...")
    
    # Get the geospatial transform of our image
    original_tif = config.RAW_S2_DIR / "gamo_gofa_sample_s2.tif"
    with rasterio.open(original_tif) as src:
        transform = src.transform
        img_height = src.height
        img_width = src.width

    for file_path in found_files:
        try:
            df = None
            # Read file based on extension
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.gpkg') or file_path.endswith('.shp'):
                gdf = gpd.read_file(file_path)
                gdf = gdf.to_crs(epsg=4326)
                df = pd.DataFrame({
                    'lon': gdf.geometry.x,
                    'lat': gdf.geometry.y,
                    'label': gdf.iloc[:, 0]
                })
            
            if df is None: 
                continue

            # Auto-detect coordinate columns
            lat_col = next((c for c in df.columns if c.lower() in ['lat', 'latitude', 'y']), None)
            lon_col = next((c for c in df.columns if c.lower() in ['lon', 'longitude', 'x']), None)
            label_col = next((c for c in df.columns if c.lower() in ['label', 'class', 'lulc', 'crop', 'type']), None)

            if lat_col and lon_col and label_col:
                print(f"[SUCCESS] Found valid training data in: {os.path.basename(file_path)}")
                print(f"  -> Using columns: {lon_col}, {lat_col}, {label_col}")
                
                # Match to patches
                matched_data = []
                for _, row in df.iterrows():
                    try:
                        # Calculate pixel coordinates from lat/lon
                        row_idx, col_idx = rowcol(transform, row[lon_col], row[lat_col])
                        
                        # Ensure it falls within our image bounds
                        if 0 <= row_idx < img_height and 0 <= col_idx < img_width:
                            patch_row = row_idx // config.PATCH_SIZE
                            patch_col = col_idx // config.PATCH_SIZE
                            patches_per_row = img_width // config.PATCH_SIZE
                            patch_idx = (patch_row * patches_per_row) + patch_col
                            
                            patch_name = f"gamo_gofa_sample_s2_patch_{patch_idx}.npy"
                            
                            # Map string labels to integers (0-4)
                            label_str = str(row[label_col]).lower()
                            if 'enset' in label_str: l_id = 0
                            elif 'maize' in label_str: l_id = 1
                            elif 'barley' in label_str: l_id = 2
                            elif 'forest' in label_str: l_id = 3
                            else: l_id = 4
                            
                            matched_data.append({'Patch_File': patch_name, 'Real_Label': l_id})
                    except Exception:
                        pass # Skip individual bad points
                
                if matched_data:
                    df_out = pd.DataFrame(matched_data).drop_duplicates(subset=['Patch_File'])
                    out_csv = config.OUT_CROP_MAPS / "real_labels.csv"
                    df_out.to_csv(out_csv, index=False)
                    print(f"[SUCCESS] Extracted {len(df_out)} real labels and saved to {out_csv.name}")
                    return True
        except Exception as e:
            pass # Ignore files that fail to load completely
            
    print("[WARNING] Could not automatically extract labels. Please check your D: drive files manually.")
    return False

# --- 2. PyTorch Dataset using Real Labels ---
class RealGamoDataset(Dataset):
    def __init__(self, patch_dir, label_csv):
        self.patch_files = list(patch_dir.glob("*.npy"))
        self.labels_df = pd.read_csv(label_csv)
        self.label_dict = dict(zip(self.labels_df['Patch_File'], self.labels_df['Real_Label']))
        
    def __len__(self):
        return len(self.patch_files)
    
    def __getitem__(self, idx):
        patch_path = self.patch_files[idx]
        patch = np.load(patch_path)
        rgb_patch = patch[:3, :, :] / 10000.0
        label = self.label_dict.get(patch_path.name, -1) # -1 for unlabelled
        return torch.tensor(rgb_patch, dtype=torch.float32), torch.tensor(label, dtype=torch.long)

# --- 3. Retrain with Real Labels ---
def train_real():
    print("\n--- Retraining Model with Real Ground-Truth Labels ---")
    label_csv = config.OUT_CROP_MAPS / "real_labels.csv"
    
    if not label_csv.exists():
        print("[ERROR] real_labels.csv not found. Skipping training.")
        return

    dataset = RealGamoDataset(config.PROCESSED_DIR, label_csv)
    valid_indices = [i for i in range(len(dataset)) if dataset[i][1] != -1]
    
    if len(valid_indices) == 0:
        print("[ERROR] No valid labeled patches found in the image bounds.")
        return
        
    print(f"Training on {len(valid_indices)} labeled patches...")
    subset = torch.utils.data.Subset(dataset, valid_indices)
    dataloader = DataLoader(subset, batch_size=4, shuffle=True)
    
    model = models.resnet18()
    state_dict = torch.load(config.MASSIVE_WEIGHTS, map_location='cpu')
    model.load_state_dict(state_dict, strict=False)
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
        print(f"Epoch {epoch+1}/{epochs} | Real Label Loss: {epoch_loss:.4f} | Accuracy: {accuracy:.2f}%")
        
    torch.save(model.state_dict(), config.GAMO_GOFA_OUTPUT_WEIGHTS)
    print(f"\n[SUCCESS] Real-world model saved to: {config.GAMO_GOFA_OUTPUT_WEIGHTS}")

if __name__ == "__main__":
    success = extract_labels()
    if success:
        train_real()
