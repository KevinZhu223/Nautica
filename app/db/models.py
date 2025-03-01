from sqlalchemy import (
    VARCHAR,
    Column,
    Float,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,  # import JSON type
    create_engine,
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from app.config.settings import settings

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    email = Column(VARCHAR(255), unique=True, index=True)
    password = Column(Text, nullable=False)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pictures = Column(JSON, default=[])  
    explanation = Column(JSON, default={})  
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="projects")
    messages = relationship("Message", back_populates="project", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    message = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="messages")

User.projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
