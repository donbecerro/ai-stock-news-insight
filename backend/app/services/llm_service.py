import json
from typing import Dict, List

from app.config import get_settings

settings = get_settings()

DISCLAIMER = (
    "This is an AI-generated educational insight, not financial advice. "
    "Do not use it as the sole basis for investment or trading decisions."
)


def _format_news(news_items: List[Dict]) -> str:
    if not news_items:
        return "No recent news items were available."
    lines = []
    for item in news_items[:5]:
        title = item.get("title", "Untitled")
        summary = item.get("summary", "")
        lines.append(f"- {title}: {summary}")
    return "\n".join(lines)


def _heuristic_recommendation(market_data: Dict, sentiment_score: float) -> Dict:
    change_percent = market_data.get("change_percent") or 0.0
    combined_score = sentiment_score + (change_percent / 10.0)

    if combined_score > 0.25:
        recommendation = "Bullish"
    elif combined_score < -0.25:
        recommendation = "Bearish"
    else:
        recommendation = "Neutral"

    confidence = min(0.86, 0.55 + abs(combined_score) * 0.2)
    return {
        "recommendation": recommendation,
        "confidence": round(confidence, 2),
    }


def _fallback_insight(
    ticker: str,
    market_data: Dict,
    news_items: List[Dict],
    sentiment: str,
    sentiment_score: float,
) -> Dict:
    latest = market_data.get("latest_close")
    previous = market_data.get("previous_close")
    change = market_data.get("change_percent")
    currency = market_data.get("currency", "USD")

    if latest is not None and previous is not None and change is not None:
        market_summary = (
            f"{ticker} last close was {latest} {currency}, with a "
            f"{change}% move versus the previous close."
        )
    else:
        market_summary = f"Market data for {ticker} is currently limited."

    if news_items:
        top_titles = "; ".join(item.get("title", "") for item in news_items[:3])
        news_summary = f"Recent news themes include: {top_titles}."
    else:
        news_summary = "No recent news items were available for analysis."

    rec = _heuristic_recommendation(market_data, sentiment_score)

    return {
        "market_summary": market_summary,
        "news_summary": news_summary,
        "sentiment": sentiment,
        "sentiment_score": round(float(sentiment_score), 2),
        "recommendation": rec["recommendation"],
        "confidence": rec["confidence"],
        "risk_notes": [
            "Market data and news sentiment can change rapidly.",
            "The analysis may not include all relevant financial, macroeconomic or company-specific information.",
            DISCLAIMER,
        ],
        "generated_by": "heuristic-fallback",
        "disclaimer": DISCLAIMER,
    }


def _openai_insight(
    ticker: str,
    market_data: Dict,
    news_items: List[Dict],
    sentiment: str,
    sentiment_score: float,
) -> Dict:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = _build_prompt(ticker, market_data, news_items, sentiment, sentiment_score)

    response = client.chat.completions.create(
        model=settings.openai_model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a cautious financial market intelligence assistant. "
                    "You produce structured educational analysis, not financial advice."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    data["generated_by"] = f"openai:{settings.openai_model}"
    data["disclaimer"] = DISCLAIMER
    return data


def _azure_openai_insight(
    ticker: str,
    market_data: Dict,
    news_items: List[Dict],
    sentiment: str,
    sentiment_score: float,
) -> Dict:
    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
    )
    prompt = _build_prompt(ticker, market_data, news_items, sentiment, sentiment_score)

    response = client.chat.completions.create(
        model=settings.azure_openai_deployment,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a cautious financial market intelligence assistant. "
                    "You produce structured educational analysis, not financial advice."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    data["generated_by"] = f"azure-openai:{settings.azure_openai_deployment}"
    data["disclaimer"] = DISCLAIMER
    return data


def _build_prompt(
    ticker: str,
    market_data: Dict,
    news_items: List[Dict],
    sentiment: str,
    sentiment_score: float,
) -> str:
    return f"""
Analyze the following stock market context and return strict JSON.

Ticker: {ticker}
Market data: {json.dumps(market_data, ensure_ascii=False)}
Sentiment label: {sentiment}
Sentiment score: {sentiment_score}
News:
{_format_news(news_items)}

Return only a JSON object with these fields:
- market_summary: string
- news_summary: string
- sentiment: one of positive, neutral, negative
- sentiment_score: number between -1 and 1
- recommendation: one of Bullish, Neutral, Bearish
- confidence: number between 0 and 1
- risk_notes: array of strings

Rules:
- Do not provide financial advice.
- Mention uncertainty and risk.
- Keep the response concise and executive-friendly.
""".strip()


def _normalize_llm_output(
    ticker: str,
    data: Dict,
    market_data: Dict,
    news_items: List[Dict],
    sentiment: str,
    sentiment_score: float,
) -> Dict:
    fallback = _fallback_insight(ticker, market_data, news_items, sentiment, sentiment_score)
    normalized = dict(fallback)
    normalized.update({k: v for k, v in data.items() if v is not None})

    if "risk_notes" not in normalized or not isinstance(normalized["risk_notes"], list):
        normalized["risk_notes"] = fallback["risk_notes"]

    normalized["sentiment_score"] = float(normalized.get("sentiment_score", sentiment_score))
    normalized["confidence"] = float(normalized.get("confidence", fallback["confidence"]))
    normalized["disclaimer"] = DISCLAIMER
    return normalized


def generate_insight(
    ticker: str,
    market_data: Dict,
    news_items: List[Dict],
    sentiment: str,
    sentiment_score: float,
) -> Dict:
    try:
        if (
            settings.azure_openai_api_key
            and settings.azure_openai_endpoint
            and settings.azure_openai_deployment
        ):
            data = _azure_openai_insight(
                ticker, market_data, news_items, sentiment, sentiment_score
            )
            return _normalize_llm_output(
                ticker, data, market_data, news_items, sentiment, sentiment_score
            )

        if settings.openai_api_key:
            data = _openai_insight(ticker, market_data, news_items, sentiment, sentiment_score)
            return _normalize_llm_output(
                ticker, data, market_data, news_items, sentiment, sentiment_score
            )
    except Exception:
        pass

    return _fallback_insight(ticker, market_data, news_items, sentiment, sentiment_score)
