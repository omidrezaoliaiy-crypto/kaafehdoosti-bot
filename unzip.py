import zipfile
import os

print("Starting safe offline extraction...")
zip_path = r"C:\music_bundle.zip"
dest = r"C:\KaafehDoostiBot"

if os.path.exists(zip_path):
    print(f"Opening {zip_path} ({os.path.getsize(zip_path)} bytes)...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest)
    print("Extraction completed successfully!")
    try:
        os.remove(zip_path)
        print("Zip removed.")
    except Exception as e:
        print(f"Could not remove zip: {e}")
else:
    print(f"Zip file {zip_path} does not exist!")

r_dir = os.path.join(dest, "music_cache")
n_dir = os.path.join(dest, "music_cache_nostalgia")

r_count = len([f for f in os.listdir(r_dir) if f.lower().endswith(".mp3")]) if os.path.exists(r_dir) else 0
n_count = len([f for f in os.listdir(n_dir) if f.lower().endswith(".mp3")]) if os.path.exists(n_dir) else 0

print(f"OFFLINE_EXTRACTION_SUCCESS: RADIO={r_count} NOSTALGIA={n_count}")
