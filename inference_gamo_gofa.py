# File: inference_gamo_gofa.py
import torch
import torchvision.models as models
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import config_gamo_gofa as config

class InferenceDataset(Dataset):
    def __init__(self, patch_dir):
        # Sort files to keep them in spatial order if needed
        self.patch_files = sorted(list(patch_dir.glob("*.npy")))
        
    def __len__(self):
        return len(self.patch_files)
    
    def __getitem__(self, idx):
        patch = np.load(self.patch_files[idx])
        rgb_patch = patch[:3, :, :] / 10000.0
        return torch.tensor(rgb_patch, dtype=torch.float32), self.patch_files[idx].name

def run_inference():
    print("--- Starting Gamo-Gofa Inference & Mapping ---")
    
    # 1. Load Data
    dataset = InferenceDataset(config.PROCESSED_DIR)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=False)
    print(f"Loaded {len(dataset)} patches for inference.")
    
    # 2. Load the Newly Trained Model
    print(f"Loading custom model: {config.GAMO_GOFA_OUTPUT_WEIGHTS.name}")
    model = models.resnet18()
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, 5) # Must match the 5 classes from training
    
    model.load_state_dict(torch.load(config.GAMO_GOFA_OUTPUT_WEIGHTS, map_location='cpu'))
    model.eval() # Set to evaluation mode
    
    # 3. Run Predictions
    print("Predicting land cover classes...")
    results = []
    
    # Class names mapping (0: Enset, 1: Maize, 2: Barley, 3: Forest, 4: Other)
    class_names = {0: "Enset", 1: "Maize", 2: "Barley", 3: "Forest", 4: "Other"}
    
    with torch.no_grad():
        for inputs, filenames in dataloader:
            outputs = model(inputs)
            # Get the class with the highest probability
            _, predicted = torch.max(outputs, 1)
            
            for fname, pred_idx in zip(filenames, predicted.numpy()):
                results.append({
                    "Patch_File": fname,
                    "Predicted_Class_ID": int(pred_idx),
                    "Predicted_Class_Name": class_names[int(pred_idx)]
                })
                
    # 4. Save Results
    df = pd.DataFrame(results)
    out_csv = config.OUT_CROP_MAPS / "gamo_gofa_predictions.csv"
    df.to_csv(out_csv, index=False)
    
    print(f"\n[SUCCESS] Inference complete.")
    print(f"Processed {len(df)} patches.")
    print(f"Results saved to: {out_csv}")
    
    # Show a preview of the first 5 predictions
    print("\n--- Sample Predictions ---")
    print(df.head().to_string(index=False))

if __name__ == "__main__":
    run_inference()
