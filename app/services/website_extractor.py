import re
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.utils.validators import validate_url_for_fetch


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

BLOCKED_TAGS = {
    "script", "style", "noscript", "svg", "canvas",
    "iframe", "nav", "footer", "header",
}

MAX_CONTENT_CHARS = 12000


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_website_content(url: str, timeout: float = 15.0) -> dict:
    """Fetch a website and extract title, meta description, headings, and body text.

    Returns a dict with keys: url, title, description, headings, text, ok, error.
    """
    validate_url_for_fetch(url)

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
            response = client.get(url)
    except httpx.HTTPError as exc:
        return {"url": url, "ok": False, "error": f"Failed to fetch website: {exc}"}
    except Exception as exc:
        return {"url": url, "ok": False, "error": f"Unexpected error fetching website: {exc}"}

    if response.status_code >= 400:
        return {
            "url": url,
            "ok": False,
            "error": f"Website returned status {response.status_code}",
            "status_code": response.status_code,
        }

    html = response.text
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(BLOCKED_TAGS):
        tag.decompose()

    title_tag = soup.find("title")
    title = _clean_text(title_tag.get_text()) if title_tag else ""

    description = ""
    meta_desc = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    if meta_desc and meta_desc.get("content"):
        description = _clean_text(meta_desc["content"])
    if not description:
        og_desc = soup.find("meta", attrs={"property": re.compile("^og:description$", re.I)})
        if og_desc and og_desc.get("content"):
            description = _clean_text(og_desc["content"])

    headings = []
    for level in ("h1", "h2", "h3"):
        for tag in soup.find_all(level):
            txt = _clean_text(tag.get_text())
            if txt:
                headings.append({"level": level, "text": txt})

    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = _clean_text(main.get_text(" ", strip=True))
    if len(text) > MAX_CONTENT_CHARS:
        text = text[:MAX_CONTENT_CHARS] + "..."

    base_domain = urlparse(url).netloc
    internal_links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        parsed = urlparse(href)
        if parsed.netloc == base_domain:
            label = _clean_text(a.get_text())
            if label:
                internal_links.append({"label": label, "url": href})
    internal_links = internal_links[:30]

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
