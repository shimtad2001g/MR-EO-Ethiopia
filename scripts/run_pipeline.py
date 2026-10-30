import subprocess
import time

# The sequence of scripts to run
pipeline_steps = [
    "scripts\\harmonize.py",
    "scripts\\geoai_model.py",
    "scripts\\validate_model.py",
    "scripts\\visual_check.py"
]

print("==================================================")
print("🚀 STARTING MR-EO ETHIOPIA GEO-AI PIPELINE")
print("==================================================\n")

start_time = time.time()

for step in pipeline_steps:
    print(f"▶️ Running: {step} ...")
    
    # Run the script using the same Python executable
    result = subprocess.run(["python", step], capture_output=False, text=True)
    
    if result.returncode == 0:
        print(f"✅ Finished {step} successfully.\n")
    else:
        print(f"❌ ERROR in {step}. Pipeline aborted.")
        break

end_time = time.time()
print("==================================================")
print(f"🏁 PIPELINE COMPLETE in {end_time - start_time:.2f} seconds!")
print("Check your 'outputs' folder for the final classified map and visual comparison.")
print("==================================================")