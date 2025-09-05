from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    DATABASE_URL: str
    BUCKET_NAME: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", settings.GOOGLE_APPLICATION_CREDENTIALS)

