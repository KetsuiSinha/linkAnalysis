"""YouTube platform for prospect discovery."""

from typing import List, Optional

import httpx
from app.config import settings
from app.platforms.base import SearchPlatform
from app.utils.validators import normalize_url
from app.utils.validators import extract_emails, extract_phones, extract_whatsapp_links
from app.utils.normalizers import extract_keywords


class YouTubePlatform(SearchPlatform):
    name = "YouTube"

    def __init__(self):
        super().__init__()
        self.api_key = settings.youtube_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"

    def search(self, query: str, understood_query: dict, max_results: int = 10) -> List[dict]:
        """Search YouTube for prospects (channels)."""
        if not self.api_key:
            return []

        keywords = understood_query.get("search_keywords", [])
        search_query = " ".join(keywords[:3])

        params = {
            "key": self.api_key,
            "part": "snippet",
            "q": search_query,
            "type": "channel",
            "maxResults": min(max_results, 50),
            "order": "relevance",
        }

        try:
            response = self._get_session().get(
                f"{self.base_url}/search",
                params=params,
                timeout=30,
            )
            if response.status_code != 200:
                return []
            data = response.json()
        except Exception:
            return []

        results = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            channel_id = item.get("id", {}).get("channelId", "")
            if not channel_id:
                continue

            title = snippet.get("title", "")
            description = snippet.get("description", "")
            channel_url = f"https://www.youtube.com/channel/{channel_id}"

            # Get channel details for more info
            channel_info = self._get_channel_info(channel_id)
            location = channel_info.get("country", "")
            email = channel_info.get("email")

            results.append({
                "name": title,
                "platform": "YouTube",
                "profile_url": channel_url,
                "location": location,
                "bio": description[:500],
                "email": email,
                "phone": None,
                "whatsapp_link": None,
                "source": "YouTube",
            })

        return results

    def _get_channel_info(self, channel_id: str) -> dict:
        """Get detailed channel info."""
        if not self.api_key:
            return {}

        params = {
            "key": self.api_key,
            "part": "snippet,brandingSettings",
            "id": channel_id,
        }

        try:
            response = self._get_session().get(
                f"{self.base_url}/channels",
                params=params,
                timeout=30,
            )
            if response.status_code != 200:
                return {}
            data = response.json()
            items = data.get("items", [])
            if not items:
                return {}
            item = items[0]
            snippet = item.get("snippet", {})
            branding = item.get("brandingSettings", {}).get("channel", {})
            return {
                "country": snippet.get("country", ""),
                "email": branding.get("email", ""),
            }
        except Exception:
            return {}

    def extract_profile(self, url: str) -> Optional[dict]:
        """Extract profile from YouTube URL."""
        return None