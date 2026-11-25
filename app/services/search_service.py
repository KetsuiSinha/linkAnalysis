"""Search service for multi-platform prospect discovery."""

from typing import List, Dict, Any

from app.platforms import PLATFORMS
from app.schemas import UnderstoodQuery


def search_all_platforms(query: str, understood_query: UnderstoodQuery, max_results_per_platform: int = 10) -> List[Dict[str, Any]]:
    """Search all platforms for prospects."""
    # Handle both dict and Pydantic model
    if hasattr(understood_query, 'search_keywords'):
        understood_dict = {
            "search_keywords": understood_query.search_keywords,
            "city": understood_query.city,
            "state": understood_query.state,
            "country": understood_query.country,
            "interest": understood_query.interest,
            "audience": understood_query.audience,
            "target_type": understood_query.target_type,
        }
    else:
        understood_dict = understood_query

    all_results = []
    for platform in PLATFORMS:
        try:
            platform_results = platform.search(query, understood_dict, max_results=10)
            all_results.extend(platform_results)
        except Exception as e:
            # Log error but continue with other platforms
            print(f"Error searching {platform.name}: {e}")
            continue

    return all_results