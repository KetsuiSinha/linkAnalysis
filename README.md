# Dxora Test - AI-Powered Website Link Analysis API

A FastAPI application that analyzes a given website URL, understands its content using an LLM, and generates structured business, competitor, SEO, search query, and target audience insights.

## Endpoint (port 4000)

| Endpoint | Method | Description |
|---|---|---|
| `POST /link-analysis` | POST | Analyze a website URL (5 analysis sections) |
| `GET /docs` | GET | Interactive Swagger UI |
| `GET /` | GET | Service info |

## Project structure

```
linkAnalysis/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app + /link-analysis endpoint
│   ├── config.py        # Pydantic Settings (.env)
│   ├── schemas.py       # Pydantic request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py
│   │   ├── competitor_service.py
│   │   ├── llm_service.py          # OpenAI + rule-based fallback
│   │   └── website_extractor.py    # HTTPX + BeautifulSoup
│   └── utils/
│       ├── __init__.py
│       └── validators.py           # URL validation + SSRF protection
├── tests/
│   └── test_link_analysis.py
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add OPENAI_API_KEY (or leave blank for rule-based fallback)

# 4. Run the server
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Open http://localhost:4000/docs for the interactive API docs.

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
  "website": "https://example.com",
  "brand": {
    "name": "Example",
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
      {"query": "Best technology services company", "platforms": ["Google", "LinkedIn"], "intent": "Service Discovery", ...}
    ],
    "seo_improvements": {
      "primary_keyword": "...",
      "recommended_title": "...",
      "meta_description": "...",
      "supporting_content": [...]
    },
    "top_services": [...],
    "target_audience": {...}
  }
}
```

## LLM Platform Research & Recommendation

### Comparison

| Provider | Model | API Cost (input/output) | Context Window | JSON Support | Recommendation |
|---|---|---|---|---|---|
| OpenAI | gpt-4o-mini | $0.15 / $0.60 per 1M tokens | 128K | Yes (`response_format`) | Best balance |
| OpenAI | gpt-4o | $2.50 / $10.00 per 1M tokens | 128K | Yes | Highest accuracy, higher cost |
| Google Gemini | gemini-1.5-flash | $0.075 / $0.30 per 1M tokens | 1M | Yes | Cheapest, very fast |
| Anthropic Claude | claude-3-haiku | $0.25 / $1.25 per 1M tokens | 200K | Yes | Fast, good accuracy |

*Pricing is approximate and based on public provider documentation. Verify current pricing before production use.*

### Recommended model

**Provider:** OpenAI  
**Model:** `gpt-4o-mini`  
**Estimated input tokens:** ~3,000–6,000 per analysis (cleaned content)  
**Estimated output tokens:** ~800–1,500 per analysis  
**Estimated cost per analysis:** ~$0.001–$0.005  
**Expected response time:** 2–6 seconds  
**Reason:** Strong structured-JSON support via `response_format`, good accuracy for content understanding, low cost, and 128K context window handles typical website content.  
**Fallback:** `gemini-1.5-flash` (lowest cost, largest context).  
**No-key fallback:** The app includes a deterministic rule-based analyzer so the endpoint works without an API key.

### Cost optimization
- Strip scripts, styles, nav, footer, iframes before sending content to the LLM.
- Truncate body text to ~12K chars.
- Use `gpt-4o-mini` (smaller, cheaper) instead of `gpt-4o`.
- Single LLM call produces all five sections (avoids repeated calls).
- Cache results per URL where appropriate.

## Error handling
- Invalid URLs → 400 with a clear message.
- SSRF protection: localhost, private IPs (10.x, 172.16–31.x, 192.168.x), link-local, and loopback addresses are blocked.
- Unreachable websites → 400 with the fetch error.
- LLM failure → automatic rule-based fallback so the response is still valid JSON.

## Testing

```bash
pip install pytest
pytest tests/
```

## Submission notes
- No API keys or secrets are committed. Use `.env` (gitignored) for credentials.
- Follow Dxora Technologies on LinkedIn and CREST on Instagram as part of application verification.
- Share your LinkedIn and Instagram profile links when submitting.
- Email: hr@chivoxai.com — Subject: `Your Name - Python Practical test review`
