# Dxora Test - AI-Powered Website Link Analysis API

A FastAPI application that analyzes a website URL, understands its content using an LLM, and returns structured business, competitor, SEO, search-query, and target-audience insights.

## Endpoint (port 4000)

| Endpoint | Method | Description |
|---|---|---|
| `POST /link-analysis` | POST | Analyze a website URL and return five insight sections |
| `GET /docs` | GET | Interactive Swagger UI |
| `GET /` | GET | Service health/info |

## Project structure

```
linkAnalysis/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app + /link-analysis endpoint
│   ├── config.py         # Pydantic Settings (.env)
│   ├── schemas.py        # Pydantic v2 request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py   # Thin orchestration layer
│   │   ├── competitor_service.py # Competitor normalization
│   │   ├── llm_service.py        # OpenAI client + rule-based fallback
│   │   └── website_extractor.py  # HTTPX + BeautifulSoup fetcher
│   └── utils/
│       ├── __init__.py
│       └── validators.py         # URL validation + SSRF protection
├── tests/
│   └── test_link_analysis.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add OPENAI_API_KEY (optional; rule-based fallback works without it)

# 4. Run the server
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Open http://localhost:4000/docs for the interactive API documentation.

## Example request

```http
POST http://localhost:4000/link-analysis
Content-Type: application/json

{
  "url": "https://example.com"
}
```

## Example response

```json
{
  "success": true,
  "website": "https://example.com/",
  "brand": {
    "name": "Example Domain",
    "category": "Technology Services",
    "summary": "..."
  },
  "analysis": {
    "competitor_analysis": {
      "brand_overview": "...",
      "competitors": [...],
      "strengths": [...],
      "weaknesses_or_gaps": [...],
      "competitive_advantages": [...],
      "opportunities": [...]
    },
    "target_search_queries": [
      {
        "query": "Best technology services company",
        "platforms": ["Google", "LinkedIn"],
        "intent": "Service Discovery",
        "business_relevance": "...",
        "target_audience": "..."
      }
    ],
    "seo_improvements": {
      "primary_keyword": "...",
      "secondary_keywords": [...],
      "recommended_title": "...",
      "meta_description": "...",
      "supporting_content": [...]
    },
    "top_services": [...],
    "target_audience": {
      "primary_audience": [...],
      "secondary_audience": [...],
      "industries": [...],
      "customer_needs": [...]
    }
  }
}
```

## How it works

1. **Validate** the URL (http/https only; private/internal addresses are blocked for SSRF safety).
2. **Fetch** the page with HTTPX and extract readable text via BeautifulSoup (scripts, styles, nav, footers, and iframes are stripped).
3. **Analyze** with OpenAI `gpt-4o-mini` (structured JSON output) when an API key is present. When no key is configured, or the LLM call fails, a deterministic rule-based analyzer builds the same shape from the extracted content so the endpoint still returns valid JSON.
4. **Return** the five sections required by the brief: competitor analysis, target search queries, SEO improvements, top 5 services, and target audience.

## LLM research & recommendation

| Provider | Model | Approx. cost (in/out per 1M) | Context window | JSON support | Verdict |
|---|---|---|---|---|---|
| OpenAI | gpt-4o-mini | $0.15 / $0.60 | 128K | Yes (`response_format`) | Best balance |
| OpenAI | gpt-4o | $2.50 / $10.00 | 128K | Yes | Highest accuracy, higher cost |
| Google Gemini | gemini-1.5-flash | $0.075 / $0.30 | 1M | Yes | Cheapest, very fast |
| Anthropic Claude | claude-3-haiku | $0.25 / $1.25 | 200K | Yes | Fast, solid accuracy |

*Pricing is approximate and based on public provider documentation; verify before production use.*

**Recommended:** OpenAI `gpt-4o-mini` — reliable structured-JSON output, good accuracy for content understanding, low cost, and a 128K context window that comfortably holds a cleaned page. **Fallback:** `gemini-1.5-flash` (lowest cost, largest context). **No-key fallback:** the app's built-in rule-based analyzer.

### Cost optimization
- Strip scripts, styles, nav, footer, and iframes before sending content to the LLM.
- Cap body text at ~12K characters to keep prompts small.
- Use `gpt-4o-mini` instead of `gpt-4o`.
- A single LLM call produces all five sections (no repeated calls).
- Cache results per URL where appropriate.

## Error handling

- Invalid URL scheme or missing hostname → `400`
- Private/internal addresses (localhost, 10.x, 172.16–31.x, 192.168.x, link-local) → `400` (SSRF protection)
- Unreachable website or HTTP ≥ 400 → `400` with the fetch error
- LLM failure → automatic rule-based fallback; response is still valid JSON

## Testing

```bash
pip install pytest
pytest tests/
```

##  Screenshots

<img width="1917" height="1078" alt="image" src="https://github.com/user-attachments/assets/f2bb8b5f-6dca-4617-8573-7f8fc514c532" />
<img width="1917" height="1078" alt="image" src="https://github.com/user-attachments/assets/d5129134-2fe7-4c72-9a83-5fa2ff4e57c5" />
