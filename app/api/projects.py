# projects.py
import io
import os
import tempfile
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pdf2image import convert_from_bytes
from PIL import Image
from sqlalchemy.orm import Session

from app.core import get_current_active_user, get_db
from app.db import crud, models
from app.schemas.project import (MessageCreate, MessageResponse, ProjectCreate,
                                 ProjectResponse, ProjectUpdate)
from app.utils.gcs import upload_file_to_gcs
from app.utils.genai_helper import explain, chat

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    new_project = crud.create_project(db, user=current_user, pictures=[], explanation=project.explanation)
    return new_project

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    projects = crud.get_projects_by_user(db, user=current_user)
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    project = crud.get_project_by_id(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    project = crud.get_project_by_id(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    updated_project = crud.update_project(db, project, pictures=project_update.pictures, explanation=project_update.explanation)
    return updated_project

@router.delete("/{project_id}", response_model=ProjectResponse)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    project = crud.get_project_by_id(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    deleted_project = crud.delete_project(db, project)
    return deleted_project

@router.post("/{project_id}/upload_pictures", response_model=ProjectResponse)
def upload_pictures(
    project_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Retrieve the project and verify user ownership
    project = crud.get_project_by_id(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    new_picture_urls = []

    for file in files:
        filename = file.filename.lower()
        ext = os.path.splitext(filename)[1]
        file_bytes = file.file.read()

        if ext == ".pdf":
            try:
                pages = convert_from_bytes(file_bytes)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing PDF file: {e}")
            for i, page in enumerate(pages):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{i}.png") as tmp:
                    page.save(tmp, format="PNG")
                    temp_file_path = tmp.name
                with open(temp_file_path, "rb") as png_file:
                    picture_url = upload_file_to_gcs(png_file, filename=f"{os.path.splitext(filename)[0]}_page_{i}.png")
                new_picture_urls.append(picture_url)
                os.remove(temp_file_path)
        else:
            try:
                image = Image.open(BytesIO(file_bytes))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing image file: {e}")
            image = image.convert("RGBA")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                image.save(tmp, format="PNG")
                temp_file_path = tmp.name
            with open(temp_file_path, "rb") as png_file:
                picture_url = upload_file_to_gcs(png_file, filename=f"{os.path.splitext(filename)[0]}.png")
            new_picture_urls.append(picture_url)
            os.remove(temp_file_path)

        file.file.seek(0)

    if project.pictures is None:
        project.pictures = new_picture_urls
    else:
        project.pictures = project.pictures + new_picture_urls

    print("Updated project pictures:", project.pictures)
    db.commit()
    db.refresh(project)

    explanation = explain(project)
    project.explanation = explanation
    db.commit()
    db.refresh(project)
    return project



@router.post("/{project_id}/messages", response_model=MessageResponse)
def add_message(
    project_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    project = crud.get_project_by_id(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    new_message = crud.add_message_to_project(db, project, message_text=message_data.message, role="user")
    messages = crud.get_messages_for_project(db, project)
    assistant = chat(project, messages)
    new_message = crud.add_message_to_project(db, project, message_text=assistant, role="assistant")
    return new_message

@router.get("/{project_id}/messages", response_model=List[MessageResponse])
def get_messages(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    project = crud.get_project_by_id(db, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    messages = crud.get_messages_for_project(db, project)
    return messages
