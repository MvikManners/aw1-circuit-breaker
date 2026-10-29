from cryptography.fernet import Fernet
import os

# 🔐 Ensure this is the same key used in your vault_sync.py
SECRET_KEY = b'IxwSCC82yCTHQPEQT8oQWdeVoQdAUeEHz8nODzLflYE='
cipher_suite = Fernet(SECRET_KEY)

# Path to the backup you want to test
backup_path = '/home/LavetoLab/backups/ledger_2026-06-02_090619.zip.enc'
output_path = '/home/LavetoLab/instance/restored_test.zip'

print(f"🔓 Decrypting: {backup_path}")

try:
    with open(backup_path, 'rb') as f:
        data = f.read()

    decrypted_data = cipher_suite.decrypt(data)

    with open(output_path, 'wb') as f:
        f.write(decrypted_data)

    print(f"✅ Success! Restored archive saved to: {output_path}")
except Exception as e:
    print(f"❌ Restoration Failed: {e}")

