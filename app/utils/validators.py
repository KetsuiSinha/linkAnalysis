"""Input validation utilities."""

import re
from typing import Optional
from urllib.parse import urlparse

from fastapi import HTTPException


# Platforms we support
SUPPORTED_PLATFORMS = {
    "Google", "LinkedIn", "X", "YouTube", "Instagram",
    "Facebook", "Threads", "WhatsApp", "Email"
}

# Email regex
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Phone regex (basic international format)
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")

# WhatsApp link patterns
WHATSAPP_PATTERNS = [
    re.compile(r"https?://(?:wa\.me|api\.whatsapp\.com)/[A-Za-z0-9_+-]+"),
    re.compile(r"https?://(?:web\.)?whatsapp\.com/send\?phone=\d+"),
]

# Social media URL patterns for validation
PLATFORM_URL_PATTERNS = {
    "LinkedIn": re.compile(r"https?://(?:www\.)?linkedin\.com/(?:in|company)/[A-Za-z0-9_-]+"),
    "X": re.compile(r"https?://(?:www\.)?(?:twitter\.com|x\.com)/[A-Za-z0-9_]+"),
    "YouTube": re.compile(r"https?://(?:www\.)?youtube\.com/(?:@[A-Za-z0-9_-]+|channel/[A-Za-z0-9_-]+|user/[A-Za-z0-9_-]+)"),
    "Instagram": re.compile(r"https?://(?:www\.)?instagram\.com/[A-Za-z0-9_.]+"),
    "Facebook": re.compile(r"https?://(?:www\.)?facebook\.com/[A-Za-z0-9_.]+"),
    "Threads": re.compile(r"https?://(?:www\.)?threads\.net/@[A-Za-z0-9_.]+"),
    "WhatsApp": re.compile(r"https?://(?:wa\.me|api\.whatsapp\.com|web\.whatsapp\.com)/[A-Za-z0-9_+-]+"),
}


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(EMAIL_REGEX.match(email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format (basic E.164)."""
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    return bool(PHONE_REGEX.match(cleaned))


def validate_whatsapp_link(url: str) -> bool:
    """Validate WhatsApp contact link."""
    return any(pattern.match(url) for pattern in WHATSAPP_PATTERNS)


def validate_platform_url(platform: str, url: str) -> bool:
    """Validate that a URL matches the expected pattern for a platform."""
    pattern = PLATFORM_URL_PATTERNS.get(platform)
    if not pattern:
        return True  # No pattern defined, allow
    return bool(pattern.match(url))


def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format."""
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if not cleaned.startswith("+"):
        # Assume US if no country code
        if len(cleaned) == 10:
            cleaned = "+1" + cleaned
        elif len(cleaned) == 11 and cleaned.startswith("1"):
            cleaned = "+" + cleaned
    return cleaned


def extract_emails(text: str) -> list:
    """Extract all email addresses from text."""
    return EMAIL_REGEX.findall(text)


def extract_phones(text: str) -> list:
    """Extract phone numbers from text."""
    # Basic pattern for various phone formats
    phone_pattern = re.compile(r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?)?\d{3}[\s\-]?\d{4}")
    return phone_pattern.findall(text)


def extract_whatsapp_links(text: str) -> list:
    """Extract WhatsApp links from text."""
    links = []
    for pattern in WHATSAPP_PATTERNS:
        links.extend(pattern.findall(text))
    return links


def normalize_url(url: str) -> str:
    """Normalize URL (remove tracking params, ensure https)."""
    parsed = urlparse(url)
    # Remove common tracking parameters
    tracking_params = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
    query_parts = []
    for param in parsed.query.split("&"):
        if param and param.split("=")[0] not in tracking_params:
            query_parts.append(param)
    clean_query = "&".join(query_parts)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{clean_query}" if clean_query else f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def is_valid_profile_url(platform: str, url: str) -> bool:
    """Check if a URL is a valid profile URL for the platform."""
    if platform not in SUPPORTED_PLATFORMS:
        return False
    if platform == "Email":
        return validate_email(url.replace("mailto:", ""))
    if platform == "WhatsApp":
        return validate_whatsapp_link(url)
    return validate_platform_url(platform, url)