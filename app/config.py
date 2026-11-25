"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM credentials
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")

    # Search API credentials
    google_search_api_key: str | None = os.getenv("GOOGLE_SEARCH_API_KEY")
    google_search_cx: str | None = os.getenv("GOOGLE_SEARCH_CX")

    # Platform API credentials
    linkedin_access_token: str | None = os.getenv("LINKEDIN_ACCESS_TOKEN")
    twitter_bearer_token: str | None = os.getenv("TWITTER_BEARER_TOKEN")
    youtube_api_key: str | None = os.getenv("YOUTUBE_API_KEY")
    facebook_access_token: str | None = os.getenv("FACEBOOK_ACCESS_TOKEN")

    # App settings
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "4000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()