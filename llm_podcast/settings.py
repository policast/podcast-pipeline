"""Central module for app settings."""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from '.env' file, or overwritten by ENV VARS."""

    model_config = SettingsConfigDict(
        env_file=".env",  # environment variables will take priority over .env file
        env_file_encoding="utf-8",
        extra="allow",
    )
    openai_api_key: SecretStr = Field(
        default=...,
        description="API key for OpenAPI.",
    )


# Paths
DATA_DIR: Path = Path("data/")
MEETING_DIR: Path = DATA_DIR / "meeting"
PDF_DIR: Path = DATA_DIR / "pdf"
TXT_DIR: Path = DATA_DIR / "txt"
SUMMARY_DIR: Path = DATA_DIR / "summary"
SCRIPT_DIR: Path = DATA_DIR / "script"
SOUND_DIR: Path = DATA_DIR / "sound"
