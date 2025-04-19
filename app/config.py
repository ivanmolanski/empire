from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite+aiosqlite:///./empire.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # LLM Configuration
    PRIMARY_LLM_MODEL: str = "agentica-org/deepcoder-14b-preview:free"
    FALLBACK_LLM_MODEL: str = "gemini-2.0-flash-thinking-exp-01-21"
    OPENROUTER_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEFAULT_LLM_PROVIDER: Literal["openrouter", "gemini"] = "openrouter"

    class Config:
        env_file = ".env"

settings = Settings()
