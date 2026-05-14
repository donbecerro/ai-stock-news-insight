from typing import Dict

from app.services.news_service import get_news


def run_news_agent(state: Dict) -> Dict:
    ticker = state["ticker"]
    limit = state.get("news_limit", 5)
    news_items = get_news(ticker, limit=limit)

    if news_items:
        news_summary = " ".join(item.get("title", "") for item in news_items[:3]).strip()
    else:
        news_summary = "No recent news found."

    return {
        "news": news_items,
        "news_summary": news_summary,
    }
