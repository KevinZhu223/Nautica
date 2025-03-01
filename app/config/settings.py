from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    OPENAI_KEY: str
    DATABASE_URL: str
    REGION_NAME: str
    BUCKET_NAME: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
