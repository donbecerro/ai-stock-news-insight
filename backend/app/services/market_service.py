from typing import Dict, List

try:
    import yfinance as yf
except Exception:
    yf = None

from app.utils.helpers import normalize_ticker, round_optional


def _fallback_market_data(ticker: str) -> Dict:
    sample_history: List[Dict] = [
        {"date": "2026-01-05", "close": 188.20},
        {"date": "2026-01-06", "close": 189.10},
        {"date": "2026-01-07", "close": 187.80},
        {"date": "2026-01-08", "close": 190.30},
        {"date": "2026-01-09", "close": 191.40},
    ]
    latest = sample_history[-1]["close"]
    previous = sample_history[-2]["close"]
    change_percent = ((latest - previous) / previous) * 100

    return {
        "ticker": ticker,
        "latest_close": round_optional(latest),
        "previous_close": round_optional(previous),
        "change_percent": round_optional(change_percent),
        "currency": "USD",
        "provider": "fallback-sample",
        "data_quality": "demo",
        "history": sample_history,
    }


def get_stock_data(ticker: str) -> Dict:
    """Retrieve recent market data for a stock ticker.

    yfinance is used for the MVP. If it fails because of network issues,
    invalid responses or rate limits, this function returns deterministic
    fallback data so the backend remains demo-friendly.
    """
    normalized_ticker = normalize_ticker(ticker)

    if yf is None:
        return _fallback_market_data(normalized_ticker)

    try:
        stock = yf.Ticker(normalized_ticker)
        history = stock.history(period="1mo", interval="1d", auto_adjust=False)

        if history is None or history.empty or "Close" not in history:
            return _fallback_market_data(normalized_ticker)

        history = history.dropna(subset=["Close"])
        if history.empty:
            return _fallback_market_data(normalized_ticker)

        closes = history["Close"]
        latest_close = float(closes.iloc[-1])
        previous_close = float(closes.iloc[-2]) if len(closes) > 1 else latest_close
        change_percent = (
            ((latest_close - previous_close) / previous_close) * 100
            if previous_close
            else 0.0
        )

        history_points = []
        for index, row in history.tail(10).iterrows():
            date_value = getattr(index, "strftime", lambda fmt: str(index))("%Y-%m-%d")
            history_points.append(
                {
                    "date": date_value,
                    "close": round(float(row["Close"]), 2),
                }
            )

        return {
            "ticker": normalized_ticker,
            "latest_close": round_optional(latest_close),
            "previous_close": round_optional(previous_close),
            "change_percent": round_optional(change_percent),
            "currency": "USD",
            "provider": "yfinance",
            "data_quality": "live_or_cached",
            "history": history_points,
        }
    except Exception:
        return _fallback_market_data(normalized_ticker)
