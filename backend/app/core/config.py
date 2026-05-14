from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Asayomi API"
    debug: bool = False
    database_url: str = "sqlite:///./asayomi.db"

    # Azure OpenAI
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: str = "gpt-4o-mini"

    # Collection
    collection_interval_hours: int = 8
    data_retention_days: int = 30

    # Frontend
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
