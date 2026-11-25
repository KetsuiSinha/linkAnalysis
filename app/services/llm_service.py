"""LLM service for natural language query understanding."""

import json
import os
from typing import Any, Dict, List, Optional

from app.config import settings
from app.schemas import UnderstoodQuery


class LLMService:
    """LLM service for natural language query understanding and prospect relevance classification."""

    def __init__(self):
        self.api_key = settings.openai_api_key
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def understand_query(self, query: str) -> UnderstoodQuery:
        """Parse natural language query into structured search parameters."""
        if self.client:
            return self._understand_with_llm(query)
        return self._understand_rule_based(query)

    def _understand_with_llm(self, query: str) -> UnderstoodQuery:
        """Use LLM to understand the query."""
        system_prompt = (
            "You are an expert at parsing natural language prospect discovery queries. "
            "Extract structured search parameters from the user's query. "
            "Return ONLY valid JSON matching the specified schema."
        )

        user_prompt = f"""
Parse this prospect discovery query into structured parameters:

Query: "{query}"

Return JSON with these exact fields:
{{
  "interest": "Primary interest/topic (e.g., Football, Digital Marketing)",
  "audience": "Target audience description (e.g., Football lovers, Startup founders)",
  "city": "City name if mentioned, otherwise null",
  "state": "State/province if mentioned, otherwise null",
  "country": "Country if mentioned, otherwise null",
  "target_type": "individual or business",
  "search_keywords": ["keyword1", "keyword2", "keyword3"]
}}

Rules:
- Extract location hierarchy: city, state/province, country
- If only "Washington DC" mentioned, city="Washington DC", state="District of Columbia", country="USA"
- If "London UK" mentioned, city="London", state=null, country="UK"
- Generate 3-5 relevant search keywords for platform searches
- target_type is "individual" unless query mentions "business", "company", "agency", "owners"
"""

        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content
            data = json.loads(content)
            return UnderstoodQuery(**data)
        except Exception:
            return self._understand_rule_based(query)

    def _understand_rule_based(self, query: str) -> UnderstoodQuery:
        """Rule-based fallback for query understanding."""
        query_lower = query.lower()

        # Extract location components
        city = None
        state = None
        country = None

        # Common location patterns
        location_patterns = {
            "washington dc": ("Washington DC", "District of Columbia", "USA"),
            "new york": ("New York", "New York", "USA"),
            "los angeles": ("Los Angeles", "California", "USA"),
            "chicago": ("Chicago", "Illinois", "USA"),
            "san francisco": ("San Francisco", "California", "USA"),
            "boston": ("Boston", "Massachusetts", "USA"),
            "seattle": ("Seattle", "Washington", "USA"),
            "austin": ("Austin", "Texas", "USA"),
            "denver": ("Denver", "Colorado", "USA"),
            "miami": ("Miami", "Florida", "USA"),
            "london": ("London", None, "UK"),
            "paris": ("Paris", None, "France"),
            "berlin": ("Berlin", None, "Germany"),
            "tokyo": ("Tokyo", None, "Japan"),
            "sydney": ("Sydney", "New South Wales", "Australia"),
            "mumbai": ("Mumbai", "Maharashtra", "India"),
            "delhi": ("Delhi", None, "India"),
            "bangalore": ("Bangalore", "Karnataka", "India"),
            "ahmedabad": ("Ahmedabad", "Gujarat", "India"),
            "dubai": ("Dubai", None, "UAE"),
            "singapore": ("Singapore", None, "Singapore"),
            "hong kong": ("Hong Kong", None, "Hong Kong"),
            "toronto": ("Toronto", "Ontario", "Canada"),
            "vancouver": ("Vancouver", "British Columbia", "Canada"),
        }

        query_lower = query.lower()
        for pattern, (c, s, co) in location_patterns.items():
            if pattern in query_lower:
                city = c
                state = s
                country = co
                break

        # Extract interest/keywords - simple approach
        interest_keywords = [
            "football", "soccer", "cricket", "basketball", "tennis", "golf",
            "digital marketing", "marketing", "seo", "seo expert", "social media marketing",
            "startup", "startup founder", "entrepreneur", "founder", "co-founder",
            "restaurant", "restaurant owner", "chef", "food",
            "real estate", "real estate agent", "realtor",
            "software", "software engineer", "developer", "programmer",
            "data science", "data scientist", "machine learning", "ai",
            "finance", "investment", "venture capital", "vc",
            "lawyer", "attorney", "legal",
            "doctor", "physician", "healthcare",
            "teacher", "professor", "education",
        ]

        interest = "General"
        for keyword in interest_keywords:
            if keyword in query.lower():
                interest = keyword.title()
                break

        # Determine audience
        audience = query  # fallback to full query
        audience_keywords = {
            "lovers": "enthusiasts",
            "fans": "enthusiasts",
            "enthusiasts": "enthusiasts",
            "owners": "business owners",
            "founders": "founders",
            "founder": "founder",
            "entrepreneurs": "entrepreneurs",
            "entrepreneur": "entrepreneur",
            "professionals": "professionals",
            "experts": "experts",
            "specialists": "specialists",
            "consultants": "consultants",
            "agencies": "agencies",
            "companies": "companies",
            "startups": "startups",
        }

        audience = "Professionals"
        for kw, aud in audience_keywords.items():
            if kw in query.lower():
                audience = aud
                break

        # Generate search keywords
        search_keywords = [interest.lower()]
        if city:
            search_keywords.append(city.lower())
        if state:
            search_keywords.append(state.lower())
        if country:
            search_keywords.append(country.lower())

        return UnderstoodQuery(
            interest=interest,
            audience=audience,
            city=city,
            state=state,
            country=country,
            target_type="individual",
            search_keywords=search_keywords[:5],
        )

    def classify_relevance(self, prospect_data: dict, understood_query: dict) -> float:
        """Classify prospect relevance to the query (0.0 to 1.0)."""
        # Rule-based relevance scoring
        score = 0.0
        factors = 0

        # Interest match
        bio = (prospect_data.get("bio") or "").lower()
        interest = understood_query.get("interest", "").lower()
        if interest and interest in bio:
            score += 0.4
        factors += 1

        # Location match
        loc = (prospect_data.get("location") or "").lower()
        city = (understood_query.get("city") or "").lower()
        state = (understood_query.get("state") or "").lower()
        country = (understood_query.get("country") or "").lower()

        if city and city in loc:
            score += 0.3
        elif state and state in loc:
            score += 0.2
        elif country and country in loc:
            score += 0.1
        factors += 1

        # Interest keywords in bio
        bio_keywords = set(bio.split())
        query_keywords = set((understood_query.get("interest", "") + " " + " ".join(understood_query.get("search_keywords", []))).lower().split())
        if bio_keywords and query_keywords:
            overlap = len(bio_keywords & query_keywords)
            if overlap > 0:
                score += 0.2 * min(overlap / len(query_keywords), 1.0)
        factors += 1

        return min(score, 1.0) if factors > 0 else 0.0


def understand_query(query: str) -> UnderstoodQuery:
    """Convenience function to understand a query."""
    return LLMService().understand_query(query)