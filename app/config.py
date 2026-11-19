"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")

    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "4000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
