from typing import List


def enrich_competitors(competitors: List[dict]) -> List[dict]:
    enriched = []
    for c in competitors or []:
        enriched.append({
            "name": c.get("name", "Unknown Competitor"),
            "main_service": c.get("main_service", "Not specified"),
            "target_market": c.get("target_market", "Not specified"),
            "key_strength": c.get("key_strength", "Not specified"),
            "opportunity": c.get("opportunity", "Not specified"),
            "inferred": c.get("inferred", True),
        })
    return enriched
