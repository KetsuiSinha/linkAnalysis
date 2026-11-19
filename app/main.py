"""FastAPI application exposing the /link-analysis endpoint."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.schemas import (
    ErrorResponse,
    LinkAnalysisRequest,
    LinkAnalysisResponse,
)
from app.services.analysis_service import run_link_analysis

app = FastAPI(
    title="Dxora Test - AI-Powered Website Link Analysis API",
    version="1.0.0",
    description=(
        "Accepts a website URL, extracts its content, analyzes it with an LLM "
        "(or a rule-based fallback when no LLM key is configured), and returns "
        "structured business, competitor, SEO, services, and audience insights."
    ),
)


@app.get("/", tags=["health"])
def root():
    """Service info and available endpoints."""
    return {
        "service": "Dxora AI-Powered Website Link Analysis API",
        "endpoints": {
            "link_analysis": "POST /link-analysis",
        },
        "docs": "/docs",
    }


@app.post(
    "/link-analysis",
    response_model=LinkAnalysisResponse,
    tags=["analysis"],
    summary="Analyze a website URL",
)
def link_analysis(request: LinkAnalysisRequest):
    """Analyze a website and return five structured insight sections.

    Sections returned:
    1. Competitor vs Your Brand Details
    2. Top 5 Target Search Queries
    3. SEO Improvement
    4. Top 5 Services
    5. Target Audience Identification
    """
    url = str(request.url)
    try:
        result = run_link_analysis(url)
    except HTTPException:
        # Let FastAPI handle validation/SSRF errors with their proper status codes.
        raise
    except Exception as exc:  # pragma: no cover - defensive top-level guard
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                error="Analysis failed",
                detail=str(exc),
            ).model_dump(),
        )

    if not result.get("success"):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                success=False,
                error=result.get("error", "Unknown error"),
            ).model_dump(),
        )

    return result
