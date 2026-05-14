# AI Stock News Insight - Backend

FastAPI backend for the `ai-stock-news-insight` project.

This backend contains the core AI workflow of the project:

- stock market data ingestion with `yfinance`,
- financial news ingestion with NewsAPI or Finnhub,
- sentiment analysis,
- LangGraph workflow orchestration,
- LLM-based market insight generation,
- and a REST API consumed by the Next.js frontend.

The backend is intentionally designed as a small but realistic AI engineering MVP: simple enough to run locally, but structured like a production-ready service that can later be deployed to AWS ECS or Azure Container Apps.

---

## Why this backend matters

The most important part of the project is here because this service owns:

1. Data acquisition
2. AI orchestration
3. Agentic workflow design
4. Business logic
5. API contract for the frontend

The frontend displays the product experience, but this backend is where the AI reasoning workflow lives.

---

## Architecture

```text
User / Frontend
      |
      v
FastAPI REST API
      |
      v
LangGraph Workflow
      |
      +--> Market data service: yfinance
      +--> News service: NewsAPI / Finnhub / fallback mock news
      +--> Sentiment agent
      +--> Insight agent
      +--> LLM service: OpenAI / Azure OpenAI / local heuristic fallback
      |
      v
Structured JSON response
```

---

## Why FastAPI

FastAPI is used because it is lightweight, Python-native, easy to containerize, and integrates naturally with AI tooling such as LangGraph, LangChain, yfinance and OpenAI-compatible APIs.

It also provides automatic OpenAPI documentation at:

```text
http://localhost:8000/docs
```

---

## Why LangGraph

LangGraph is used to make the AI logic explicit as a workflow instead of hiding everything inside one large prompt.

The current MVP workflow is:

```text
validate_ticker
      |
      v
fetch_market_data
      |
      v
fetch_news
      |
      v
analyze_sentiment
      |
      v
generate_insight
```

This makes the system easier to extend with future agents, such as:

- risk agent,
- macro events agent,
- technical analysis agent,
- portfolio agent,
- human-in-the-loop review agent.

---

## Why yfinance

`yfinance` is a Python package for retrieving market data from Yahoo Finance.

The `y` stands for Yahoo Finance. It is not a typo.

In this MVP, yfinance is used because it is fast to prototype with and does not require an API key. The architecture keeps this dependency isolated inside `services/market_service.py`, so it can later be replaced by a production-grade provider such as:

- Polygon,
- Finnhub,
- Alpha Vantage,
- Bloomberg,
- Refinitiv.

---

## Project structure

```text
backend/
|
|-- app/
|   |-- main.py
|   |-- config.py
|   |
|   |-- api/
|   |   |-- routes.py
|   |
|   |-- agents/
|   |   |-- news_agent.py
|   |   |-- sentiment_agent.py
|   |   |-- insight_agent.py
|   |
|   |-- services/
|   |   |-- market_service.py
|   |   |-- news_service.py
|   |   |-- llm_service.py
|   |
|   |-- workflows/
|   |   |-- stock_workflow.py
|   |
|   |-- models/
|   |   |-- schemas.py
|   |
|   |-- utils/
|       |-- helpers.py
|
|-- tests/
|-- requirements.txt
|-- Dockerfile
|-- docker-compose.yml
|-- .env.example
```

---

## Local setup

From the `backend/` folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

---

## Run with Docker

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Swagger docs:

```text
http://localhost:8000/docs
```

---

## Main endpoint

```http
GET /api/analyze/{ticker}
```

Example:

```bash
curl http://localhost:8000/api/analyze/AAPL
```

Example response:

```json
{
  "ticker": "AAPL",
  "market_summary": "AAPL last close was 192.53 USD, with a 0.84% move versus the previous close.",
  "market_data": {
    "ticker": "AAPL",
    "latest_close": 192.53,
    "previous_close": 190.92,
    "change_percent": 0.84,
    "currency": "USD",
    "provider": "yfinance",
    "data_quality": "live_or_cached",
    "history": []
  },
  "news": [],
  "news_summary": "Recent coverage is mixed and should be reviewed together with market volatility.",
  "sentiment": "neutral",
  "sentiment_score": 0.0,
  "recommendation": "Neutral",
  "confidence": 0.58,
  "risk_notes": [
    "This is an AI-generated educational insight, not financial advice."
  ],
  "generated_by": "heuristic-fallback"
}
```

---

## Environment variables

The service works without API keys using fallback demo data and heuristic analysis.

For richer behavior, configure the following variables in `.env`:

```bash
APP_ENV=local
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_VERSION=2024-02-15-preview
NEWS_API_KEY=
FINNHUB_API_KEY=
CORS_ORIGINS=http://localhost:3000
```

---

## Fallback behavior

This backend is designed to run even without external paid services:

- If NewsAPI/Finnhub keys are missing, it returns sample news.
- If OpenAI/Azure OpenAI keys are missing, it uses a deterministic heuristic insight generator.
- If yfinance fails or the network is unavailable, it returns sample market data.

This is intentional for a portfolio MVP: the system can be demonstrated immediately while still showing a realistic enterprise architecture.

---

## Tests

```bash
pytest
```

---

## Disclaimer

This project is for educational and portfolio purposes only. It does not provide financial advice, investment recommendations or trading instructions.
