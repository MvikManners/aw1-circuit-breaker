import os
import json

def reveal_secrets():
    print("--- 🔍 REVEALING ENVIRONMENT VARIABLES ---")
    # This will print every variable your server has access to
    for key, value in os.environ.items():
        if "DRIVE" in key or "GOOGLE" in key or "FOLDER" in key:
            print(f"{key}: {value}")
    print("--- 🏁 END OF REVEAL ---")

if __name__ == "__main__":
    reveal_secrets()