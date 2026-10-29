
from app.analytics import (
    get_total_revenue,
    get_top_product,
    get_monthly_revenue,
    get_top_region,
    compare_months,
)


def test_total_revenue():
    result = get_total_revenue()
    assert result["total_revenue"] == 1439200.0
    assert result["eligible_transactions"] == 48


def test_top_product():
    result = get_top_product()
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["Product"] == "Monitor"
    assert result[0]["revenue"] == 473000


def test_monthly_revenue():
    result = get_monthly_revenue()
    assert len(result) == 6


def test_top_region():
    result = get_top_region()
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["Region"] == "South"
    assert result[0]["revenue"] == 411200


def test_month_comparison():
    result = compare_months("2026-01", "2026-02")
    assert isinstance(result, dict)
    assert result["month1"] == "2026-01"
    assert result["month2"] == "2026-02"
