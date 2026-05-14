from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class HistoricalPrice(BaseModel):
    date: str
    close: float


class MarketData(BaseModel):
    ticker: str
    latest_close: Optional[float] = None
    previous_close: Optional[float] = None
    change_percent: Optional[float] = None
    currency: str = "USD"
    provider: str = "unknown"
    data_quality: str = "unknown"
    history: List[HistoricalPrice] = Field(default_factory=list)


class NewsItem(BaseModel):
    title: str
    summary: str = ""
    source: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[str] = None


class StockAnalysisResponse(BaseModel):
    ticker: str
    market_summary: str
    market_data: MarketData
    news: List[NewsItem]
    news_summary: str
    sentiment: str
    sentiment_score: float
    recommendation: str
    confidence: float
    risk_notes: List[str]
    generated_by: str
    disclaimer: str
