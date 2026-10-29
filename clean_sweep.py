import os
import shutil

# 🛑 THE TARGET ZONES
UPLOAD_DIR = '/home/LavetoLab/static/'
FORENSICS_DIR = '/home/LavetoLab/static/forensics/'

def purge_local_storage():
    print("🧹 INITIATING GOSPEL OS CLEAN SWEEP...")
    
    folders_to_clean = [UPLOAD_DIR, FORENSICS_DIR]
    files_removed = 0
    bytes_saved = 0

    for folder in folders_to_clean:
        if not os.path.exists(folder):
            continue
            
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            
            # 🛡️ PROTECT SYSTEM FILES (Don't delete the logo or index files)
            if os.path.isdir(file_path) or filename.endswith(('.png', '.html', '.gitkeep')):
                continue

            try:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                files_removed += 1
                bytes_saved += file_size
                print(f"🗑️ PURGED: {filename}")
            except Exception as e:
                print(f"🚨 ERROR DELETING {filename}: {e}")

    print(f"\n✅ CLEAN SWEEP COMPLETE.")
    print(f"📊 FILES REMOVED: {files_removed}")
    print(f"💾 SPACE RECLAIMED: {round(bytes_saved / (1024 * 1024), 2)} MB")

if __name__ == "__main__":
    purge_local_storage()