import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

FOLDER_ID = '1ZGyXj5EQ1KbtkhEphlO2ghLTvv3mfmFk'
CREDENTIALS_FILE = '/home/LavetoLab/credentials.json'

# SET TO FALSE FOR LIVE DELETION
DRY_RUN = False

def enforce_latest_backup_policy():
    try:
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=creds)

        query = f"'{FOLDER_ID}' in parents and trashed = false"
        results = service.files().list(
            q=query,
            orderBy='createdTime desc',
            fields="files(id, name, createdTime)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        files = results.get('files', [])

        latest_db = None
        latest_ui = None
        to_trash = []

        for file in files:
            name = file['name']
            if name.startswith("ledger_") and not latest_db:
                latest_db = file
                print(f"✅ Retaining latest DB: {name}")
            elif name.startswith("UI_TEMPLATES_") and not latest_ui:
                latest_ui = file
                print(f"✅ Retaining latest UI: {name}")
            else:
                to_trash.append(file)

        if to_trash:
            print(f"Cleanup initiated. {'[DRY-RUN MODE - NO DELETION]' if DRY_RUN else 'Executing deletion...'}")
            for file in to_trash:
                if DRY_RUN:
                    print(f"-> [DRY-RUN] Would trash: {file['name']}")
                else:
                    print(f"-> Trashing: {file['name']}")
                    service.files().update(
                        fileId=file['id'],
                        body={'trashed': True},
                        supportsAllDrives=True
                    ).execute()
        else:
            print("System clean. Latest pair protected.")

    except Exception as e:
        print(f"🚨 TASK ERROR: {str(e)}")

if __name__ == "__main__":
    enforce_latest_backup_policy()