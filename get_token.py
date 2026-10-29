import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Vela, this is the final recalibrated configuration [cite: 2026-03-04]
CLIENT_CONFIG = {
    "web": {  # Changed from 'installed' to 'web' for server stability [cite: 2026-03-04]
        "client_id": "564395220839-gt58giu6k5u1qu3ulmr27941sur23nhi.apps.googleusercontent.com",
        "project_id": "system-restoration-sync",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"]
    }
}

def forge_vault_key():
    # Using the from_client_config flow to keep the handshake secure [cite: 2026-03-04]
    flow = InstalledAppFlow.from_client_config(
        CLIENT_CONFIG, 
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri='http://localhost' # Set here only [cite: 2026-03-04]
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent')

    print(f"\n1. Open this link: {auth_url}\n")
    code = input("2. Paste the 'code=' value from the URL here: ").strip()

    flow.fetch_token(code=code)
    with open('token.json', 'w') as f:
        f.write(flow.credentials.to_json())
    print("\nSUCCESS: Master Key forged and saved to token.json!")

if __name__ == "__main__":
    forge_vault_key()