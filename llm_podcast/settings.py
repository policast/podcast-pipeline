"""Central module for app settings."""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from '.env' file, or overwritten by ENV VARS."""

    model_config = SettingsConfigDict(
        env_file=".env",  # environment variables will take priority over .env file
        env_file_encoding="utf-8",
    )
    openai_api_key: SecretStr = Field(
        default=...,
        description="API key for OpenAPI.",
    )


# Paths
DATA_DIR: Path = Path("data/")
MEETING_ID: int = 14107
MEETING_DIR: Path = DATA_DIR / "meeting"
MEETING_JSON_PATH = MEETING_DIR / f"{MEETING_ID}.json"
PDF_DIR: Path = DATA_DIR / "pdf"
TXT_DIR: Path = DATA_DIR / "txt"
SUMMARY_DIR: Path = DATA_DIR / "summary"
SCRIPT_DIR: Path = DATA_DIR / "script"
SOUND_DIR: Path = DATA_DIR / "sound"
