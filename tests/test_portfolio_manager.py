"""Regression tests for the integrated dashboard portfolio manager."""

import asyncio
from copy import deepcopy
from types import SimpleNamespace

import pytest

from custom_components.portfolio_tracker.const import DOMAIN
from custom_components.portfolio_tracker.websocket_api import (
    PortfolioManagerError,
    _mutate,
    _revision,
    async_handle_manage,
)


def execute(holdings, action, **payload):
    return _mutate(holdings, action, {"payload": payload}, "CHF")


def add_asset(holdings, symbol="AAPL", **payload):
    return execute(holdings, "add_asset", symbol=symbol, **payload)


def add_trade(holdings, asset_id, **payload):
    defaults = {
        "asset_id": asset_id,
        "type": "buy",
        "date": "2026-10-01",
        "quantity": "5",
        "price": "100",
        "currency": "CHF",
    }
    return execute(holdings, "add_transaction", **{**defaults, **payload})


def test_add_watchlist_asset_and_reject_duplicate_symbol() -> None:
    holdings = []

    asset_id = add_asset(holdings, "novn.sw", watch_only=True)

    assert holdings[0]["holding_id"] == asset_id
    assert holdings[0]["symbol"] == "NOVN.SW"
    assert holdings[0]["watch_only"] is True
    assert holdings[0]["transactions"] == []
    with pytest.raises(PortfolioManagerError, match="already exists"):
        add_asset(holdings, "NOVN.SW")


def test_trade_moves_watchlist_asset_to_active_portfolio() -> None:
    holdings = []
    asset_id = add_asset(holdings, watch_only=True)

    add_trade(holdings, asset_id)

    assert holdings[0]["watch_only"] is False
    assert holdings[0]["transactions"][0]["transaction_price_mode"] == "per_unit"


def test_failed_oversell_is_atomic() -> None:
    holdings = []
    asset_id = add_asset(holdings, watch_only=False)
    before = deepcopy(holdings)

    with pytest.raises(PortfolioManagerError, match="negative historical"):
        add_trade(
            holdings,
            asset_id,
            type="sell",
            date="2026-09-01",
            quantity="1",
        )

    assert holdings == before


def test_reverse_dated_sell_is_rejected_without_partial_update() -> None:
    holdings = []
    asset_id = add_asset(holdings)
    add_trade(holdings, asset_id, date="2026-10-10", quantity="2")
    before = deepcopy(holdings)

    with pytest.raises(PortfolioManagerError, match="negative historical"):
        add_trade(
            holdings,
            asset_id,
            type="sell",
            date="2026-10-01",
            quantity="1",
        )

    assert holdings == before


def test_alerts_can_be_cleared_and_must_be_ordered() -> None:
    holdings = []
    asset_id = add_asset(holdings, "LOGN.SW")
    execute(holdings, "set_alerts", asset_id=asset_id, below=50, above=100)
    assert holdings[0]["alert_below"] == 50
    assert holdings[0]["alert_above"] == 100

    execute(holdings, "set_alerts", asset_id=asset_id, below="", above="")

    assert "alert_below" not in holdings[0]
    assert "alert_above" not in holdings[0]
    with pytest.raises(PortfolioManagerError, match="Lower alert"):
        execute(holdings, "set_alerts", asset_id=asset_id, below=100, above=50)


def test_history_requires_explicit_deletion_confirmation() -> None:
    holdings = []
    asset_id = add_asset(holdings)
    add_trade(holdings, asset_id)

    with pytest.raises(PortfolioManagerError, match="requires confirmation"):
        execute(holdings, "remove_asset", asset_id=asset_id)

    execute(
        holdings,
        "remove_asset",
        asset_id=asset_id,
        confirm_history=True,
    )
    assert holdings == []


def test_transaction_edit_preserves_and_updates_all_accounting_fields() -> None:
    holdings = []
    asset_id = add_asset(holdings, "NOVN.SW")
    add_trade(
        holdings,
        asset_id,
        price_mode="total",
        price="500",
        market_price="100",
        market_currency="CHF",
        exchange="SIX",
        note="Broker reference",
    )
    transaction = holdings[0]["transactions"][0]

    execute(
        holdings,
        "update_transaction",
        asset_id=asset_id,
        transaction_id=transaction["transaction_id"],
        type="buy",
        date="2026-10-01",
        quantity="5",
        price="550",
        price_mode="total",
        currency="CHF",
        market_price="110",
        market_currency="CHF",
        fees="2",
        taxes="3",
        exchange="SIX",
        note="Updated reference",
    )

    edited = holdings[0]["transactions"][0]
    assert edited["transaction_price_mode"] == "total"
    assert edited["transaction_price"] == 550
    assert edited["transaction_market_price"] == 110
    assert edited["transaction_exchange"] == "SIX"
    assert edited["transaction_note"] == "Updated reference"


def test_duplicate_client_transaction_id_is_rejected() -> None:
    holdings = []
    first = add_asset(holdings, "AAPL")
    second = add_asset(holdings, "MSFT")
    add_trade(holdings, first, transaction_id="request-one")

    with pytest.raises(PortfolioManagerError, match="already exists"):
        add_trade(holdings, second, transaction_id="request-one")


def test_duplicate_assets_are_consolidated_without_losing_history() -> None:
    holdings = [
        {
            "holding_id": "watched-copy",
            "symbol": "novn.sw",
            "name": "Novartis watchlist",
            "asset_type": "stock",
            "watch_only": True,
            "alert_below": 80,
            "transactions": [],
        },
        {
            "holding_id": "active-position",
            "symbol": "NOVN.SW",
            "name": "Novartis",
            "asset_type": "stock",
            "watch_only": False,
            "alert_above": 120,
            "transactions": [
                {
                    "transaction_id": "buy-one",
                    "transaction_type": "buy",
                    "transaction_date": "2026-01-10",
                    "quantity": 5,
                    "transaction_price": 90,
                    "transaction_price_mode": "per_unit",
                    "transaction_currency": "CHF",
                }
            ],
        },
    ]

    result = execute(holdings, "consolidate_duplicates", confirmed=True)

    assert result == "consolidated:1"
    assert len(holdings) == 1
    assert holdings[0]["holding_id"] == "active-position"
    assert holdings[0]["watch_only"] is False
    assert holdings[0]["alert_below"] == 80
    assert holdings[0]["alert_above"] == 120
    assert [item["transaction_id"] for item in holdings[0]["transactions"]] == [
        "buy-one"
    ]


def test_consolidation_deduplicates_copied_transaction_ids() -> None:
    transaction = {
        "transaction_id": "same-transaction",
        "transaction_type": "buy",
        "transaction_date": "2026-01-10",
        "quantity": 2,
        "transaction_price": 100,
        "transaction_price_mode": "per_unit",
        "transaction_currency": "CHF",
    }
    holdings = [
        {
            "holding_id": "first",
            "symbol": "AAPL",
            "name": "Apple",
            "asset_type": "stock",
            "watch_only": False,
            "transactions": [deepcopy(transaction)],
        },
        {
            "holding_id": "copy",
            "symbol": "aapl",
            "name": "Apple copy",
            "asset_type": "stock",
            "watch_only": False,
            "transactions": [deepcopy(transaction)],
        },
    ]

    execute(holdings, "consolidate_duplicates", confirmed=True)

    assert len(holdings) == 1
    assert len(holdings[0]["transactions"]) == 1


def test_consolidation_requires_confirmation_and_duplicates() -> None:
    holdings = [
        {
            "holding_id": "only",
            "symbol": "AAPL",
            "name": "Apple",
            "asset_type": "stock",
            "watch_only": True,
            "transactions": [],
        }
    ]
    before = deepcopy(holdings)

    with pytest.raises(PortfolioManagerError) as confirmation:
        execute(holdings, "consolidate_duplicates")
    assert confirmation.value.code == "consolidation_confirmation_required"
    with pytest.raises(PortfolioManagerError) as duplicates:
        execute(holdings, "consolidate_duplicates", confirmed=True)
    assert duplicates.value.code == "no_duplicates"
    assert holdings == before


def test_invalid_duplicate_history_is_not_partially_consolidated() -> None:
    holdings = [
        {
            "holding_id": "invalid-sale",
            "symbol": "TEST",
            "name": "Invalid sale",
            "asset_type": "stock",
            "watch_only": False,
            "transactions": [
                {
                    "transaction_id": "sell-first",
                    "transaction_type": "sell",
                    "transaction_date": "2026-01-01",
                    "quantity": 2,
                }
            ],
        },
        {
            "holding_id": "later-buy",
            "symbol": "test",
            "name": "Later buy",
            "asset_type": "stock",
            "watch_only": False,
            "transactions": [
                {
                    "transaction_id": "buy-later",
                    "transaction_type": "buy",
                    "transaction_date": "2026-02-01",
                    "quantity": 1,
                }
            ],
        },
    ]
    before = deepcopy(holdings)

    with pytest.raises(PortfolioManagerError) as error:
        execute(holdings, "consolidate_duplicates", confirmed=True)

    assert error.value.code == "duplicate_merge_invalid"
    assert holdings == before


def test_warrant_supports_swissquote_and_external_sensor_sources() -> None:
    holdings = []
    swiss_id = add_asset(
        holdings,
        "",
        asset_type="warrant",
        price_source="swissquote",
        trading_venue="six",
        valor="150558611",
        price_mode="midpoint",
        price_currency="CHF",
        warrant_type="call",
        strike="100",
        ratio="10",
        expiry="2027-12-31",
    )
    entity_id = add_asset(
        holdings,
        "BROKER-WARRANT",
        asset_type="warrant",
        price_source="entity",
        price_entity="sensor.broker_warrant",
        price_mode="bid",
        price_currency="CHF",
        trading_venue="other",
        warrant_type="put",
        strike="90",
        ratio="5",
        expiry="2027-06-30",
    )

    swiss = next(item for item in holdings if item["holding_id"] == swiss_id)
    external = next(item for item in holdings if item["holding_id"] == entity_id)
    assert swiss["symbol"] == "150558611"
    assert swiss["price_mode"] == "midpoint"
    assert external["price_entity"] == "sensor.broker_warrant"
    assert external["price_mode"] == "bid"


@pytest.mark.parametrize(
    ("payload", "error_code"),
    [
        (
            {
                "asset_type": "warrant",
                "price_source": "swissquote",
                "trading_venue": "six",
                "valor": "invalid",
                "warrant_type": "call",
                "strike": 1,
                "ratio": 1,
                "expiry": "2027-01-01",
            },
            "invalid_valor",
        ),
        (
            {
                "asset_type": "warrant",
                "price_source": "entity",
                "price_entity": "switch.not_a_price",
                "price_currency": "CHF",
                "trading_venue": "other",
                "warrant_type": "call",
                "strike": 1,
                "ratio": 1,
                "expiry": "2027-01-01",
            },
            "price_entity_required",
        ),
    ],
)
def test_invalid_warrant_configuration_is_rejected(payload, error_code) -> None:
    with pytest.raises(PortfolioManagerError) as error:
        add_asset([], "TEST", **payload)
    assert error.value.code == error_code


class _Connection:
    def __init__(self, *, is_admin: bool) -> None:
        self.user = SimpleNamespace(is_admin=is_admin)
        self.results: list[tuple[int, dict]] = []
        self.errors: list[tuple[int, str, str]] = []

    def send_result(self, message_id: int, result: dict) -> None:
        self.results.append((message_id, result))

    def send_error(self, message_id: int, code: str, message: str) -> None:
        self.errors.append((message_id, code, message))


class _ConfigEntries:
    def __init__(self, entry) -> None:
        self.entry = entry
        self.updates: list[dict] = []

    def async_get_entry(self, entry_id: str):
        return self.entry if entry_id == self.entry.entry_id else None

    def async_update_entry(self, entry, *, options: dict) -> None:
        entry.options = options
        self.updates.append(options)


def _hass_and_entry():
    entry = SimpleNamespace(
        entry_id="portfolio-1",
        domain=DOMAIN,
        data={"base_currency": "CHF"},
        options={"holdings": []},
    )
    config_entries = _ConfigEntries(entry)
    hass = SimpleNamespace(data={}, config_entries=config_entries)
    return hass, entry, config_entries


def test_websocket_rejects_non_admin_users() -> None:
    hass, _entry, config_entries = _hass_and_entry()
    connection = _Connection(is_admin=False)

    asyncio.run(
        async_handle_manage(
            hass,
            connection,
            {
                "id": 1,
                "entry_id": "portfolio-1",
                "action": "get_assets",
            },
        )
    )

    assert connection.errors[0][1] == "unauthorized"
    assert config_entries.updates == []


def test_websocket_detects_stale_manager_revision() -> None:
    hass, entry, config_entries = _hass_and_entry()
    connection = _Connection(is_admin=True)
    stale_revision = _revision([])
    entry.options["holdings"] = [
        {
            "holding_id": "existing",
            "symbol": "AAPL",
            "name": "Apple",
            "asset_type": "stock",
            "watch_only": True,
            "transactions": [],
        }
    ]

    asyncio.run(
        async_handle_manage(
            hass,
            connection,
            {
                "id": 2,
                "entry_id": "portfolio-1",
                "action": "add_asset",
                "revision": stale_revision,
                "payload": {"symbol": "MSFT", "watch_only": True},
            },
        )
    )

    assert connection.errors[0][1] == "conflict"
    assert config_entries.updates == []


def test_websocket_get_and_update_return_current_revision() -> None:
    hass, entry, config_entries = _hass_and_entry()
    connection = _Connection(is_admin=True)

    async def scenario() -> None:
        await async_handle_manage(
            hass,
            connection,
            {
                "id": 1,
                "entry_id": "portfolio-1",
                "action": "get_assets",
            },
        )
        revision = connection.results[-1][1]["revision"]
        await async_handle_manage(
            hass,
            connection,
            {
                "id": 2,
                "entry_id": "portfolio-1",
                "action": "add_asset",
                "revision": revision,
                "payload": {"symbol": "NESN.SW", "watch_only": True},
            },
        )

    asyncio.run(scenario())

    assert connection.errors == []
    assert len(config_entries.updates) == 1
    assert entry.options["holdings"][0]["symbol"] == "NESN.SW"
    assert connection.results[-1][1]["revision"] == _revision(
        entry.options["holdings"]
    )
