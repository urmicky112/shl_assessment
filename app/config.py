from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    gemini_api_key: str
    chroma_db_path: str = str(Path(__file__).parent.parent / "chroma_db")
    
    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = 'utf-8'

settings = Settings()