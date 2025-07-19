import os
import glob
import subprocess
import re
import shutil

# === Config ===
openface_exe = r"OpenFace\FeatureExtraction.exe"  # Adjust path if needed
input_dir    = "recording_dump"

# === Determine output root from logs/current_folder.txt ===
logs_dir = "logs"
config_file = os.path.join(logs_dir, "current_folder.txt")
if not os.path.exists(config_file):
    raise FileNotFoundError(f"Configuration file not found: {config_file}")
with open(config_file, 'r') as f:
    folder_name = f.read().strip()

output_root = os.path.join(logs_dir, folder_name)
csv_dir     = os.path.join(output_root, "csv_dump")
non_csv_dir = os.path.join(output_root, "not_csv_dump")
base_outname = "post_movie"

# === Prepare folders ===
os.makedirs(csv_dir, exist_ok=True)
os.makedirs(non_csv_dir, exist_ok=True)

# === Helper: Extract index from recording filename ===
def extract_index(filename):
    match = re.search(r"recording_(\d+)\.avi", filename)
    return int(match.group(1)) if match else None

# === Get already processed indices from csv_dir ===
existing_csvs = glob.glob(os.path.join(csv_dir, f"{base_outname}_*.csv"))
existing_indices = {
    int(re.search(r"_(\d+)\.csv", os.path.basename(f)).group(1))
    for f in existing_csvs if re.search(r"_(\d+)\.csv", os.path.basename(f))
}

# === Process recordings ===
recordings = sorted(glob.glob(os.path.join(input_dir, "recording_*.avi")))

for recording in recordings:
    idx = extract_index(recording)
    if idx is None or idx in existing_indices:
        continue  # skip if already processed or index missing

    out_csv_name = f"{base_outname}_{idx}.csv"
    print(f"Processing {recording} → {out_csv_name}")

    # Run OpenFace and store outputs in a temp dir first
    temp_output_dir = os.path.join(output_root, f"__temp_{idx}")
    os.makedirs(temp_output_dir, exist_ok=True)

    cmd = [
        openface_exe,
        "-f", recording,
        "-out_dir", temp_output_dir,
        "-of", out_csv_name
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to process {recording}: {e}")
        shutil.rmtree(temp_output_dir)
        continue

    # Move .csv to csv_dir and other files to non_csv_dir
    for item in os.listdir(temp_output_dir):
        src = os.path.join(temp_output_dir, item)
        if item.endswith(".csv"):
            shutil.move(src, os.path.join(csv_dir, item))
        else:
            shutil.move(src, os.path.join(non_csv_dir, item))

    shutil.rmtree(temp_output_dir)
