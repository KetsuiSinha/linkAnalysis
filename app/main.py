"""FastAPI application for AI-Powered Multi-Platform Prospect Discovery."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from app.schemas import (
    ErrorResponse,
    ProspectDiscoveryRequest,
    ProspectDiscoveryResponse,
)
from app.services.prospect_service import discover_prospects
from app.utils.security import RateLimitMiddleware, validate_query
from app.utils.logging_config import logger, log_request, log_error


app = FastAPI(
    title="Dxora Test - AI-Powered Multi-Platform Prospect Discovery API",
    version="1.0.0",
    description=(
        "Accepts a natural-language prospect discovery query, understands the intent, "
        "discovers prospects across multiple platforms, consolidates duplicates, "
        "and returns structured JSON with verified social links and contact info."
    ),
)

# Security middleware
app.add_middleware(RateLimitMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "Dxora AI-Powered Multi-Platform Prospect Discovery API",
        "endpoints": {
            "prospect_discovery": "POST /prospect-discovery",
        },
        "docs": "/docs",
    }


@app.post(
    "/prospect-discovery",
    response_model=ProspectDiscoveryResponse,
    summary="Discover prospects from natural language query",
)
def prospect_discovery(request: ProspectDiscoveryRequest):
    """Discover prospects from a natural language query across multiple platforms."""
    start_time = time.time()
    client_ip = "unknown"

    # Validate and sanitize query
    query = validate_query(request.query)

    try:
        result = discover_prospects(query)
    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000
        log_error("prospect_discovery", exc, {"query": query[:50]})
        log_request(query, "unknown", False, 0, duration_ms)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                error="Prospect discovery failed",
                detail="Internal server error",
            ).dict(),
        )

    duration_ms = (time.time() - start_time) * 1000
    prospect_count = result.total_prospects if hasattr(result, 'total_prospects') else len(result.prospects) if hasattr(result, 'prospects') else 0
    log_request(query, "unknown", result.success, prospect_count, duration_ms)

    if not result.success:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                success=False,
                error="Discovery failed",
            ).dict(),
        )

    return result