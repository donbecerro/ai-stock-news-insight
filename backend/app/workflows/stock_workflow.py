from typing import Any, Dict, List, Optional, TypedDict

from app.agents.insight_agent import run_insight_agent
from app.agents.news_agent import run_news_agent
from app.agents.sentiment_agent import run_sentiment_agent
from app.services.market_service import get_stock_data
from app.utils.helpers import normalize_ticker

try:
    from langgraph.graph import END, START, StateGraph

    LANGGRAPH_AVAILABLE = True
except Exception:
    END = "__end__"
    START = "__start__"
    StateGraph = None
    LANGGRAPH_AVAILABLE = False


class StockAnalysisState(TypedDict, total=False):
    ticker: str
    news_limit: int
    market_data: Dict[str, Any]
    news: List[Dict[str, Any]]
    news_summary: str
    sentiment: str
    sentiment_score: float
    insight: Dict[str, Any]


def validate_ticker_node(state: StockAnalysisState) -> Dict[str, Any]:
    return {"ticker": normalize_ticker(state["ticker"])}


def fetch_market_data_node(state: StockAnalysisState) -> Dict[str, Any]:
    return {"market_data": get_stock_data(state["ticker"])}


def fetch_news_node(state: StockAnalysisState) -> Dict[str, Any]:
    return run_news_agent(state)


def analyze_sentiment_node(state: StockAnalysisState) -> Dict[str, Any]:
    return run_sentiment_agent(state)


def generate_insight_node(state: StockAnalysisState) -> Dict[str, Any]:
    return run_insight_agent(state)


def _build_graph():
    if not LANGGRAPH_AVAILABLE:
        return None

    graph = StateGraph(StockAnalysisState)
    graph.add_node("validate_ticker", validate_ticker_node)
    graph.add_node("fetch_market_data", fetch_market_data_node)
    graph.add_node("fetch_news", fetch_news_node)
    graph.add_node("analyze_sentiment", analyze_sentiment_node)
    graph.add_node("generate_insight", generate_insight_node)

    graph.add_edge(START, "validate_ticker")
    graph.add_edge("validate_ticker", "fetch_market_data")
    graph.add_edge("fetch_market_data", "fetch_news")
    graph.add_edge("fetch_news", "analyze_sentiment")
    graph.add_edge("analyze_sentiment", "generate_insight")
    graph.add_edge("generate_insight", END)

    return graph.compile()


STOCK_ANALYSIS_GRAPH = _build_graph()


def _run_without_langgraph(ticker: str, news_limit: int) -> StockAnalysisState:
    state: StockAnalysisState = {"ticker": normalize_ticker(ticker), "news_limit": news_limit}
    state.update(fetch_market_data_node(state))
    state.update(fetch_news_node(state))
    state.update(analyze_sentiment_node(state))
    state.update(generate_insight_node(state))
    return state


def _to_response(state: StockAnalysisState) -> Dict[str, Any]:
    insight = state.get("insight", {})
    return {
        "ticker": state["ticker"],
        "market_summary": insight.get("market_summary", ""),
        "market_data": state.get("market_data", {}),
        "news": state.get("news", []),
        "news_summary": insight.get("news_summary") or state.get("news_summary", ""),
        "sentiment": insight.get("sentiment", state.get("sentiment", "neutral")),
        "sentiment_score": insight.get(
            "sentiment_score", state.get("sentiment_score", 0.0)
        ),
        "recommendation": insight.get("recommendation", "Neutral"),
        "confidence": insight.get("confidence", 0.5),
        "risk_notes": insight.get("risk_notes", []),
        "generated_by": insight.get(
            "generated_by",
            "langgraph" if LANGGRAPH_AVAILABLE else "sequential-fallback",
        ),
        "disclaimer": insight.get(
            "disclaimer",
            "This is an AI-generated educational insight, not financial advice.",
        ),
    }


def run_stock_analysis(ticker: str, news_limit: int = 5) -> Dict[str, Any]:
    normalized_ticker = normalize_ticker(ticker)
    bounded_limit = max(1, min(int(news_limit), 10))

    if STOCK_ANALYSIS_GRAPH is not None:
        final_state: StockAnalysisState = STOCK_ANALYSIS_GRAPH.invoke(
            {"ticker": normalized_ticker, "news_limit": bounded_limit}
        )
    else:
        final_state = _run_without_langgraph(normalized_ticker, bounded_limit)

    return _to_response(final_state)
