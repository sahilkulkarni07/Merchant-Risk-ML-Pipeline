def test_llm_report_returns_text():
    dummy_row = {
        "merchant_id": 1,
        "country": "US",
        "risk_tier": "Medium",
        "risk_probability": 0.45,
        "monthly_volume": 20000,
        "transaction_count": 350,
        "dispute_count": 5
    }

    feature_importance = None  # or small dummy df
    portfolio_metrics = {
        "average_risk_probability": 0.40,
        "expected_high_risk_merchants": 15
    }

    from reporting.llm_report_generator import generate_llm_underwriting_report

    report = generate_llm_underwriting_report(dummy_row, feature_importance, portfolio_metrics)

    assert isinstance(report, str)
    assert len(report) > 100