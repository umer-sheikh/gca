from gulf_climate_agent.core.normalization import infer_trend, summarize_numeric


def test_summarize_numeric_handles_none() -> None:
    summary = summarize_numeric([1, 2, None, 4])
    assert summary["count"] == 3
    assert summary["min"] == 1.0
    assert summary["max"] == 4.0


def test_infer_trend_increasing() -> None:
    trend = infer_trend([1, 2, 3])
    assert trend["direction"] == "increasing"
