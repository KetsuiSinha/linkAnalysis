"""Instagram platform for prospect discovery."""

from typing import List, Optional

import httpx
from app.config import settings
from app.platforms.base import SearchPlatform
from app.utils.validators import normalize_url
from app.utils.validators import extract_emails, extract_phones, extract_whatsapp_links
from app.utils.normalizers import extract_keywords


class InstagramPlatform(SearchPlatform):
    name = "Instagram"

    def __init__(self):
        super().__init__()
        self.access_token = settings.get("instagram_access_token") if hasattr(settings, "instagram_access_token") else None
        self.business_account_id = settings.get("instagram_business_account_id") if hasattr(settings, "instagram_business_account_id") else None
        self.base_url = "https://graph.facebook.com/v18.0"

    def search(self, query: str, understood_query: dict, max_results: int = 10) -> List[dict]:
        """Search Instagram for prospects."""
        # Instagram Graph API requires Business Account and specific permissions
        # Placeholder - return empty for now
        return []

    def extract_profile(self, url: str) -> Optional[dict]:
        """Extract profile from Instagram URL."""
        return None