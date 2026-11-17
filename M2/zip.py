import zipfile
import os

zip_path = "M2/Archive.zip"
print(zip_path)
extract_path = "M2"

os.makedirs(extract_path, exist_ok=True)

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(extract_path)

print("ZIP file extracted successfully!")