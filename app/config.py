import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret_key_here_32_chars_long_at_least_!!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # minutes
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    class Config:
        env_file = ".env" # Optional: Load .env file if it exists
        extra = "ignore" # Allow extra fields in .env not defined in Settings

settings = Settings()
