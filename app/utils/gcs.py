import time
from fastapi import UploadFile
from app.config.settings import Settings
from google.cloud import storage

settings = Settings()

def upload_file_to_gcs(file: UploadFile) -> str:
    client = storage.Client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    file_name = f"document_{int(time.time())}_{file.filename}"
    blob = bucket.blob(file_name)
    blob.upload_from_file(file.file)
    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{file_name}"
