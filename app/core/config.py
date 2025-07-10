from pydantic_settings import BaseSettings
from typing import Optional
import imp

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cab Booking API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/cabdb"  
    SECRET_KEY: str = "supersecretkey" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 