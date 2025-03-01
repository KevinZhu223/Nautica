from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploads"  # Create this directory in your project

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        uploaded_files = []
        for file in files:
            # Create a unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append({
                "filename": file.filename,
                "saved_as": filename,
                "content_type": file.content_type
            })
        
        return {
            "message": "Files uploaded successfully",
            "files": uploaded_files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_files():
    try:
        files = os.listdir(UPLOAD_DIR)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))