import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Settings(BaseSettings):
    bot_token: str = Field(default="123456789:dummy_token", validation_alias="BOT_TOKEN")
    admin_id: Optional[int] = Field(default=None, validation_alias="ADMIN_ID")
    database_url: str = Field(default="sqlite+aiosqlite:///finance_bot.db", validation_alias="DATABASE_URL")
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
