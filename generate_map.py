import os
import glob
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
from matplotlib.patches import Patch

directory = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia"

# Search recursively (**) for common geospatial raster formats
extensions = ['*.tif', '*.tiff', '*.jp2', '*.img', '*.nc', '*.dat']
files = []
for ext in extensions:
    files.extend(glob.glob(os.path.join(directory, "**", ext), recursive=True))

if not files:
    print("Error: Still no raster files found. Please check the folder contents.")
    print("Files currently in the directory:", os.listdir(directory))
else:
    # Process the first valid raster file found
    image_path = files[0]
    print(f"Generating map from: {image_path}")
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    with rasterio.open(image_path) as src:
        # Try reading standard Sentinel-2 True Color (B4, B3, B2). Fallback to RGB (1,2,3)
        try:
            if src.count >= 4:
                rgb = src.read([4, 3, 2]) 
            else:
                rgb = src.read([1, 2, 3])
        except:
            rgb = src.read([1, 2, 3])
            
        # Plot the raster
        show(rgb, transform=src.transform, ax=ax, adjust='linear')
        
        # Add the exact title from your screenshot
        ax.set_title("Study Area: Addis Ababa (Urban), Ethiopia\nSentinel-2 True Color Composite", 
                     fontsize=16, fontweight='bold', pad=15)
        
        # Add axis labels
        ax.set_xlabel("Longitude (°E)", fontsize=12, fontweight='bold')
        ax.set_ylabel("Latitude (°N)", fontsize=12, fontweight='bold')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.5)

    # Add the custom legend exactly as shown in your screenshot
    legend_elements = [
        Patch(facecolor='red', label='Band 4 (Red)'),
        Patch(facecolor='green', label='Band 3 (Green)'),
        Patch(facecolor='blue', label='Band 2 (Blue)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', title='Sentinel-2 Bands', title_fontsize='13', fontsize='11')

    # Save as a high-resolution PNG (300 DPI for publication) in the main folder
    output_path = os.path.join(directory, "Figure_1_Study_Area_Map.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Success! High-resolution map saved to: {output_path}")
