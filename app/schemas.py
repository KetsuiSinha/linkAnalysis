"""Request and response schemas for the link-analysis API.

Pydantic v1 models (pure Python, no Rust compilation required for deployment).
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class LinkAnalysisRequest(BaseModel):
    """Incoming request body: a single website URL to analyze."""

    url: HttpUrl = Field(..., description="Website URL to analyze")

    @validator("url")
    @classmethod
    def url_must_be_http_or_https(cls, v: HttpUrl) -> HttpUrl:
        if v.scheme not in ("http", "https"):
            raise ValueError("URL must use http or https scheme")
        return v


class Brand(BaseModel):
    name: str = Field(..., description="Detected brand / site name")
    category: str = Field(..., description="Main business category")
    summary: str = Field(..., description="Short human-readable business summary")


class Competitor(BaseModel):
    name: str
    main_service: Optional[str] = None
    target_market: Optional[str] = None
    key_strength: Optional[str] = None
    opportunity: Optional[str] = None
    inferred: bool = Field(
        default=True,
        description="True when competitor data is AI-suggested rather than verified",
    )


class CompetitorAnalysis(BaseModel):
    brand_overview: str
    competitors: List[Competitor] = []
    strengths: List[str] = []
    weaknesses_or_gaps: List[str] = []
    competitive_advantages: List[str] = []
    opportunities: List[str] = []


class SearchQuery(BaseModel):
    query: str
    platforms: List[str] = []
    intent: str
    business_relevance: str
    target_audience: str


class SEOImprovements(BaseModel):
    primary_keyword: str
    secondary_keywords: List[str] = []
    long_tail_keywords: List[str] = []
    relevant_business_keywords: List[str] = []
    recommended_title: str
    improved_title_structure: str
    meta_description: str
    supporting_content: List[str] = []


class Service(BaseModel):
    service_name: str
    description: str
    target_industry: str
    target_customer: str
    main_benefit: str
    inferred: bool = Field(
        default=False,
        description="True when the service was inferred rather than read from the page",
    )


class TargetAudience(BaseModel):
    primary_audience: List[str] = []
    secondary_audience: List[str] = []
    industry_segments: List[str] = []
    business_types: List[str] = []
    customer_profiles: List[str] = []
    location_focus: Optional[str] = None
    customer_needs: List[str] = []
    customer_interests: List[str] = []
    recommended_segments: List[str] = []


class AnalysisResult(BaseModel):
    competitor_analysis: CompetitorAnalysis
    target_search_queries: List[SearchQuery] = []
    seo_improvements: SEOImprovements
    top_services: List[Service] = []
    target_audience: TargetAudience


class LinkAnalysisResponse(BaseModel):
    success: bool
    website: str
    brand: Brand
    analysis: AnalysisResult


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[Any] = None
