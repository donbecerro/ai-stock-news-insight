from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.models.schemas import HealthResponse, StockAnalysisResponse
from app.workflows.stock_workflow import LANGGRAPH_AVAILABLE, run_stock_analysis

settings = get_settings()
router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
    )


@router.get(
    "/analyze/{ticker}",
    response_model=StockAnalysisResponse,
    tags=["analysis"],
    summary="Analyze a stock using market data, news and AI workflow orchestration.",
)
async def analyze_stock(
    ticker: str,
    news_limit: int = Query(default=5, ge=1, le=10),
):
    try:
        return run_stock_analysis(ticker=ticker, news_limit=news_limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected analysis error: {exc}",
        ) from exc


@router.get("/workflow/status", tags=["workflow"])
async def workflow_status():
    return {
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "workflow": [
            "validate_ticker",
            "fetch_market_data",
            "fetch_news",
            "analyze_sentiment",
            "generate_insight",
        ],
    }
