"""Base class for platform discovery."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.schemas import RawProfile, SearchResult
from app.config import settings


class BasePlatform(ABC):
    """Base class for platform discovery."""

    name: str = "Base Platform"
    rate_limit_delay: float = 1.0  # seconds between requests

    def __init__(self):
        self.settings = settings

    @abstractmethod
    def search(self, query: str, understood_query: dict, max_results: int = 10) -> List[dict]:
        """Search for prospects on this platform. Returns list of raw profile dicts."""

    @abstractmethod
    def extract_profile(self, url: str) -> Optional[dict]:
        """Extract detailed profile info from a profile URL."""

    def _rate_limit(self):
        """Rate limiting between requests."""
        import time
        import random
        time.sleep(self.rate_limit_delay + random.uniform(0, 0.5))


class SearchPlatform(BasePlatform):
    """Platforms that use search APIs (Google, etc.)."""

    def __init__(self):
        super().__init__()
        self.session = None

    def _get_session(self):
        import httpx
        if self.session is None:
            self.session = httpx.Client(timeout=30.0, follow_redirects=True)
        return self.session

    def close(self):
        if self.session:
            self.session.close()
            self.session = None