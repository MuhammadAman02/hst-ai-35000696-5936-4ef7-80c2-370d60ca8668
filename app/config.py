from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "sqlite:///./asics_store.db"
    secret_key: str = "your-secret-key-change-in-production"
    admin_username: str = "admin"
    admin_password: str = "admin123"
    debug: bool = True
    upload_dir: str = "static/images/products"
    
    class Config:
        env_file = ".env"

settings = Settings()