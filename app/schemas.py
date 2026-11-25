"""Request and response schemas for the prospect discovery API."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class ProspectDiscoveryRequest(BaseModel):
    """Incoming request body: a natural-language prospect discovery query."""

    query: str = Field(..., min_length=3, max_length=500, description="Natural-language prospect discovery query")

    @validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        return v


class ParsedQuery(BaseModel):
    """Structured understanding of the user's natural-language query."""

    interest: str = Field(..., description="Primary interest or topic (e.g., Football, Digital Marketing)")
    audience: str = Field(..., description="Target audience description (e.g., Football lovers, Startup founders)")
    location: Optional[dict] = Field(default=None, description="Geographical location with city, state, country")
    target_type: str = Field(default="individual", description="Type of target: individual or business")


class SocialLink(BaseModel):
    """A single social media or contact link for a prospect."""

    platform: str = Field(..., description="Platform name (Google, LinkedIn, X, YouTube, Instagram, Facebook, Threads, WhatsApp, Email)")
    link: str = Field(..., description="Verified public profile or contact link")

    @validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        allowed = {"Google", "LinkedIn", "X", "YouTube", "Instagram", "Facebook", "Threads", "WhatsApp", "Email"}
        if v not in allowed:
            raise ValueError(f"Platform must be one of: {', '.join(allowed)}")
        return v


class Prospect(BaseModel):
    """A discovered prospect with consolidated social links."""

    name: str = Field(..., description="Prospect's full name")
    location: Optional[str] = Field(default=None, description="Geographical location when available")
    social_link: List[SocialLink] = Field(default_factory=list, description="Consolidated verified social and contact links")


class ProspectDiscoveryResponse(BaseModel):
    """Complete response for prospect discovery."""

    success: bool = True
    query: str
    total_prospects: int
    prospects: List[Prospect] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[Any] = None


# Internal schemas for processing
class RawProfile(BaseModel):
    """Raw profile data from a platform before consolidation."""

    name: str
    platform: str
    profile_url: HttpUrl
    location: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp_link: Optional[str] = None
    source: str  # platform name


class SearchResult(BaseModel):
    """A search result from a platform."""

    title: str
    url: HttpUrl
    snippet: Optional[str] = None
    platform: str


class UnderstoodQuery(BaseModel):
    """LLM-parsed query structure."""

    interest: str
    audience: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    target_type: str = "individual"
    search_keywords: List[str] = Field(default_factory=list)