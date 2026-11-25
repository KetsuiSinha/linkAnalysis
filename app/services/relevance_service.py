"""Relevance scoring service for prospects."""

from typing import Dict, Any, List

from app.services.llm_service import LLMService
from app.utils.normalizers import extract_keywords, calculate_jaccard_similarity


def calculate_relevance(prospect: Dict[str, Any], understood_query: Dict[str, Any]) -> float:
    """Calculate relevance score (0.0 to 1.0) for a prospect against the understood query."""
    score = 0.0
    max_score = 0.0

    # Interest/keyword match in bio
    bio = (prospect.get("bio") or "").lower()
    interest = understood_query.get("interest", "").lower()
    search_keywords = [kw.lower() for kw in understood_query.get("search_keywords", [])]

    bio_keywords = set(extract_keywords(bio))
    query_keywords = set([kw for kw in [interest] + search_keywords if kw])

    if bio_keywords and query_keywords:
        overlap = len(bio_keywords & query_keywords)
        if overlap > 0:
            score += 0.4 * (overlap / len(query_keywords))

    # Location match
    prospect_loc = (prospect.get("location") or "").lower()
    city = understood_query.get("city", "").lower()
    state = understood_query.get("state", "").lower()
    country = understood_query.get("country", "").lower()

    if city and city in prospect_loc:
        score += 0.3
    elif state and state in prospect_loc:
        score += 0.2
    elif country and country in prospect_loc:
        score += 0.1

    # Social platform presence (more platforms = more verified)
    social_count = len(prospect.get("social_link", []))
    if social_count >= 3:
        score += 0.15
    elif social_count >= 2:
        score += 0.1
    elif social_count >= 1:
        score += 0.05

    # Contact info availability
    if prospect.get("email"):
        score += 0.05
    if prospect.get("phone"):
        score += 0.05
    if prospect.get("whatsapp_link"):
        score += 0.05

    return min(score, 1.0)


def filter_relevant_prospects(prospects: List[dict], understood_query: dict, min_score: float = 0.2) -> List[dict]:
    """Filter prospects by relevance score."""
    scored = []
    for prospect in prospects:
        score = calculate_relevance(prospect, understood_query)
        if score >= min_score:
            prospect["_relevance_score"] = score
            scored.append(prospect)

    # Sort by relevance score descending
    scored.sort(key=lambda p: p.get("_relevance_score", 0), reverse=True)
    return scored