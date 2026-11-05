"""Tests for coordinator normalization and price-alert delivery."""

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace

import custom_components.portfolio_tracker.coordinator as coordinator_module
from custom_components.portfolio_tracker.coordinator import PortfolioCoordinator
from custom_components.portfolio_tracker.models import PortfolioData, Quote


class _States:
    def __init__(self, state) -> None:
        self._state = state

    def get(self, _entity_id: str):
        return self._state


class _Services:
    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.fail = False
        self.fail_targets: set[str] = set()

    async def async_call(self, domain, service, data, **kwargs) -> None:
        self.calls.append((domain, service, data, kwargs))
        target = kwargs.get("target", {}).get("entity_id", [None])[0]
        if self.fail or target in self.fail_targets:
            raise RuntimeError("temporary notify failure")


def _coordinator(hass, options: dict | None = None) -> PortfolioCoordinator:
    instance = PortfolioCoordinator.__new__(PortfolioCoordinator)
    instance.hass = hass
    instance.entry = SimpleNamespace(
        entry_id="portfolio-1",
        data={},
        options=options or {},
    )
    instance._active_alerts = set()
    instance._mobile_alerts = set()
    return instance


def _data(price: str) -> PortfolioData:
    return PortfolioData(
        quotes={
            "TEST": Quote(
                symbol="TEST",
                name="Test Asset",
                price=Decimal(price),
                previous_close=Decimal("100"),
                currency="CHF",
                exchange="TEST",
                instrument_type="EQUITY",
                timestamp=None,
            )
        },
        fx_rates={"CHF": Decimal("1")},
        base_currency="CHF",
    )


def test_external_midpoint_quote_is_normalized() -> None:
    state = SimpleNamespace(
        state="10",
        name="Broker Warrant",
        attributes={"bid": "9", "ask": "11", "previous_close": "8"},
        last_updated=datetime(2026, 11, 5, tzinfo=UTC),
    )
    hass = SimpleNamespace(states=_States(state))
    coordinator = _coordinator(hass)

    quote = coordinator._external_quote(
        {
            "symbol": "test",
            "name": "",
            "price_entity": "sensor.test_price",
            "price_mode": "midpoint",
            "price_currency": "chf",
        }
    )

    assert quote is not None
    assert quote.symbol == "TEST"
    assert quote.name == "Broker Warrant"
    assert quote.price == Decimal("10")
    assert quote.previous_close == Decimal("8")
    assert quote.currency == "CHF"


def test_mobile_alert_retries_after_temporary_failure(monkeypatch) -> None:
    services = _Services()
    hass = SimpleNamespace(
        config=SimpleNamespace(language="de-CH"),
        services=services,
    )
    coordinator = _coordinator(
        hass,
        {
            "notify_targets": ["notify.mobile_app_phone"],
            "persistent_notifications": True,
        },
    )
    persistent: list[tuple] = []
    monkeypatch.setattr(
        coordinator_module,
        "async_create",
        lambda hass, message, **kwargs: persistent.append((message, kwargs)),
    )
    holding = {
        "holding_id": "holding-1",
        "symbol": "TEST",
        "name": "Test Asset",
        "asset_type": "stock",
        "quantity": 1,
        "average_price": 100,
        "alert_below": 90,
        "alert_above": 110,
    }

    async def run_scenario() -> None:
        services.fail = True
        await coordinator._async_notify_price_alerts(_data("111"), [holding])
        assert len(persistent) == 1
        assert len(services.calls) == 1
        assert coordinator._mobile_alerts == set()

        services.fail = False
        await coordinator._async_notify_price_alerts(_data("112"), [holding])
        assert len(persistent) == 1
        assert len(services.calls) == 2
        assert coordinator._mobile_alerts == {
            ("holding-1_above", "notify.mobile_app_phone")
        }

        await coordinator._async_notify_price_alerts(_data("113"), [holding])
        assert len(persistent) == 1
        assert len(services.calls) == 2

        await coordinator._async_notify_price_alerts(_data("100"), [holding])
        assert coordinator._active_alerts == set()
        assert coordinator._mobile_alerts == set()

        await coordinator._async_notify_price_alerts(_data("89"), [holding])
        assert len(persistent) == 2
        assert len(services.calls) == 3
        assert services.calls[-1][0:2] == ("notify", "send_message")
        assert services.calls[-1][3]["target"] == {
            "entity_id": ["notify.mobile_app_phone"]
        }
        assert "unter dem Grenzwert" in services.calls[-1][2]["message"]

    asyncio.run(run_scenario())


def test_mobile_alert_retries_only_failed_target(monkeypatch) -> None:
    services = _Services()
    services.fail_targets = {"notify.mobile_app_tablet"}
    hass = SimpleNamespace(
        config=SimpleNamespace(language="en"),
        services=services,
    )
    coordinator = _coordinator(
        hass,
        {
            "notify_targets": [
                "notify.mobile_app_phone",
                "notify.mobile_app_tablet",
            ],
            "persistent_notifications": False,
        },
    )
    monkeypatch.setattr(coordinator_module, "async_create", lambda *args, **kwargs: None)
    holding = {
        "holding_id": "holding-1",
        "symbol": "TEST",
        "name": "Test Asset",
        "asset_type": "stock",
        "quantity": 1,
        "average_price": 100,
        "alert_below": 0,
        "alert_above": 110,
    }

    async def run_scenario() -> None:
        await coordinator._async_notify_price_alerts(_data("111"), [holding])
        assert len(services.calls) == 2
        assert coordinator._mobile_alerts == {
            ("holding-1_above", "notify.mobile_app_phone")
        }

        services.fail_targets.clear()
        await coordinator._async_notify_price_alerts(_data("112"), [holding])
        assert len(services.calls) == 3
        assert services.calls[-1][3]["target"] == {
            "entity_id": ["notify.mobile_app_tablet"]
        }
        assert coordinator._mobile_alerts == {
            ("holding-1_above", "notify.mobile_app_phone"),
            ("holding-1_above", "notify.mobile_app_tablet"),
        }

        await coordinator._async_notify_price_alerts(_data("113"), [holding])
        assert len(services.calls) == 3

    asyncio.run(run_scenario())
