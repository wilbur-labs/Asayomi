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
    azure_openai_embedding_deployment_name: str = "text-embedding-3-small"

    # Collection
    collection_interval_hours: int = 8
    data_retention_days: int = 30

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # Admin auth — required to call /api/v1/system/* trigger endpoints.
    # When unset, those routes return 503 (fail closed).
    admin_token: Optional[str] = None

    # SMTP / メール通知
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    notify_email: Optional[str] = None  # 通知先メールアドレス

    # Webhook 通知
    webhook_url: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None

    # RSS 出力
    rss_site_url: str = "http://localhost:5173"
    rss_max_items: int = 50

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
