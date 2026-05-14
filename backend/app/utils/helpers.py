from datetime import datetime, timezone
from typing import Any, Optional


def normalize_ticker(ticker: str) -> str:
    cleaned = ticker.strip().upper()
    if not cleaned:
        raise ValueError("Ticker cannot be empty.")
    if len(cleaned) > 12:
        raise ValueError("Ticker is too long. Use a valid stock ticker such as AAPL.")
    return cleaned


def safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def round_optional(value: Optional[float], digits: int = 2) -> Optional[float]:
    if value is None:
        return None
    return round(value, digits)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def truncate(text: str, max_length: int = 500) -> str:
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."
