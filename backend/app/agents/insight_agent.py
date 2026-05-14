from typing import Dict

from app.services.llm_service import generate_insight


def run_insight_agent(state: Dict) -> Dict:
    insight = generate_insight(
        ticker=state["ticker"],
        market_data=state["market_data"],
        news_items=state.get("news", []),
        sentiment=state.get("sentiment", "neutral"),
        sentiment_score=state.get("sentiment_score", 0.0),
    )
    return {"insight": insight}
