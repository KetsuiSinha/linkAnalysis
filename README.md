# Dxora Test - AI-Powered Multi-Platform Prospect Discovery API

A FastAPI application that discovers relevant prospects across multiple online platforms based on a natural-language search query.

## Endpoint (port 4000)

| Endpoint | Method | Description |
|---|---|---|
| `POST /prospect-discovery` | POST | Discover prospects from natural language query |
| `GET /docs` | GET | Interactive Swagger UI |
| `GET /` | GET | Service health/info |

## Project structure

```
linkAnalysis/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + /prospect-discovery endpoint
│   ├── config.py            # Settings from .env
│   ├── schemas.py           # Pydantic v1 request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── query_service.py       # LLM query understanding
│   │   ├── search_service.py      # Multi-platform search orchestration
│   │   ├── prospect_service.py    # Main discovery pipeline
│   │   ├── profile_extractor.py   # Profile enrichment from web
│   │   ├── deduplication_service.py # Profile consolidation
│   │   ├── relevance_service.py   # Prospect relevance scoring
│   │   └── llm_service.py         # LLM integration (OpenAI + fallback)
│   ├── platforms/ (9 platforms: Google, LinkedIn, X, YouTube, Instagram, Facebook, Threads, WhatsApp, Email)
│   │   ├── __init__.py
│   │   ├── base.py           # Base platform class
│   │   ├── google.py         # Google Custom Search
│   │   ├── linkedin.py       # LinkedIn (placeholder)
│   │   ├── x_platform.py     # X (Twitter) API v2
│   │   ├── youtube.py        # YouTube Data API v3
│   │   ├── instagram.py      # Instagram Graph API (placeholder)
│   │   ├── facebook.py       # Facebook Graph API (placeholder)
│   │   ├── threads.py        # Threads (placeholder)
│   │   ├── whatsapp.py       # WhatsApp contact extraction
│   │   └── email.py          # Email extraction
│   └── utils/
│       ├── __init__.py
│       ├── validators.py     # Input validation (email, phone, URL, WhatsApp)
│       ├── normalizers.py    # Name/location matching, deduplication helpers
│       ├── security.py       # SSRF protection, input sanitization, rate limiting
│       └── logging_config.py # Structured logging
├── tests/
│   └── test_prospect_discovery.py
├── .env.example
├── .gitignore
├── requirements.txt
├── runtime.txt
├── Procfile
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
# Edit .env and add:
# - OPENAI_API_KEY (for query understanding & relevance)
# - GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_CX (for Google Custom Search)
# - YOUTUBE_API_KEY (for YouTube channel discovery)
# - TWITTER_BEARER_TOKEN (for X/Twitter search)
# Other platform keys are optional

# 4. Run the server
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Open http://localhost:4000/docs for the interactive API documentation.

## Example request

```http
POST http://localhost:4000/prospect-discovery
Content-Type: application/json

{
  "query": "Football lovers in Washington DC in USA"
}
```

## Example response

```json
{
  "success": true,
  "query": "Football lovers in Washington DC in USA",
  "total_prospects": 2,
  "prospects": [
    {
      "name": "John Smith",
      "location": "Washington DC, USA",
      "social_link": [
        {
          "platform": "Facebook",
          "link": "https://www.facebook.com/johnsmith"
        },
        {
          "platform": "Instagram",
          "link": "https://www.instagram.com/johnsmith"
        },
        {
          "platform": "LinkedIn",
          "link": "https://www.linkedin.com/in/johnsmith"
        },
        {
          "platform": "X",
          "link": "https://x.com/johnsmith"
        },
        {
          "platform": "Email",
          "link": "mailto:john.smith@example.com"
        },
        {
          "platform": "WhatsApp",
          "link": "https://wa.me/15551234567"
        }
      ]
    },
    {
      "name": "Michael Johnson",
      "location": "Washington DC, USA",
      "social_link": [
        {
          "platform": "YouTube",
          "link": "https://www.youtube.com/channel/UC123456789"
        },
        {
          "platform": "Threads",
          "link": "https://www.threads.net/@michaeljohnson"
        }
      ]
    }
  ]
}
```

## How it works

1. **Query Understanding** - LLM (or rule-based fallback) parses the natural language query into structured parameters: interest, audience, city/state/country, and search keywords.

2. **Multi-Platform Search** - Searches across 9 platforms:
   - Google (Custom Search API) - finds public profiles
   - LinkedIn - professional profiles
   - X (Twitter) - recent tweets from relevant users
   - YouTube - channels matching interest/location
   - Instagram, Facebook, Threads - placeholders (need API access)
   - WhatsApp, Email - contact info extraction from other sources

3. **Profile Enrichment** - Fetches profile pages to extract bio, location, email, phone, WhatsApp links.

4. **Deduplication** - Identifies and merges profiles belonging to the same person across platforms using name/location matching.

5. **Relevance Scoring** - Scores prospects by interest match, location match, platform presence, and contact info availability.

6. **Structured Output** - Returns consolidated prospects with verified social links.

## Security Features

- **Input Validation & Sanitization** - All inputs sanitized, length-limited, control characters removed
- **SSRF Protection** - Outbound requests validated against allowed domains, private IP ranges blocked
- **Rate Limiting** - 30 requests/minute per IP (configurable)
- **Input Length Limits** - Queries limited to 500 characters
- **CORS Configuration** - Configurable CORS policy
- **No Secrets in Code** - All credentials via environment variables

## Supported Platforms

| Platform | Method | Status |
|---|---|---|
| Google | Custom Search API | ✅ Working |
| X (Twitter) | API v2 | ✅ Working |
| YouTube | Data API v3 | ✅ Working |
| LinkedIn | API | ⚠️ Placeholder (needs API access) |
| Instagram | Graph API | ⚠️ Placeholder |
| Facebook | Graph API | ⚠️ Placeholder |
| Threads | Graph API | ⚠️ Placeholder |
| WhatsApp | Contact extraction | ⚠️ From other sources |
| Email | Extraction | ⚠️ From other sources |

## LLM Platform Research & Recommendation

### Comparison

| Provider | Model | API Cost (in/out per 1M) | Context Window | JSON Support | Recommendation |
|---|---|---|---|---|---|
| OpenAI | gpt-3.5-turbo | $0.50 / $1.50 | 16K | Yes | Best balance |
| OpenAI | gpt-4o-mini | $0.15 / $0.60 | 128K | Yes | Best balance (newer) |
| Google Gemini | gemini-1.5-flash | $0.075 / $0.30 | 1M | Yes | Cheapest, very fast |
| Anthropic Claude | claude-3-haiku | $0.25 / $1.25 | 200K | Yes | Fast, good accuracy |

*Pricing is approximate and based on public provider documentation. Verify current pricing before production use.*

### Recommended model

**Provider:** OpenAI  
**Model:** `gpt-3.5-turbo` (or `gpt-4o-mini` if available)  
**Estimated input tokens:** ~500 per query understanding + ~200 per relevance check  
**Estimated output tokens:** ~100 per query + ~50 per relevance  
**Estimated cost per discovery request:** ~$0.001–$0.003  
**Expected response time:** 1–3 seconds  
**Reason:** Fast, cheap, reliable structured JSON output via `response_format`, good query understanding.  
**Fallback:** `gemini-1.5-flash` (lowest cost, largest context).  
**No-key fallback:** Built-in rule-based query understanding works without any API key.

### Cost optimization
- Single LLM call for query understanding (reused for relevance)
- Rule-based fallback when no API key
- Deterministic validation instead of LLM calls for contact info
- Caching of query understanding results (implement Redis in production)

## Test queries

| No. | Search Query | Expected Audience |
|---|---|---|
| 1 | Football lovers in Washington DC in USA | Football enthusiasts |
| 2 | Digital marketing agency owners in New York USA | Marketing business owners |
| 3 | Startup founders in London UK | Startup founders |
| 4 | Cricket lovers in Ahmedabad India | Cricket enthusiasts |
| 5 | Restaurant owners in Dubai UAE | Restaurant business owners |

## Deployment

### Render (recommended for Python 3.11)

1. Push to GitHub
2. Render → New → Web Service → connect repo
3. Settings:
   - Runtime: Python 3.11 (via `runtime.txt`)
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add env vars: `OPENAI_API_KEY`, `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_CX`, `YOUTUBE_API_KEY`, `TWITTER_BEARER_TOKEN`
5. Deploy

### Railway (alternative)

1. railway.app → New Project → GitHub
2. Auto-detects `runtime.txt` (Python 3.11)
3. Add env vars
4. Deploy

## Testing

```bash
pip install pytest
pytest tests/
```

## Submission checklist

- [ ] Repo is **Public** on GitHub
- [ ] No `.env` with real keys committed (only `.env.example`)
- [ ] README has setup, sample request/response, LLM comparison
- [ ] Live demo URL works (`/docs` and `POST /prospect-discovery`)
- [ ] Followed Dxora on LinkedIn and CREST on Instagram
- [ ] Email sent to `hr@chivoxai.com` with:
  - Full Name
  - Demo Link
  - GitHub Repository Link
  - Contact Number
  - Current Location
  - LinkedIn Profile Link
  - Instagram Profile Link
  - Preferred Date and Time for Final Discussion

## Email template

**To:** hr@chivoxai.com  
**Subject:** Your Name - Python Practical Prospect Discovery Test Review  

**Body:**
```
1. Full Name: [Your Name]
2. Demo Link: https://your-app.up.railway.app (or Render URL)
3. Public GitHub Repository Link: https://github.com/YOURUSERNAME/linkAnalysis
4. Contact Number: [your number]
5. Current Location: [City, State]
6. LinkedIn Profile Link: [your LinkedIn profile]
7. Instagram Profile Link: [your Instagram profile]
8. Preferred Date and Time for Final Discussion: [your slot]
```