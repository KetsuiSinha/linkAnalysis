"""Threads platform for prospect discovery."""

from typing import List, Optional

import httpx
from app.config import settings
from app.platforms.base import SearchPlatform
from app.utils.validators import normalize_url
from app.utils.validators import extract_emails, extract_phones, extract_whatsapp_links
from app.utils.normalizers import extract_keywords


class ThreadsPlatform(SearchPlatform):
    name = "Threads"

    def __init__(self):
        super().__init__()
        # Threads uses Instagram Graph API
        self.base_url = "https://graph.facebook.com/v18.0"

    def search(self, query: str, understood_query: dict, max_results: int = 10) -> List[dict]:
        """Search Threads for prospects."""
        # Threads API not publicly available yet
        # Placeholder
        return []

    def extract_profile(self, url: str) -> Optional[dict]:
        """Extract profile from Threads URL."""
        return None