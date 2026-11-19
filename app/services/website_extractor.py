"""Website content extraction.

Fetches a URL over HTTP(S), strips boilerplate HTML (scripts, styles, nav,
footers, iframes), and returns the title, meta description, headings, body
text, and same-domain links that are useful for downstream LLM analysis.
"""

import re
from typing import Any, Dict
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.utils.validators import validate_url_for_fetch

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

# Tags that rarely carry business-relevant text and only add noise to the LLM.
BLOCKED_TAGS = {
    "script",
    "style",
    "noscript",
    "svg",
    "canvas",
    "iframe",
    "nav",
    "footer",
    "header",
}

# Hard cap on body text length so prompts stay within reasonable token limits.
MAX_CONTENT_CHARS = 12000


def _clean_text(text: str) -> str:
    """Collapse whitespace and trim."""
    return re.sub(r"\s+", " ", text or "").strip()


def extract_website_content(url: str, timeout: float = 15.0) -> Dict[str, Any]:
    """Fetch and extract readable content from a website.

    Returns a dict with keys:
        url, ok, error, status_code, title, description, headings, text,
        internal_links
    """
    validate_url_for_fetch(url)

    try:
        with httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            response = client.get(url)
    except httpx.HTTPError as exc:
        return {"url": url, "ok": False, "error": f"Failed to fetch website: {exc}"}
    except Exception as exc:  # pragma: no cover - defensive
        return {"url": url, "ok": False, "error": f"Unexpected error: {exc}"}

    if response.status_code >= 400:
        return {
            "url": url,
            "ok": False,
            "error": f"Website returned status {response.status_code}",
            "status_code": response.status_code,
        }

    soup = BeautifulSoup(response.text, "lxml")

    # Remove noise tags before extracting text.
    for tag in soup(BLOCKED_TAGS):
        tag.decompose()

    title_tag = soup.find("title")
    title = _clean_text(title_tag.get_text()) if title_tag else ""

    description = _extract_meta_description(soup)

    headings = _extract_headings(soup)

    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = _clean_text(main.get_text(" ", strip=True))
    if len(text) > MAX_CONTENT_CHARS:
        text = text[:MAX_CONTENT_CHARS] + "..."

    internal_links = _extract_internal_links(soup, url)

    return {
        "url": url,
        "ok": True,
        "title": title,
        "description": description,
        "headings": headings,
        "text": text,
        "internal_links": internal_links,
        "status_code": response.status_code,
    }


def _extract_meta_description(soup: BeautifulSoup) -> str:
    for attrs in (
        {"name": re.compile("^description$", re.I)},
        {"property": re.compile("^og:description$", re.I)},
    ):
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            return _clean_text(tag["content"])
    return ""


def _extract_headings(soup: BeautifulSoup) -> list:
    headings = []
    for level in ("h1", "h2", "h3"):
        for tag in soup.find_all(level):
            txt = _clean_text(tag.get_text())
            if txt:
                headings.append({"level": level, "text": txt})
    return headings


def _extract_internal_links(soup: BeautifulSoup, url: str) -> list:
    base_domain = urlparse(url).netloc
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        parsed = urlparse(href)
        if parsed.netloc == base_domain:
            label = _clean_text(a.get_text())
            if label:
                links.append({"label": label, "url": href})
    return links[:30]
