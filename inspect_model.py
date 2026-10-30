# File: inspect_model.py
import torch
import numpy as np
import os
import config_gamo_gofa as config

def inspect():
    print("--- Inspecting Gamo-Gofa Pipeline Assets ---")
    
    # 1. Check the Patches
    patch_files = list(config.PROCESSED_DIR.glob("*.npy"))
    if patch_files:
        sample_patch = np.load(patch_files[0])
        print(f"\n[PATCH INFO]")
        print(f"Total patches generated: {len(patch_files)}")
        print(f"Shape of a single patch: {sample_patch.shape} (Bands, Height, Width)")
    else:
        print("[WARNING] No patches found.")

    # 2. Check the Model Weights
    print(f"\n[MODEL INFO]")
    if not config.MASSIVE_WEIGHTS.exists():
        print(f"[ERROR] Weights file not found: {config.MASSIVE_WEIGHTS}")
        return

    try:
        # Load weights to CPU to avoid CUDA memory errors during inspection
        checkpoint = torch.load(config.MASSIVE_WEIGHTS, map_location=torch.device('cpu'))
        
        # Sometimes weights are saved inside a dictionary (e.g., checkpoint['state_dict'])
        if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
            print("Found weights inside 'state_dict' key.")
        elif isinstance(checkpoint, dict) and 'model' in checkpoint:
            state_dict = checkpoint['model']
            print("Found weights inside 'model' key.")
        else:
            state_dict = checkpoint
            print("Weights loaded directly as a state_dict.")

        # Print the first 5 keys to understand the architecture
        print("\nFirst 5 layers in the model:")
        keys = list(state_dict.keys())[:5]
        for k in keys:
            print(f"  -> {k} | Shape: {state_dict[k].shape}")
            
        # Try to find the input convolution layer to see how many bands it expects
        for k in state_dict.keys():
            if 'patch_embed' in k or 'conv1' in k or 'stem' in k:
                if len(state_dict[k].shape) == 4: # Conv layer (out, in, h, w)
                    print(f"\n[CRITICAL INFO] Input layer '{k}' expects {state_dict[k].shape[1]} input bands.")
                    break
                    
    except Exception as e:
        print(f"[ERROR] Failed to load weights: {e}")

if __name__ == "__main__":
    inspect()
