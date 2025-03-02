# utils/gcs.py
import os
import time
from google.cloud import storage
from app.config.settings import Settings
import secrets

settings = Settings()

def upload_file_to_gcs(file, filename: str = None) -> str:
    """
    Upload a file to Google Cloud Storage and return its public URL.

    Parameters:
        file: Either a FastAPI UploadFile or a file-like object.
        filename: Optional filename to use for the stored file.
    """
    client = storage.Client()
    bucket = client.bucket(settings.BUCKET_NAME)
    
    if filename is None:
        try:
            filename = file.filename
        except AttributeError:
            filename = f"{secrets.token_hex(8)}.png"
    
    file_name = f"document_{int(time.time())}_{filename}"
    blob = bucket.blob(file_name)
    
    if hasattr(file, "file"):
        blob.upload_from_file(file.file)
    else:
        blob.upload_from_file(file)
    
    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{file_name}"
