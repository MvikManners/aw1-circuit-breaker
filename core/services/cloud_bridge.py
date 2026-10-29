from google.cloud import storage
from google.oauth2 import service_account
import os

# Secure credentials path
KEY_PATH = "/home/LavetoLab/credentials.json"

def get_storage_client():
    """Returns an authenticated GCS client."""
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
    return storage.Client(credentials=credentials, project="system-restoration-sync")

def upload_to_gcs(file_obj, bucket_name, destination_blob_name):
    """Uploads a file to your GCS forensic bucket."""
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_file(file_obj)
    return blob.public_url # Returns the link for the AI auditor to read