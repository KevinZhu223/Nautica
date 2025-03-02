# projects.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.core import get_current_active_user, get_db
from app.db import crud, models
from app.schemas.project import ProjectCreate, ProjectResponse, MessageCreate, MessageResponse, ProjectUpdate
from app.utils.gcs import upload_file_to_gcs

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

    # Initialize list to hold new picture URLs
    new_picture_urls = []
    for file in files:
        picture_url = upload_file_to_gcs(file)  # Upload each file and get its URL
        new_picture_urls.append(picture_url)
    
    # Append the new URLs to the project's existing pictures list (or initialize if None)
    if project.pictures is None:
        project.pictures = new_picture_urls
    else:
        project.pictures = project.pictures + new_picture_urls

    print(project.pictures)

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
    new_message = crud.add_message_to_project(db, project, message_text=message_data.message, role=message_data.role)
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
