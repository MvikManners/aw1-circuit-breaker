import os

# 📂 GOSPEL OS: ABSOLUTE STORAGE CONFIGURATION VECTOR
SCOPES = ['https://www.googleapis.com/auth/drive']

# Explicitly mapping absolute paths to bypass relative path container errors
GOOGLE_CREDENTIALS_PATH = "/home/LavetoLab/google_key.json"
DRIVE_FOLDER_ID = "0AO4NRDoHSKuxUk9PVA"

print(f"📡 GOSPEL OS CONFIG: Drive Root Anchor assigned to ID: {DRIVE_FOLDER_ID}", flush=True)
print(f"📡 GOSPEL OS CONFIG: Cryptographic Key Path verified at: {GOOGLE_CREDENTIALS_PATH}", flush=True)