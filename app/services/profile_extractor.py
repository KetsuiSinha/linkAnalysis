"""Profile extraction service."""

from typing import Optional, Dict, Any, List

from app.platforms import PLATFORMS
from app.utils.validators import is_valid_profile_url, normalize_url
from app.utils.validators import extract_emails, extract_phones, extract_whatsapp_links
from app.utils.normalizers import extract_keywords


def extract_profile_from_url(url: str, platform_name: str) -> Optional[Dict[str, Any]]:
    """Extract detailed profile information from a profile URL."""
    platform = next((p for p in PLATFORMS if p.name == platform_name), None)
    if not platform:
        return None

    try:
        return platform.extract_profile(url)
    except Exception:
        return None


def enrich_profile_from_web(url: str) -> Dict[str, Any]:
    """Extract additional profile info by fetching the profile page."""
    import httpx
    from bs4 import BeautifulSoup
    import re

    result = {
        "name": None,
        "bio": None,
        "location": None,
        "email": None,
        "phone": None,
        "whatsapp_link": None,
    }

    try:
        response = httpx.get(url, timeout=15, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        if response.status_code != 200:
            return result

        html = response.text
        soup = BeautifulSoup(html, "lxml")

        # Extract text content
        text = soup.get_text(" ", strip=True)[:2000]

        # Extract emails
        emails = extract_emails(text)
        if emails:
            result["email"] = emails[0]

        # Extract phones
        phones = extract_phones(text)
        if phones:
            result["phone"] = phones[0]

        # Extract WhatsApp links
        whatsapp_links = extract_whatsapp_links(text)
        if whatsapp_links:
            result["whatsapp_link"] = whatsapp_links[0]

        # Try to extract name from meta tags
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            result["name"] = og_title["content"]

        # Try to extract bio/description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            result["bio"] = og_desc["content"][:500]

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content") and not result["bio"]:
            result["bio"] = meta_desc["content"][:500]

    except Exception:
        pass

    return result