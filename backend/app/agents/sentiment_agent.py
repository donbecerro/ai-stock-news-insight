from typing import Dict, Iterable, List

POSITIVE_TERMS = {
    "beat",
    "beats",
    "growth",
    "strong",
    "positive",
    "surge",
    "rally",
    "upgrade",
    "profit",
    "profits",
    "optimistic",
    "momentum",
    "record",
    "outperform",
}

NEGATIVE_TERMS = {
    "miss",
    "misses",
    "decline",
    "weak",
    "negative",
    "drop",
    "selloff",
    "downgrade",
    "loss",
    "losses",
    "risk",
    "lawsuit",
    "investigation",
    "warning",
    "underperform",
}


def _tokenize(items: Iterable[str]) -> List[str]:
    text = " ".join(items).lower()
    for char in ",.;:!?()[]{}\"'":
        text = text.replace(char, " ")
    return [token.strip() for token in text.split() if token.strip()]


def run_sentiment_agent(state: Dict) -> Dict:
    news_items = state.get("news", [])
    texts = []
    for item in news_items:
        texts.append(item.get("title", ""))
        texts.append(item.get("summary", ""))

    tokens = _tokenize(texts)
    if not tokens:
        return {"sentiment": "neutral", "sentiment_score": 0.0}

    positive_hits = sum(1 for token in tokens if token in POSITIVE_TERMS)
    negative_hits = sum(1 for token in tokens if token in NEGATIVE_TERMS)
    total_hits = positive_hits + negative_hits

    if total_hits == 0:
        score = 0.0
    else:
        score = (positive_hits - negative_hits) / total_hits

    if score > 0.2:
        sentiment = "positive"
    elif score < -0.2:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "sentiment_score": round(score, 2),
    }
