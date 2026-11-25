"""Google Custom Search platform for prospect discovery."""

import json
import urllib.parse
from typing import List, Optional

import httpx
from app.config import settings
from app.platforms.base import SearchPlatform
from app.utils.validators import is_valid_profile_url, normalize_url, extract_emails, extract_phones, extract_whatsapp_links
from app.utils.normalizers import extract_keywords


class GooglePlatform(SearchPlatform):
    name = "Google"

    def __init__(self):
        super().__init__()
        self.api_key = settings.google_search_api_key
        self.cx = settings.google_search_cx
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, understood_query: dict, max_results: int = 10) -> List[dict]:
        """Search Google Custom Search API for prospects."""
        if not self.api_key or not self.cx:
            return []

        # Build search query
        search_terms = understood_query.get("search_keywords", [])
        search_query = " ".join(query.split()[:8])  # Use first 8 words of original query
        if understood_query.get("city"):
            search_query += f" {understood_query['city']}"
        if understood_query.get("state"):
            search_query += f" {understood_query['state']}"
        if understood_query.get("country"):
            search_query += f" {understood_query['country']}"

        # Add site-specific search for better profile discovery
        search_query += " (site:linkedin.com OR site:twitter.com OR site:instagram.com OR site:facebook.com OR site:youtube.com OR site:threads.net)"

        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": search_query,
            "num": min(max_results, 10),
        }

        try:
            response = self._get_session().get(self.base_url, params=params, timeout=30)
            if response.status_code != 200:
                return []
            data = response.json()
        except Exception:
            return []

        results = []
        items = data.get("items", [])
        for item in items[:max_results]:
            url = item.get("link", "")
            if not url:
                continue

            # Extract title and snippet
            title = item.get("title", "")
            snippet = item.get("snippet", "")

            # Extract potential name from title
            name = self._extract_name_from_title(title, snippet)

            # Extract contact info from snippet
            emails = extract_emails(snippet)
            phones = extract_phones(snippet)
            whatsapp_links = extract_whatsapp_links(snippet)

            # Only add if it looks like a profile (has a name or contact info)
            if name or emails or phones or whatsapp_links:
                results.append({
                    "name": name or "Unknown",
                    "platform": "Google",
                    "profile_url": normalize_url(url),
                    "location": None,
                    "bio": snippet[:500],
                    "email": emails[0] if emails else None,
                    "phone": None,
                    "whatsapp_link": whatsapp_links[0] if whatsapp_links else None,
                    "source": "Google",
                })

        return results

    def extract_profile(self, url: str) -> Optional[dict]:
        """Extract detailed profile from a Google search result URL."""
        # For Google, we just return the search result as-is
        return None

    def _extract_name_from_title(self, title: str, snippet: str) -> Optional[str]:
        """Extract a person's name from title/snippet."""
        import re
        # Common patterns: "Name - Title", "Name | Title", "Name - Company"
        patterns = [
            r"^([A-Z][a-z]+ [A-Z][a-z]+)",  # "John Smith"
            r"^([A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+)",  # "John Michael Smith"
        ]
        for pattern in [re.compile(p) for p in patterns]:
            match = pattern.search(title)
            if match:
                return match.group(1)
        # Try snippet
        match = re.search(r"([A-Z][a-z]+ [A-Z][a-z]+)", snippet)
        if match:
            return match.group(1)
        return None