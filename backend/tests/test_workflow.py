from app.workflows.stock_workflow import run_stock_analysis


def test_stock_workflow_returns_expected_contract():
    result = run_stock_analysis("AAPL", news_limit=2)

    assert result["ticker"] == "AAPL"
    assert "market_data" in result
    assert "news" in result
    assert "recommendation" in result
    assert result["recommendation"] in {"Bullish", "Neutral", "Bearish"}
    assert "disclaimer" in result
