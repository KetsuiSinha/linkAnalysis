from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.schemas import LinkAnalysisRequest, LinkAnalysisResponse, ErrorResponse
from app.services.analysis_service import run_link_analysis


app = FastAPI(
    title="Dxora Test - AI-Powered Website Link Analysis API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "service": "Dxora AI-Powered Website Link Analysis API",
        "endpoints": {
            "link_analysis": "POST /link-analysis",
        },
        "docs": "/docs",
    }


@app.post("/link-analysis", response_model=LinkAnalysisResponse)
def link_analysis(request: LinkAnalysisRequest):
    """Analyze a website URL and return business, competitor, SEO, services, and audience insights."""
    url = str(request.url)
    try:
        result = run_link_analysis(url)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(success=False, error="Analysis failed", detail=str(exc)).dict(),
        )
    if not result.get("success"):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(success=False, error=result.get("error", "Unknown error")).dict(),
        )
    return result
