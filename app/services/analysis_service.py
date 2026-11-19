"""Thin orchestration layer for link analysis."""

from app.services.llm_service import analyze_website


def run_link_analysis(url: str) -> dict:
    """Run the full five-section analysis for a URL."""
    return analyze_website(url)
