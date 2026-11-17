from app.services.llm_service import analyze_website


def run_link_analysis(url: str) -> dict:
    return analyze_website(url)
