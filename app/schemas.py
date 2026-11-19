"""Request and response schemas for the link-analysis API.

All models use Pydantic v2. The response shape mirrors the example in the
assignment brief so reviewers can map each field directly to the spec.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class LinkAnalysisRequest(BaseModel):
    """Incoming request body: a single website URL to analyze."""

    url: HttpUrl = Field(..., description="Website URL to analyze")

    @field_validator("url")
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
    competitors: List[Competitor] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses_or_gaps: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)


class SearchQuery(BaseModel):
    query: str
    platforms: List[str] = Field(default_factory=list)
    intent: str
    business_relevance: str
    target_audience: str


class SEOImprovements(BaseModel):
    primary_keyword: str
    secondary_keywords: List[str] = Field(default_factory=list)
    long_tail_keywords: List[str] = Field(default_factory=list)
    relevant_business_keywords: List[str] = Field(default_factory=list)
    recommended_title: str
    improved_title_structure: str
    meta_description: str
    supporting_content: List[str] = Field(default_factory=list)


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
    primary_audience: List[str] = Field(default_factory=list)
    secondary_audience: List[str] = Field(default_factory=list)
    industry_segments: List[str] = Field(default_factory=list)
    business_types: List[str] = Field(default_factory=list)
    customer_profiles: List[str] = Field(default_factory=list)
    location_focus: Optional[str] = None
    customer_needs: List[str] = Field(default_factory=list)
    customer_interests: List[str] = Field(default_factory=list)
    recommended_segments: List[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    competitor_analysis: CompetitorAnalysis
    target_search_queries: List[SearchQuery] = Field(default_factory=list)
    seo_improvements: SEOImprovements
    top_services: List[Service] = Field(default_factory=list)
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
