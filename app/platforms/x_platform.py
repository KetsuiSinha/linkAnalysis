"""X (Twitter) platform for prospect discovery."""

from typing import List, Optional

import httpx
from app.config import settings
from app.platforms.base import SearchPlatform
from app.utils.validators import is_valid_profile_url, normalize_url
from app.utils.validators import extract_emails, extract_phones, extract_whatsapp_links
from app.utils.normalizers import extract_keywords


class XPlatform(SearchPlatform):
    name = "X"

    def __init__(self):
        super().__init__()
        self.bearer_token = settings.twitter_bearer_token
        self.base_url = "https://api.twitter.com/2"

    def search(self, query: str, understood_query: dict, max_results: int = 10) -> List[dict]:
        """Search X for prospects."""
        if not self.bearer_token:
            return []

        keywords = understood_query.get("search_keywords", [])
        search_query = " ".join(keywords[:3])

        # X API v2 recent search
        params = {
            "query": f"{query} -is:retweet lang:en",
            "max_results": min(max_results, 100),
            "user.fields": "username,name,description,location,url,verified,public_metrics",
            "expansions": "author_id",
        }

        try:
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            response = self._get_session().get(
                f"{self.base_url}/tweets/search/recent",
                params=params,
                headers=headers,
                timeout=30,
            )
            if response.status_code != 200:
                return []
            data = response.json()
        except Exception:
            return []

        results = []
        users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
        for tweet in data.get("data", []):
            author_id = tweet.get("author_id")
            user = users.get(author_id)
            if not user:
                continue

            username = user.get("username", "")
            name = user.get("name", username)
            bio = user.get("description", "")
            location = user.get("location", "")
            profile_url = f"https://twitter.com/{username}"

            emails = extract_emails(bio)
            phones = extract_phones(bio)

            results.append({
                "name": name,
                "platform": "X",
                "profile_url": profile_url,
                "location": location,
                "bio": bio[:500],
                "email": emails[0] if emails else None,
                "phone": None,
                "whatsapp_link": None,
                "source": "X",
            })

        return results

    def extract_profile(self, url: str) -> Optional[dict]:
        """Extract profile from X URL."""
        return None