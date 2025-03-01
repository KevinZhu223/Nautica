# schemas/project.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    pictures: Optional[List[str]] = []
    explanation: Optional[dict] = {}

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    message: str
    role: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    project_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
