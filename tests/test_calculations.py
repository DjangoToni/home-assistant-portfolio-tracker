"""Tests for portfolio and performance calculations."""

from datetime import UTC, datetime
from decimal import Decimal

from custom_components.portfolio_tracker.calculator import (
    holding_alert_price,
    holding_cost,
    holding_gain,
    holding_value,
    portfolio_daily_percent,
    portfolio_holdings,
    portfolio_value,
    professional_holdings,
)
from custom_components.portfolio_tracker.models import (
    PortfolioData,
    Quote,
    StockHistoryPoint,
)
from custom_components.portfolio_tracker.performance import build_performance_report


def _quote(
    symbol: str,
    price: str,
    previous: str | None,
    currency: str,
) -> Quote:
    return Quote(
        symbol=symbol,
        name=symbol,
        price=Decimal(price),
        previous_close=Decimal(previous) if previous is not None else None,
        currency=currency,
        exchange="TEST",
        instrument_type="EQUITY",
        timestamp=None,
    )


def _transaction(day: str, quantity: float, price: float) -> dict:
    return {
        "transaction_id": day,
        "transaction_type": "buy",
        "transaction_date": day,
        "quantity": quantity,
        "transaction_price": price,
        "transaction_price_mode": "per_unit",
        "transaction_market_price": 0,
        "transaction_market_currency": "",
        "transaction_currency": "USD",
        "transaction_fees": 0,
        "transaction_taxes": 0,
        "transaction_exchange": "",
        "transaction_note": "",
    }


def test_portfolio_value_cost_and_gain_use_exchange_rates() -> None:
    holding = {
        "symbol": "ACME",
        "asset_type": "stock",
        "transactions": [_transaction("2026-01-01", 2, 100)],
    }
    data = PortfolioData(
        quotes={"ACME": _quote("ACME", "125", "120", "USD")},
        fx_rates={"CHF": Decimal("1"), "USD": Decimal("0.9")},
        base_currency="CHF",
    )

    assert holding_value(data, holding) == Decimal("225.0")
    assert holding_cost(data, holding) == Decimal("180.0")
    assert holding_gain(data, holding) == Decimal("45.0")
    assert portfolio_value(data, [holding]) == Decimal("225.0")


def test_watchlist_and_external_assets_are_filtered() -> None:
    active = {"symbol": "A", "asset_type": "stock"}
    watched = {"symbol": "B", "asset_type": "stock", "watch_only": True}
    external = {
        "symbol": "C",
        "asset_type": "warrant",
        "price_source": "entity",
    }
    crypto = {"symbol": "BTC-USD", "asset_type": "crypto"}

    assert portfolio_holdings([active, watched]) == [active]
    assert professional_holdings([active, watched, external, crypto]) == [active]


def test_crypto_alert_price_uses_display_currency() -> None:
    holding = {
        "symbol": "BTC-USD",
        "asset_type": "crypto",
        "display_currency": "CHF",
    }
    data = PortfolioData(
        quotes={"BTC-USD": _quote("BTC-USD", "60000", "59000", "USD")},
        fx_rates={"CHF": Decimal("1"), "USD": Decimal("0.9")},
        base_currency="CHF",
    )

    assert holding_alert_price(data, holding) == Decimal("54000.0")


def test_daily_portfolio_change_requires_complete_data() -> None:
    holdings = [
        {"symbol": "A", "quantity": 1, "average_price": 1},
        {"symbol": "B", "quantity": 1, "average_price": 1},
    ]
    data = PortfolioData(
        quotes={
            "A": _quote("A", "110", "100", "CHF"),
            "B": _quote("B", "50", None, "CHF"),
        },
        fx_rates={"CHF": Decimal("1")},
        base_currency="CHF",
    )

    assert portfolio_daily_percent(data, holdings) is None


def test_time_weighted_return_neutralizes_cash_flow() -> None:
    holding = {
        "symbol": "ACME",
        "asset_type": "stock",
        "transactions": [
            _transaction("2026-01-01", 1, 100),
            _transaction("2026-01-02", 1, 110),
        ],
    }

    def point(day: int, close: str) -> StockHistoryPoint:
        return StockHistoryPoint(
            timestamp=datetime(2026, 1, day, tzinfo=UTC),
            open=None,
            high=None,
            low=None,
            close=Decimal(close),
            volume=None,
        )

    data = PortfolioData(
        quotes={"ACME": _quote("ACME", "121", "110", "USD")},
        fx_rates={"USD": Decimal("1")},
        base_currency="USD",
        stock_history={
            "ACME": (point(1, "100"), point(2, "110"), point(3, "121")),
            "^TEST": (point(1, "100"), point(2, "105"), point(3, "110")),
        },
    )

    report = build_performance_report(data, [holding], "^TEST", "USD")

    assert report.time_weighted_return == Decimal("21.00")
    assert report.benchmark_return == Decimal("10.0")
    assert report.excess_return == Decimal("11.00")
    assert len(report.points) == 3
