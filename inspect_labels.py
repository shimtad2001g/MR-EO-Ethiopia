# File: inspect_labels.py
import os
import glob
import pandas as pd
import geopandas as gpd
import config_gamo_gofa as config

def inspect_files():
    print("--- Inspecting Discovered Ground-Truth Files ---")
    search_dir = config.D_DRIVE_CARBON
    extensions = ["*.csv", "*.gpkg", "*.shp", "*.xlsx"]
    
    found_files = []
    for ext in extensions:
        found_files.extend(glob.glob(os.path.join(search_dir, "**", ext), recursive=True))
        
    found_files = [f for f in found_files if "AfriClimate" not in f and "GamoGofa_AOI" not in f and "Ethiopia_ADM2" not in f]
    
    for i, file_path in enumerate(found_files):
        print(f"\n[{i+1}] File: {os.path.basename(file_path)}")
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=3)
                print(f"    Columns: {list(df.columns)}")
                print(f"    Sample Data:\n{df.to_string(index=False)}")
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, nrows=3)
                print(f"    Columns: {list(df.columns)}")
                print(f"    Sample Data:\n{df.to_string(index=False)}")
            elif file_path.endswith('.gpkg') or file_path.endswith('.shp'):
                gdf = gpd.read_file(file_path, rows=3)
                print(f"    Columns: {list(gdf.columns)}")
                print(f"    Geometry Type: {gdf.geom_type.iloc[0] if not gdf.empty else 'Empty'}")
                print(f"    Sample Data:\n{gdf.drop(columns='geometry').to_string(index=False)}")
        except Exception as e:
            print(f"    [ERROR reading file]: {e}")

if __name__ == "__main__":
    inspect_files()
