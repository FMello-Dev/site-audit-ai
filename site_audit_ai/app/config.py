from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Deixamos Optional para não travar se faltar uma das duas
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None 
    HEADLESS_MODE: bool = True

    class Config:
        env_file = ".env"

settings = Settings()