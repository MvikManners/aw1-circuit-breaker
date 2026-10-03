from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = '/home/LavetoLab/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = '1ZGyXj5EQ1KbtkhEphlO2ghLTvv3mfmFk' # Paste your Folder ID from the URL here

def test_connection():
    try:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        
        # Query to list files in your target folder
        query = f"'{FOLDER_ID}' in parents"
        results = service.files().list(q=query, fields="files(name, id)").execute()
        items = results.get('files', [])
        
        print(f"✅ Connection Successful! Folder contains {len(items)} items:")
        for item in items:
            print(f" - {item['name']}")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_connection()