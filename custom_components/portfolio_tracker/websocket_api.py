"""Authenticated editing commands for the integrated portfolio manager."""

from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from typing import Any
from uuid import uuid4

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    ASSET_TYPES,
    CONF_ALERT_ABOVE,
    CONF_ALERT_BELOW,
    CONF_ASSET_TYPE,
    CONF_AVERAGE_PRICE,
    CONF_BASE_CURRENCY,
    CONF_COINGECKO_ID,
    CONF_DISPLAY_CURRENCY,
    CONF_EXPIRY,
    CONF_HOLDING_ID,
    CONF_HOLDINGS,
    CONF_ISIN,
    CONF_ISSUER,
    CONF_NAME,
    CONF_PRICE_CURRENCY,
    CONF_PRICE_ENTITY,
    CONF_PRICE_MODE,
    CONF_PRICE_SOURCE,
    CONF_QUANTITY,
    CONF_RATIO,
    CONF_STRIKE,
    CONF_SYMBOL,
    CONF_TRADING_VENUE,
    CONF_TRANSACTION_CURRENCY,
    CONF_TRANSACTION_DATE,
    CONF_TRANSACTION_EXCHANGE,
    CONF_TRANSACTION_FEES,
    CONF_TRANSACTION_ID,
    CONF_TRANSACTION_MARKET_CURRENCY,
    CONF_TRANSACTION_MARKET_PRICE,
    CONF_TRANSACTION_NOTE,
    CONF_TRANSACTION_PRICE,
    CONF_TRANSACTION_PRICE_MODE,
    CONF_TRANSACTION_TAXES,
    CONF_TRANSACTION_TYPE,
    CONF_TRANSACTIONS,
    CONF_UNDERLYING,
    CONF_VALOR,
    CONF_WARRANT_TYPE,
    CONF_WATCH_ONLY,
    CONF_WKN,
    DEFAULT_BASE_CURRENCY,
    DOMAIN,
    PRICE_MODES,
    PRICE_SOURCES,
    TRANSACTION_PRICE_MODES,
    TRANSACTION_TYPES,
    WARRANT_TYPES,
    WARRANT_VENUES,
    entry_value,
)
from .transactions import transaction_balances_are_valid

COMMAND = f"{DOMAIN}/manage"
DATA_REGISTERED = f"{DOMAIN}_websocket_registered"
DATA_LOCKS = f"{DOMAIN}_manager_locks"

_ASSET_TEXT_FIELDS = {
    CONF_NAME: 128,
    CONF_ISIN: 32,
    CONF_WKN: 32,
    CONF_ISSUER: 128,
    CONF_UNDERLYING: 128,
}
_WARRANT_FIELDS = {
    CONF_PRICE_SOURCE,
    CONF_PRICE_ENTITY,
    CONF_PRICE_CURRENCY,
    CONF_PRICE_MODE,
    CONF_ISIN,
    CONF_WKN,
    CONF_VALOR,
    CONF_ISSUER,
    CONF_UNDERLYING,
    CONF_WARRANT_TYPE,
    CONF_STRIKE,
    CONF_RATIO,
    CONF_EXPIRY,
    CONF_TRADING_VENUE,
}


class PortfolioManagerError(ValueError):
    """Validation error with a stable frontend translation key."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _error(code: str, message: str) -> PortfolioManagerError:
    return PortfolioManagerError(code, message)


def _number(
    value: Any,
    *,
    positive: bool = False,
    default: float | None = None,
) -> float:
    if value in (None, "") and default is not None:
        value = default
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as err:
        raise _error("invalid_number", "Invalid number") from err
    if not result.is_finite() or result < 0 or (positive and result <= 0):
        raise _error("invalid_number", "Number is outside the allowed range")
    return float(result)


def _optional_positive(value: Any) -> float | None:
    return None if value in (None, "") else _number(value, positive=True)


def _currency(value: Any, *, default: str | None = None) -> str:
    normalized = str(value or default or "").strip().upper()
    if len(normalized) != 3 or not normalized.isascii() or not normalized.isalpha():
        raise _error("invalid_currency", "Invalid currency")
    return normalized


def _required_text(value: Any, code: str, *, maximum: int = 128) -> str:
    normalized = str(value or "").strip()
    if not normalized or len(normalized) > maximum:
        raise _error(code, "Required text is missing or too long")
    return normalized


def _boolean(value: Any, code: str) -> bool:
    if not isinstance(value, bool):
        raise _error(code, "Expected a boolean value")
    return value


def _revision(holdings: list[dict[str, Any]]) -> str:
    """Return a stable revision used to prevent lost dashboard updates."""
    encoded = json.dumps(
        holdings,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode()
    return sha256(encoded).hexdigest()


def _holding(
    holdings: list[dict[str, Any]], asset_id: str
) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in holdings
            if str(item.get(CONF_HOLDING_ID, "")) == asset_id
        ),
        None,
    )


def _validate_alerts(payload: dict[str, Any]) -> tuple[float | None, float | None]:
    below = _optional_positive(payload.get("below", payload.get(CONF_ALERT_BELOW)))
    above = _optional_positive(payload.get("above", payload.get(CONF_ALERT_ABOVE)))
    if below is not None and above is not None and below >= above:
        raise _error("invalid_alert_range", "Lower alert must be below upper alert")
    return below, above


def _apply_alerts(target: dict[str, Any], payload: dict[str, Any]) -> None:
    below, above = _validate_alerts(payload)
    for field, value in ((CONF_ALERT_BELOW, below), (CONF_ALERT_ABOVE, above)):
        if value is None:
            target.pop(field, None)
        else:
            target[field] = value


def _build_asset(
    payload: dict[str, Any],
    base_currency: str,
    holdings: list[dict[str, Any]],
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a validated asset while preserving transaction history."""
    source = deepcopy(existing) if existing is not None else {}
    combined = {**source, **payload}
    asset_type = str(combined.get(CONF_ASSET_TYPE, "stock")).strip().lower()
    if asset_type not in ASSET_TYPES:
        raise _error("invalid_asset_type", "Invalid asset type")

    price_source = str(combined.get(CONF_PRICE_SOURCE, "yahoo")).strip().lower()
    valor = (
        str(combined.get(CONF_VALOR, ""))
        .replace("'", "")
        .replace("\u2019", "")
        .replace(" ", "")
    )
    symbol = str(combined.get(CONF_SYMBOL, "")).strip().upper()
    if asset_type == "warrant" and price_source == "swissquote" and not symbol:
        symbol = valor
    if not symbol or len(symbol) > 80:
        raise _error("symbol_required", "Ticker or symbol is required")
    if any(
        item is not existing
        and str(item.get(CONF_SYMBOL, "")).strip().upper() == symbol
        for item in holdings
    ):
        raise _error("duplicate_symbol", "The asset already exists")

    watch_only = combined.get(CONF_WATCH_ONLY, True)
    watch_only = _boolean(watch_only, "invalid_watch_only")
    transactions = deepcopy(source.get(CONF_TRANSACTIONS, []))
    if watch_only and (
        transactions or _number(source.get(CONF_QUANTITY, 0), default=0) > 0
    ):
        raise _error(
            "transactions_prevent_watchlist",
            "An asset with transactions cannot be moved to the watchlist",
        )

    target = deepcopy(source)
    target[CONF_HOLDING_ID] = str(
        source.get(CONF_HOLDING_ID) or uuid4().hex
    )
    target[CONF_SYMBOL] = symbol
    target[CONF_NAME] = str(combined.get(CONF_NAME) or symbol).strip()[:128]
    target[CONF_ASSET_TYPE] = asset_type
    target[CONF_WATCH_ONLY] = watch_only
    target[CONF_TRANSACTIONS] = transactions
    target.setdefault(CONF_QUANTITY, 0.0)
    target.setdefault(CONF_AVERAGE_PRICE, 0.0)

    if asset_type == "crypto":
        target[CONF_DISPLAY_CURRENCY] = _currency(
            combined.get(CONF_DISPLAY_CURRENCY), default=base_currency
        )
        target[CONF_COINGECKO_ID] = str(
            combined.get(CONF_COINGECKO_ID, "")
        ).strip().lower()[:128]
    else:
        target[CONF_DISPLAY_CURRENCY] = _currency(
            combined.get(CONF_DISPLAY_CURRENCY), default=base_currency
        )
        target[CONF_COINGECKO_ID] = ""

    if asset_type != "warrant":
        target[CONF_PRICE_SOURCE] = "yahoo"
        target[CONF_PRICE_MODE] = "state"
        for field in _WARRANT_FIELDS - {CONF_PRICE_SOURCE, CONF_PRICE_MODE}:
            target.pop(field, None)
    else:
        if price_source not in PRICE_SOURCES:
            raise _error("invalid_price_source", "Invalid price source")
        price_mode = str(combined.get(CONF_PRICE_MODE, "state")).strip().lower()
        if price_mode not in PRICE_MODES:
            raise _error("invalid_price_mode", "Invalid price mode")
        venue = str(combined.get(CONF_TRADING_VENUE, "other")).strip().lower()
        if venue not in WARRANT_VENUES:
            raise _error("invalid_trading_venue", "Invalid trading venue")
        if price_source == "swissquote":
            if venue not in {"six", "swiss_dots"}:
                raise _error(
                    "invalid_trading_venue",
                    "Swissquote warrants require SIX or Swiss DOTS",
                )
            if not valor or not valor.isdigit() or len(valor) > 9:
                raise _error("invalid_valor", "A valid Swiss valor is required")
        price_entity = str(combined.get(CONF_PRICE_ENTITY, "")).strip()
        if price_source == "entity" and not price_entity.startswith("sensor."):
            raise _error("price_entity_required", "A sensor entity is required")
        price_currency = _currency(
            combined.get(CONF_PRICE_CURRENCY), default="CHF"
        )
        warrant_type = str(
            combined.get(CONF_WARRANT_TYPE, "call")
        ).strip().lower()
        if warrant_type not in WARRANT_TYPES:
            raise _error("invalid_warrant_type", "Invalid warrant type")
        try:
            expiry = date.fromisoformat(
                _required_text(
                    combined.get(CONF_EXPIRY),
                    "invalid_expiry",
                    maximum=10,
                )
            ).isoformat()
        except ValueError as err:
            raise _error("invalid_expiry", "Invalid expiry date") from err

        target[CONF_PRICE_SOURCE] = price_source
        target[CONF_PRICE_MODE] = "state" if price_source == "yahoo" else price_mode
        target[CONF_PRICE_ENTITY] = price_entity
        target[CONF_PRICE_CURRENCY] = price_currency
        target[CONF_TRADING_VENUE] = venue
        target[CONF_VALOR] = valor
        target[CONF_WARRANT_TYPE] = warrant_type
        target[CONF_STRIKE] = _number(
            combined.get(CONF_STRIKE), positive=True
        )
        target[CONF_RATIO] = _number(combined.get(CONF_RATIO), positive=True)
        target[CONF_EXPIRY] = expiry
        for field, maximum in _ASSET_TEXT_FIELDS.items():
            value = str(combined.get(field, "")).strip()[:maximum]
            target[field] = value.upper() if field in {CONF_ISIN, CONF_WKN} else value

    _apply_alerts(target, combined)
    return target


def _transaction_from_payload(
    payload: dict[str, Any],
    base_currency: str,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    combined = {**(existing or {}), **payload}
    transaction_type = str(
        combined.get("type", combined.get(CONF_TRANSACTION_TYPE, "buy"))
    ).strip().lower()
    if transaction_type not in TRANSACTION_TYPES:
        raise _error("invalid_transaction_type", "Invalid transaction type")
    try:
        transaction_date = date.fromisoformat(
            str(
                combined.get("date", combined.get(CONF_TRANSACTION_DATE, ""))
            ).strip()
        ).isoformat()
    except ValueError as err:
        raise _error("invalid_transaction_date", "Invalid transaction date") from err
    price_mode = str(
        combined.get(
            "price_mode",
            combined.get(CONF_TRANSACTION_PRICE_MODE, "per_unit"),
        )
    ).strip()
    if price_mode not in TRANSACTION_PRICE_MODES:
        raise _error("invalid_price_mode", "Invalid transaction price mode")
    currency = _currency(
        combined.get("currency", combined.get(CONF_TRANSACTION_CURRENCY)),
        default=base_currency,
    )
    market_price = _number(
        combined.get(
            "market_price",
            combined.get(CONF_TRANSACTION_MARKET_PRICE, 0),
        ),
        default=0,
    )
    market_currency_raw = combined.get(
        "market_currency",
        combined.get(CONF_TRANSACTION_MARKET_CURRENCY, ""),
    )
    market_currency = (
        _currency(market_currency_raw) if market_currency_raw else ""
    )
    if market_price > 0 and not market_currency:
        raise _error("invalid_currency", "Market-price currency is required")

    transaction = deepcopy(existing) if existing is not None else {}
    transaction.update(
        {
            CONF_TRANSACTION_ID: str(
                (existing or {}).get(CONF_TRANSACTION_ID)
                or combined.get("transaction_id")
                or uuid4().hex
            ),
            CONF_TRANSACTION_TYPE: transaction_type,
            CONF_TRANSACTION_DATE: transaction_date,
            CONF_QUANTITY: _number(
                combined.get("quantity", combined.get(CONF_QUANTITY)),
                positive=True,
            ),
            CONF_TRANSACTION_PRICE: _number(
                combined.get("price", combined.get(CONF_TRANSACTION_PRICE)),
                positive=True,
            ),
            CONF_TRANSACTION_PRICE_MODE: price_mode,
            CONF_TRANSACTION_MARKET_PRICE: market_price,
            CONF_TRANSACTION_MARKET_CURRENCY: market_currency,
            CONF_TRANSACTION_CURRENCY: currency,
            CONF_TRANSACTION_FEES: _number(
                combined.get("fees", combined.get(CONF_TRANSACTION_FEES, 0)),
                default=0,
            ),
            CONF_TRANSACTION_TAXES: _number(
                combined.get("taxes", combined.get(CONF_TRANSACTION_TAXES, 0)),
                default=0,
            ),
            CONF_TRANSACTION_EXCHANGE: str(
                combined.get("exchange", combined.get(CONF_TRANSACTION_EXCHANGE, ""))
            ).strip()[:128],
            CONF_TRANSACTION_NOTE: str(
                combined.get("note", combined.get(CONF_TRANSACTION_NOTE, ""))
            ).strip()[:512],
        }
    )
    return transaction


def _mutate_working(
    holdings: list[dict[str, Any]],
    action: str,
    payload: dict[str, Any],
    base_currency: str,
) -> str:
    asset_id = str(payload.get("asset_id", ""))
    target = _holding(holdings, asset_id)
    if action == "add_asset":
        created = _build_asset(payload, base_currency, holdings)
        holdings.append(created)
        return created[CONF_HOLDING_ID]
    if target is None:
        raise _error("asset_not_found", "Asset not found")
    if action == "update_asset":
        replacement = _build_asset(
            payload,
            base_currency,
            holdings,
            existing=target,
        )
        holdings[holdings.index(target)] = replacement
        return asset_id
    if action == "remove_asset":
        has_history = bool(target.get(CONF_TRANSACTIONS)) or _number(
            target.get(CONF_QUANTITY, 0), default=0
        ) > 0
        if has_history and payload.get("confirm_history") is not True:
            raise _error(
                "history_confirmation_required",
                "Deleting an asset with transaction history requires confirmation",
            )
        holdings.remove(target)
        return asset_id
    if action == "set_alerts":
        _apply_alerts(target, payload)
        return asset_id
    if action not in {
        "add_transaction",
        "update_transaction",
        "remove_transaction",
    }:
        raise _error("unknown_action", "Unknown manager action")

    ledger = target.setdefault(CONF_TRANSACTIONS, [])
    transaction_id = str(payload.get("transaction_id", ""))
    existing = next(
        (
            item
            for item in ledger
            if str(item.get(CONF_TRANSACTION_ID, "")) == transaction_id
        ),
        None,
    )
    if action != "add_transaction" and existing is None:
        raise _error("transaction_not_found", "Transaction not found")
    if action == "remove_transaction":
        ledger.remove(existing)
    else:
        if action == "add_transaction" and transaction_id and any(
            str(item.get(CONF_TRANSACTION_ID, "")) == transaction_id
            for holding in holdings
            for item in holding.get(CONF_TRANSACTIONS, [])
        ):
            raise _error("duplicate_transaction", "Transaction already exists")
        transaction = _transaction_from_payload(
            payload,
            base_currency,
            existing=existing,
        )
        if existing is None:
            ledger.append(transaction)
        else:
            ledger[ledger.index(existing)] = transaction
    if not transaction_balances_are_valid(target):
        raise _error(
            "negative_balance",
            "The transaction creates a negative historical position",
        )
    if ledger:
        target[CONF_WATCH_ONLY] = False
    return asset_id


def _mutate(
    holdings: list[dict[str, Any]],
    action: str,
    message: dict[str, Any],
    base_currency: str,
) -> str:
    """Apply one action atomically and leave input untouched after an error."""
    working = deepcopy(holdings)
    changed = _mutate_working(
        working,
        action,
        dict(message.get("payload") or {}),
        base_currency,
    )
    holdings[:] = working
    return changed


async def async_handle_manage(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle one authenticated manager request."""
    if connection.user is None or not connection.user.is_admin:
        connection.send_error(msg["id"], "unauthorized", "Administrator required")
        return
    entry = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN:
        connection.send_error(msg["id"], "not_found", "Portfolio not found")
        return

    locks: dict[str, asyncio.Lock] = hass.data.setdefault(DATA_LOCKS, {})
    lock = locks.setdefault(entry.entry_id, asyncio.Lock())
    async with lock:
        holdings = deepcopy(entry_value(entry, CONF_HOLDINGS, []))
        current_revision = _revision(holdings)
        if msg["action"] == "get_assets":
            connection.send_result(
                msg["id"],
                {
                    "assets": holdings,
                    "revision": current_revision,
                    "base_currency": entry_value(
                        entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                    ),
                },
            )
            return
        requested_revision = str(msg.get("revision", ""))
        if requested_revision and requested_revision != current_revision:
            connection.send_error(
                msg["id"],
                "conflict",
                "Portfolio changed; reload the manager and try again",
            )
            return
        try:
            changed = _mutate(
                holdings,
                msg["action"],
                msg,
                entry_value(entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY),
            )
        except PortfolioManagerError as err:
            connection.send_error(msg["id"], err.code, str(err))
            return
        except (KeyError, TypeError, ValueError):
            connection.send_error(msg["id"], "invalid_request", "Invalid request")
            return
        options = dict(entry.options)
        options[CONF_HOLDINGS] = holdings
        hass.config_entries.async_update_entry(entry, options=options)
        connection.send_result(
            msg["id"],
            {
                "asset_id": changed,
                "ok": True,
                "revision": _revision(holdings),
            },
        )


def register(hass: HomeAssistant) -> None:
    """Register the manager command once for the integration."""
    if hass.data.get(DATA_REGISTERED):
        return
    hass.data[DATA_REGISTERED] = True

    @websocket_api.websocket_command(
        {
            vol.Required("type"): COMMAND,
            vol.Required("entry_id"): str,
            vol.Required("action"): vol.In(
                {
                    "get_assets",
                    "add_asset",
                    "update_asset",
                    "remove_asset",
                    "set_alerts",
                    "add_transaction",
                    "update_transaction",
                    "remove_transaction",
                }
            ),
            vol.Optional("payload", default={}): dict,
            vol.Optional("revision", default=""): str,
        }
    )
    @websocket_api.async_response
    async def manage(
        hass: HomeAssistant,
        connection: websocket_api.ActiveConnection,
        msg: dict[str, Any],
    ) -> None:
        await async_handle_manage(hass, connection, msg)

    websocket_api.async_register_command(hass, manage)


def entry_holdings(entry: ConfigEntry) -> list[dict[str, Any]]:
    """Return manager holdings for tests and diagnostics."""
    return deepcopy(entry_value(entry, CONF_HOLDINGS, []))
