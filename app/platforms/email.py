"""Email platform for contact discovery."""

from typing import List, Optional

import httpx
from app.config import settings
from app.platforms.base import BasePlatform
from app.utils.validators import normalize_url, validate_email
from app.utils.validators import extract_emails


class EmailPlatform(BasePlatform):
    name = "Email"

    def __init__(self):
        super().__init__()

    def search(self, query: str, understood_query: dict, max_results: int = 10) -> List[dict]:
        """Search for email addresses."""
        # Email doesn't have a search API
        # We extract emails from other sources (Google, websites, profiles)
        return []

    def extract_profile(self, url: str) -> Optional[dict]:
        """Extract email from a URL."""
        return None

    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        return extract_emails(text)

    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        from app.utils.validators import validate_email
        return validate_email(email)