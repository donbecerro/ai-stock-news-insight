from datetime import datetime, timedelta, timezone
from typing import Dict, List

import requests

from app.config import get_settings
from app.utils.helpers import normalize_ticker, truncate

settings = get_settings()


def _fallback_news(ticker: str) -> List[Dict]:
    return [
        {
            "title": f"{ticker} remains in focus as investors evaluate market momentum",
            "summary": "Recent market discussion highlights valuation, earnings expectations and broader macroeconomic uncertainty.",
            "source": "fallback-demo",
            "url": None,
            "published_at": None,
        },
        {
            "title": f"Analysts review near-term outlook for {ticker}",
            "summary": "Commentary remains mixed, with attention on revenue growth, margins, interest rates and sector-level risk.",
            "source": "fallback-demo",
            "url": None,
            "published_at": None,
        },
        {
            "title": f"Market volatility could influence {ticker} performance",
            "summary": "Investors continue to monitor news flow, liquidity conditions and company-specific catalysts.",
            "source": "fallback-demo",
            "url": None,
            "published_at": None,
        },
    ]


def _get_newsapi_articles(ticker: str, limit: int) -> List[Dict]:
    if not settings.news_api_key:
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": ticker,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": settings.news_api_key,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()

    articles = []
    for article in payload.get("articles", [])[:limit]:
        articles.append(
            {
                "title": article.get("title") or "Untitled article",
                "summary": truncate(article.get("description") or article.get("content") or ""),
                "source": (article.get("source") or {}).get("name"),
                "url": article.get("url"),
                "published_at": article.get("publishedAt"),
            }
        )
    return articles


def _get_finnhub_articles(ticker: str, limit: int) -> List[Dict]:
    if not settings.finnhub_api_key:
        return []

    to_date = datetime.now(timezone.utc).date()
    from_date = to_date - timedelta(days=7)
    url = "https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": ticker,
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "token": settings.finnhub_api_key,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()

    articles = []
    for article in payload[:limit]:
        timestamp = article.get("datetime")
        published_at = None
        if timestamp:
            published_at = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

        articles.append(
            {
                "title": article.get("headline") or "Untitled article",
                "summary": truncate(article.get("summary") or ""),
                "source": article.get("source"),
                "url": article.get("url"),
                "published_at": published_at,
            }
        )
    return articles


def get_news(ticker: str, limit: int = 5) -> List[Dict]:
    normalized_ticker = normalize_ticker(ticker)

    try:
        articles = _get_newsapi_articles(normalized_ticker, limit)
        if articles:
            return articles
    except Exception:
        pass

    try:
        articles = _get_finnhub_articles(normalized_ticker, limit)
        if articles:
            return articles
    except Exception:
        pass

    return _fallback_news(normalized_ticker)[:limit]
