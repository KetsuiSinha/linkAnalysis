"""Facebook platform for prospect discovery."""

from typing import List, Optional

import httpx
from app.config import settings
from app.platforms.base import SearchPlatform
from app.utils.validators import normalize_url


class FacebookPlatform(SearchPlatform):
    name = "Facebook"

    def __init__(self):
        super().__init__()
        self.access_token = settings.facebook_access_token
        self.base_url = "https://graph.facebook.com/v18.0"

    def search(self, query: str, understood_query: dict, max_results: int = 10) -> List[dict]:
        """Search Facebook for prospects."""
        if not self.access_token:
            return []
        # Facebook Graph API search for pages/people
        # Placeholder
        return []

    def extract_profile(self, url: str) -> Optional[dict]:
        """Extract profile from Facebook URL."""
        return None