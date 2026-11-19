"""Helper to normalize competitor entries returned by the LLM."""

from typing import Any, Dict, List


def enrich_competitors(competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ensure every competitor has the expected fields and an ``inferred`` flag."""
    enriched: List[Dict[str, Any]] = []
    for c in competitors or []:
        enriched.append(
            {
                "name": c.get("name", "Unknown Competitor"),
                "main_service": c.get("main_service", "Not specified"),
                "target_market": c.get("target_market", "Not specified"),
                "key_strength": c.get("key_strength", "Not specified"),
                "opportunity": c.get("opportunity", "Not specified"),
                "inferred": c.get("inferred", True),
            }
        )
    return enriched
