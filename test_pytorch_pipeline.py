# File: test_pytorch_pipeline.py
import torch
import torchvision.models as models
import numpy as np
from torch.utils.data import Dataset, DataLoader
import config_gamo_gofa as config

class GamoGofaDataset(Dataset):
    def __init__(self, patch_dir):
        self.patch_files = list(patch_dir.glob("*.npy"))
        
    def __len__(self):
        return len(self.patch_files)
    
    def __getitem__(self, idx):
        # Load the 4-band patch
        patch = np.load(self.patch_files[idx])
        
        # FIX: Slice the first 3 bands (RGB) to match the model's expected input
        rgb_patch = patch[:3, :, :]
        
        # Normalize to 0-1 range (Sentinel-2 data is usually 0-10000)
        rgb_patch = rgb_patch / 10000.0 
        
        # Convert to PyTorch Tensor (Float32)
        tensor_patch = torch.tensor(rgb_patch, dtype=torch.float32)
        
        # For this test, we don't have labels, so we return a dummy label (0)
        return tensor_patch, 0

def test_pipeline():
    print("--- Testing PyTorch Pipeline with Gamo-Gofa Data ---")
    
    # 1. Setup DataLoader
    dataset = GamoGofaDataset(config.PROCESSED_DIR)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)
    print(f"Loaded dataset with {len(dataset)} patches.")
    
    # 2. Instantiate Model (Assuming ResNet18 based on conv1 shape)
    print("Instantiating ResNet18 architecture...")
    model = models.resnet18()
    
    # 3. Load the massive_ssl_weights
    print("Loading massive_ssl_weights.pth...")
    state_dict = torch.load(config.MASSIVE_WEIGHTS, map_location='cpu')
    
    # Load weights (strict=False allows for minor mismatches like the final classification head)
    missing, unexpected = model.load_state_dict(state_dict, strict=False)
    print(f"  -> Missing keys: {len(missing)} (Expected for classification head)")
    print(f"  -> Unexpected keys: {len(unexpected)}")
    
    # 4. Run a Forward Pass
    print("Running forward pass on a batch of Gamo-Gofa data...")
    model.eval()
    with torch.no_grad():
        for inputs, labels in dataloader:
            print(f"  -> Input tensor shape: {inputs.shape}")
            outputs = model(inputs)
            print(f"  -> Output tensor shape: {outputs.shape}")
            print("[SUCCESS] Forward pass completed without errors!")
            break # Just test one batch

if __name__ == "__main__":
    test_pipeline()
