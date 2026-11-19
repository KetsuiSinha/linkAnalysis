"""LLM-powered website analysis with a deterministic rule-based fallback.

When ``OPENAI_API_KEY`` is configured the service calls OpenAI's
``gpt-4o-mini`` with ``response_format`` set to ``json_object`` so the model
returns valid JSON. When no key is available (or the LLM call fails) a
rule-based analyzer builds the same response shape from the extracted page
content, keeping the endpoint functional without any third-party credentials.
"""

import json
from typing import Any, Dict, List

from app.config import settings
from app.services.website_extractor import extract_website_content


def _urlparse_host(url: str) -> str:
    from urllib.parse import urlparse

    return urlparse(url).netloc or ""


class LLMService:
    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=self.api_key)
            except Exception:  # pragma: no cover - import/runtime guard
                self.client = None

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #
    def analyze(self, url: str) -> Dict[str, Any]:
        extracted = extract_website_content(url)
        if not extracted.get("ok"):
            return {
                "success": False,
                "website": url,
                "error": extracted.get("error", "Failed to extract website content"),
            }

        if self.client is not None:
            return self._analyze_with_llm(url, extracted)

        return self._analyze_rule_based(url, extracted)

    # ------------------------------------------------------------------ #
    # OpenAI path
    # ------------------------------------------------------------------ #
    def _analyze_with_llm(self, url: str, extracted: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "You are an expert business, SEO, and market research analyst. "
            "Analyze the website content below and return ONLY valid JSON. "
            "Do not invent search volumes or traffic figures. Mark any "
            "competitor data that is AI-suggested rather than verified."
        )

        user_prompt = self._build_llm_prompt(url, extracted)

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            data = json.loads(completion.choices[0].message.content or "{}")
        except Exception:
            # Fall back gracefully so the endpoint never returns a 500
            # just because the LLM had a hiccup.
            return self._analyze_rule_based(url, extracted)

        return self._shape_response(url, data)

    # ------------------------------------------------------------------ #
    # Rule-based fallback
    # ------------------------------------------------------------------ #
    def _analyze_rule_based(self, url: str, extracted: Dict[str, Any]) -> Dict[str, Any]:
        title = extracted.get("title") or ""
        description = extracted.get("description") or ""
        headings = extracted.get("headings") or []
        text = extracted.get("text") or ""
        if isinstance(text, list):
            text = " ".join(text)
        links = extracted.get("internal_links") or []

        brand_name = title or _urlparse_host(url) or "Unknown Brand"
        category = self._guess_category(text, headings)
        summary = description or (
            text[:200] + "..." if len(text) > 200 else text
        ) or "No description available."

        h1_texts = [h["text"] for h in headings if h.get("level") == "h1"]
        primary = h1_texts[0] if h1_texts else (title.split(" - ")[0] if title else category)
        primary_keyword = primary or category

        return self._shape_response(
            url,
            {
                "brand": {
                    "name": brand_name,
                    "category": category,
                    "summary": summary,
                },
                "competitor_analysis": {
                    "brand_overview": summary,
                    "competitors": self._build_competitors(category),
                    "strengths": ["Direct customer relationships", "Niche focus"],
                    "weaknesses_or_gaps": [
                        "Limited brand recognition",
                        "Smaller resource base",
                    ],
                    "competitive_advantages": ["Personalized service", "Agility"],
                    "opportunities": [
                        "Improve online visibility",
                        "Expand service pages",
                    ],
                },
                "target_search_queries": self._build_search_queries(
                    brand_name, category, primary_keyword
                ),
                "seo_improvements": self._build_seo(
                    brand_name, category, primary_keyword, description
                ),
                "top_services": self._infer_services(headings, links),
                "target_audience": self._build_audience(category),
            },
        )

    # ------------------------------------------------------------------ #
    # Response shaping (nests the five sections under "analysis")
    # ------------------------------------------------------------------ #
    @staticmethod
    def _shape_response(
        url: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        section_keys = (
            "competitor_analysis",
            "target_search_queries",
            "seo_improvements",
            "top_services",
            "target_audience",
        )
        analysis_block = {
            key: data[key] for key in section_keys if key in data
        }

        return {
            "success": True,
            "website": url,
            "brand": data.get(
                "brand",
                {"name": "Unknown Brand", "category": "Unknown", "summary": ""},
            ),
            "analysis": analysis_block,
        }

    # ------------------------------------------------------------------ #
    # Prompt construction
    # ------------------------------------------------------------------ #
    @staticmethod
    def _build_llm_prompt(url: str, extracted: Dict[str, Any]) -> str:
        return f"""
Website URL: {url}
Page title: {extracted.get('title', '')}
Meta description: {extracted.get('description', '')}
Headings: {extracted.get('headings', [])}
Body text: {extracted.get('text', '')}
Internal links: {extracted.get('internal_links', [])}

Produce a JSON object with these exact keys:

{{
  "brand": {{"name": "...", "category": "...", "summary": "..."}},
  "competitor_analysis": {{
    "brand_overview": "...",
    "competitors": [{{"name":"...","main_service":"...","target_market":"...","key_strength":"...","opportunity":"...","inferred":true}}],
    "strengths": [...],
    "weaknesses_or_gaps": [...],
    "competitive_advantages": [...],
    "opportunities": [...]
  }},
  "target_search_queries": [
    {{"query":"...","platforms":["Google"],"intent":"...","business_relevance":"...","target_audience":"..."}}
  ],
  "seo_improvements": {{
    "primary_keyword":"...",
    "secondary_keywords":["..."],
    "long_tail_keywords":["..."],
    "relevant_business_keywords":["..."],
    "recommended_title":"...",
    "improved_title_structure":"...",
    "meta_description":"...",
    "supporting_content":["..."]
  }},
  "top_services": [
    {{"service_name":"...","description":"...","target_industry":"...","target_customer":"...","main_benefit":"...","inferred":false}}
  ],
  "target_audience": {{
    "primary_audience":["..."],
    "secondary_audience":["..."],
    "industry_segments":["..."],
    "business_types":["..."],
    "customer_profiles":["..."],
    "location_focus":"...",
    "customer_needs":["..."],
    "customer_interests":["..."],
    "recommended_segments":["..."]
  }}
}}

Return exactly 5 target search queries and exactly 5 top services where possible.
"""

    # ------------------------------------------------------------------ #
    # Heuristic helpers (used by the rule-based fallback)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _guess_category(text: str, headings: list) -> str:
        blob = " ".join([h.get("text", "") for h in headings] + [text]).lower()
        keywords = {
            "web development": ["web development", "website", "web design", "web app"],
            "digital marketing": ["digital marketing", "seo", "social media", "marketing"],
            "software development": ["software", "custom software", "saas", "application development"],
            "e-commerce": ["e-commerce", "online store", "shop", "cart"],
            "consulting": ["consulting", "consultancy", "advisory"],
            "technology services": ["technology", "it services", "tech"],
        }
        for category, kws in keywords.items():
            if any(k in blob for k in kws):
                return category.title()
        return "Technology Services"

    @staticmethod
    def _infer_services(headings: list, links: list) -> List[Dict[str, Any]]:
        services: List[Dict[str, Any]] = []
        seen = set()
        candidates = [
            h.get("text", "")
            for h in headings
            if h.get("level") in ("h1", "h2", "h3")
        ]
        candidates += [l.get("label", "") for l in links]

        for c in candidates:
            c = c.strip()
            if not c or len(c) < 3 or c.lower() in seen:
                continue
            seen.add(c.lower())
            services.append(
                {
                    "service_name": c,
                    "description": f"{c} offering based on website content.",
                    "target_industry": "General",
                    "target_customer": "Businesses and individuals",
                    "main_benefit": "Addresses a core customer need.",
                    "inferred": True,
                }
            )
            if len(services) >= 5:
                break

        if not services:
            services.append(
                {
                    "service_name": "Consultation",
                    "description": "Initial business consultation.",
                    "target_industry": "General",
                    "target_customer": "Prospective clients",
                    "main_benefit": "Understand client needs.",
                    "inferred": True,
                }
            )
        return services[:5]

    @staticmethod
    def _build_search_queries(brand_name: str, category: str, primary: str) -> List[Dict[str, str]]:
        return [
            {
                "query": f"Best {category} company",
                "platforms": ["Google", "LinkedIn"],
                "intent": "Service Discovery",
                "business_relevance": f"Customers looking for {category}",
                "target_audience": "Prospective clients",
            },
            {
                "query": f"{primary} services",
                "platforms": ["Google"],
                "intent": "Service Search",
                "business_relevance": f"Direct demand for {primary}",
                "target_audience": "Service buyers",
            },
            {
                "query": f"{brand_name} reviews",
                "platforms": ["Google", "Facebook"],
                "intent": "Research",
                "business_relevance": "Brand trust and reputation",
                "target_audience": "Evaluating customers",
            },
            {
                "query": f"{category} ideas",
                "platforms": ["Instagram"],
                "intent": "Inspiration",
                "business_relevance": "Visual discovery",
                "target_audience": "Creative buyers",
            },
            {
                "query": f"Affordable {category}",
                "platforms": ["X"],
                "intent": "Service Discovery",
                "business_relevance": "Price-sensitive demand",
                "target_audience": "Small businesses and startups",
            },
        ]

    @staticmethod
    def _build_seo(
        brand_name: str, category: str, primary: str, description: str
    ) -> Dict[str, Any]:
        return {
            "primary_keyword": primary,
            "secondary_keywords": [category, "services", "company"],
            "long_tail_keywords": [
                f"best {category} company",
                f"affordable {primary}",
                f"{category} for small business",
            ],
            "relevant_business_keywords": [category, primary, "solutions", "services"],
            "recommended_title": f"{primary} | {brand_name} {category}",
            "improved_title_structure": "Primary Keyword | Brand Name | Category",
            "meta_description": description
            or f"{brand_name} provides {category} solutions. Learn about our services and how we can help your business grow.",
            "supporting_content": [
                "Service landing pages",
                "Industry-specific pages",
                "Frequently Asked Questions",
                "Blog topics",
                "Location-based landing pages",
            ],
        }

    @staticmethod
    def _build_audience(category: str) -> Dict[str, Any]:
        return {
            "primary_audience": ["Small businesses", "Startups"],
            "secondary_audience": ["Enterprise companies", "Professional services"],
            "industry_segments": [category, "Technology", "Retail"],
            "business_types": ["SMB", "Startup", "Agency"],
            "customer_profiles": ["Business owner", "Marketing manager", "CTO"],
            "location_focus": None,
            "customer_needs": ["Online presence", "Lead generation", "Brand visibility"],
            "customer_interests": ["Technology", "Growth", "Digital transformation"],
            "recommended_segments": [
                "Small businesses seeking websites",
                "Startups needing digital solutions",
            ],
        }

    @staticmethod
    def _build_competitors(category: str) -> List[Dict[str, Any]]:
        return [
            {
                "name": f"Leading {category} Provider",
                "main_service": category,
                "target_market": "SMB and enterprise",
                "key_strength": "Established brand",
                "opportunity": "Improve customer engagement",
                "inferred": True,
            },
            {
                "name": f"Affordable {category} Agency",
                "main_service": category,
                "target_market": "Small businesses",
                "key_strength": "Low pricing",
                "opportunity": "Expand service range",
                "inferred": True,
            },
            {
                "name": f"Premium {category} Studio",
                "main_service": category,
                "target_market": "Enterprise",
                "key_strength": "High-end design",
                "opportunity": "Improve online visibility",
                "inferred": True,
            },
        ]


def analyze_website(url: str) -> Dict[str, Any]:
    """Convenience wrapper used by the service layer."""
    return LLMService().analyze(url)
