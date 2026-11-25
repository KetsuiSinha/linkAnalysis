"""Query understanding service."""

from app.services.llm_service import understand_query
from app.schemas import UnderstoodQuery


def understand_prospect_query(query: str) -> UnderstoodQuery:
    """Understand a prospect discovery query."""
    return understand_query(query)