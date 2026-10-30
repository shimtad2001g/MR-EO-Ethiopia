import numpy as np
import config_gamo_gofa as config

patch_files = list(config.PROCESSED_DIR.glob("*.npy"))
if patch_files:
    sample = np.load(patch_files[0])
    print(f"Patch Shape: {sample.shape}")
    if sample.shape[0] == 13:
        print("[SUCCESS] The patches have 13 bands! We are ready for Model Surgery.")
    else:
        print(f"[WARNING] The patches only have {sample.shape[0]} bands. The 13-band download likely failed.")
else:
    print("[ERROR] No patches found.")
