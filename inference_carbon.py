# File: inference_carbon.py
import torch
import torchvision.models as models
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import config_gamo_gofa as config

class CarbonInferenceDataset(Dataset):
    def __init__(self, patch_dir):
        self.patch_files = sorted(list(patch_dir.glob("*.npy")))
        
    def __len__(self):
        return len(self.patch_files)
    
    def __getitem__(self, idx):
        patch = np.load(self.patch_files[idx])
        rgb_patch = patch[:3, :, :] / 10000.0
        return torch.tensor(rgb_patch, dtype=torch.float32), self.patch_files[idx].name

def run_inference():
    print("--- Starting Carbon Inference ---")
    dataset = CarbonInferenceDataset(config.PROCESSED_DIR)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=False)
    
    model = models.resnet18()
    model.fc = torch.nn.Linear(model.fc.in_features, 1) # 1 output for regression
    
    weights_path = config.BASE_DIR / "gamo_gofa_carbon_regression.pth"
    print(f"Loading model: {weights_path.name}")
    if not weights_path.exists():
        print(f"[ERROR] Model weights not found at {weights_path}")
        return
        
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
    out_csv = config.OUT_CARBON_MAPS / "carbon_predictions.csv"
    df.to_csv(out_csv, index=False)
    print(f"[SUCCESS] Carbon predictions saved to: {out_csv}")
    print(df.head().to_string(index=False))

if __name__ == "__main__":
    run_inference()
