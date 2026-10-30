# File: inference_12band.py
import torch
import torchvision.models as models
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import config_gamo_gofa as config
import torch.nn as nn

class Dataset12Bands(Dataset):
    def __init__(self, patch_dir):
        self.patch_files = sorted(list(patch_dir.glob("*.npy")))
        
    def __len__(self):
        return len(self.patch_files)
    
    def __getitem__(self, idx):
        patch = np.load(self.patch_files[idx])
        all_bands = patch / 10000.0
        return torch.tensor(all_bands, dtype=torch.float32), self.patch_files[idx].name

def run_inference():
    print("--- Starting 12-Band Carbon Inference ---")
    dataset = Dataset12Bands(config.PROCESSED_DIR)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=False)
    
    model = models.resnet18()
    # Perform surgery to match the saved 12-band weights
    model.conv1 = nn.Conv2d(12, 64, kernel_size=7, stride=2, padding=3, bias=False)
    model.fc = nn.Linear(model.fc.in_features, 1)
    
    weights_path = config.BASE_DIR / "gamo_gofa_12band_carbon.pth"
    print(f"Loading model: {weights_path.name}")
    model.load_state_dict(torch.load(weights_path, map_location='cpu'))
    model.eval()
    
    results = []
    with torch.no_grad():
        for inputs, filenames in dataloader:
            outputs = model(inputs)
            for fname, pred_val in zip(filenames, outputs.numpy()):
                results.append({
                    "Patch_File": fname,
                    "Predicted_Carbon_AGBD": float(pred_val[0])
                })
                
    df = pd.DataFrame(results)
    out_csv = config.OUT_CARBON_MAPS / "carbon_predictions_12band.csv"
    df.to_csv(out_csv, index=False)
    print(f"[SUCCESS] Predictions saved to: {out_csv}")
    print(df.head().to_string(index=False))

if __name__ == "__main__":
    run_inference()
