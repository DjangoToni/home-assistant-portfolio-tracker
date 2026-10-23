"""Regression tests for the integrated dashboard portfolio editor."""
import pytest

from custom_components.portfolio_tracker.websocket_api import _mutate


def execute(holdings, action, **payload):
    return _mutate(holdings, action, {"payload": payload}, "CHF")


def test_add_to_watchlist():
    holdings = []
    ident = execute(holdings, "add_asset", symbol="NOVN.SW", watch_only=True)
    assert holdings[0]["holding_id"] == ident
    assert holdings[0]["watch_only"]
    assert holdings[0]["transactions"] == []


def test_duplicate_symbol_rejected():
    holdings = []
    execute(holdings, "add_asset", symbol="AAPL")
    with pytest.raises(ValueError, match="bereits"):
        execute(holdings, "add_asset", symbol="aapl")


def test_trade_moves_watchlist_to_depot():
    holdings = []
    ident = execute(holdings, "add_asset", symbol="AAPL")
    execute(holdings, "add_transaction", asset_id=ident, type="buy", date="2026-10-01",
            quantity="5", price="200", currency="USD", fees="1")
    assert not holdings[0]["watch_only"]
    assert len(holdings[0]["transactions"]) == 1


def test_oversell_rejected_before_persist():
    holdings = []
    ident = execute(holdings, "add_asset", symbol="AAPL", watch_only=False)
    with pytest.raises(ValueError, match="negativen"):
        execute(holdings, "add_transaction", asset_id=ident, type="sell",
                date="2026-10-01", quantity="1", price="200")


def test_reverse_dated_sell_rejected():
    holdings = []
    ident = execute(holdings, "add_asset", symbol="AAPL")
    execute(holdings, "add_transaction", asset_id=ident, type="buy",
            date="2026-10-10", quantity="2", price="100")
    with pytest.raises(ValueError, match="negativen"):
        execute(holdings, "add_transaction", asset_id=ident, type="sell",
                date="2026-10-01", quantity="1", price="120")


def test_alert_can_be_cleared():
    holdings = []
    ident = execute(holdings, "add_asset", symbol="LOGN.SW")
    execute(holdings, "set_alerts", asset_id=ident, below=50, above=100)
    assert holdings[0]["alert_above"] == 100
    execute(holdings, "set_alerts", asset_id=ident, below="", above="")
    assert "alert_above" not in holdings[0]
    assert "alert_below" not in holdings[0]


def test_alert_order_validation():
    holdings = []
    ident = execute(holdings, "add_asset", symbol="LOGN.SW")
    with pytest.raises(ValueError, match="kleiner"):
        execute(holdings, "set_alerts", asset_id=ident, below=100, above=50)


def test_removing_history_requires_confirmation():
    holdings = []
    ident = execute(holdings, "add_asset", symbol="AAPL")
    execute(holdings, "add_transaction", asset_id=ident, type="buy",
            date="2026-10-01", quantity="2", price="100")
    with pytest.raises(ValueError, match="bestätigt"):
        execute(holdings, "remove_asset", asset_id=ident)
