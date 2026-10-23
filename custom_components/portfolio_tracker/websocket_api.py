"""Authenticated portfolio editing commands for the integrated Lovelace manager."""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import uuid4

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN, CONF_HOLDINGS, CONF_HOLDING_ID, CONF_SYMBOL, CONF_NAME,
    CONF_ASSET_TYPE, CONF_WATCH_ONLY, CONF_TRANSACTIONS, CONF_QUANTITY,
    CONF_AVERAGE_PRICE, CONF_DISPLAY_CURRENCY, CONF_ALERT_ABOVE,
    CONF_ALERT_BELOW, CONF_TRANSACTION_ID, CONF_TRANSACTION_TYPE,
    CONF_TRANSACTION_DATE, CONF_TRANSACTION_PRICE, CONF_TRANSACTION_PRICE_MODE,
    CONF_TRANSACTION_CURRENCY, CONF_TRANSACTION_FEES, CONF_TRANSACTION_TAXES,
    CONF_TRANSACTION_EXCHANGE, CONF_TRANSACTION_NOTE,
    CONF_TRANSACTION_MARKET_PRICE, CONF_TRANSACTION_MARKET_CURRENCY,
    CONF_PRICE_SOURCE,
    ASSET_TYPES, DEFAULT_BASE_CURRENCY, entry_value,
)
from .transactions import transaction_balances_are_valid


def _number(value, *, positive=False):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Ungültiger Zahlenwert") from exc
    if not result.is_finite() or (positive and result <= 0) or (not positive and result < 0):
        raise ValueError("Ungültiger oder negativer Zahlenwert")
    return float(result)


def _holding(holdings, asset_id):
    return next((h for h in holdings if h.get(CONF_HOLDING_ID) == asset_id), None)


def _mutate(holdings, action, message, base_currency):
    payload = message.get("payload", {})
    asset_id = str(payload.get("asset_id", ""))
    target = _holding(holdings, asset_id)
    if action == "add_asset":
        symbol = str(payload.get("symbol", "")).strip().upper()
        if not symbol or len(symbol) > 80:
            raise ValueError("Ticker fehlt oder ist zu lang")
        asset_type = str(payload.get("asset_type", "stock"))
        if asset_type not in ASSET_TYPES or asset_type == "warrant":
            raise ValueError("Warrants vorerst über die erweiterte Konfiguration erfassen")
        if any(str(h.get(CONF_SYMBOL, "")).upper() == symbol for h in holdings):
            raise ValueError("Asset bereits vorhanden")
        currency = str(payload.get("currency") or base_currency).upper()
        if len(currency) != 3 or not currency.isalpha():
            raise ValueError("Ungültige Währung")
        watch = payload.get("watch_only", True)
        if not isinstance(watch, bool):
            raise ValueError("Ungültiger Watchlist-Wert")
        h = {
            CONF_HOLDING_ID: uuid4().hex,
            CONF_SYMBOL: symbol,
            CONF_NAME: str(payload.get("name") or symbol)[:128],
            CONF_ASSET_TYPE: asset_type,
            CONF_WATCH_ONLY: watch,
            CONF_DISPLAY_CURRENCY: currency,
            CONF_PRICE_SOURCE: "yahoo",
            CONF_QUANTITY: 0.0,
            CONF_AVERAGE_PRICE: 0.0,
            CONF_TRANSACTIONS: [],
        }
        holdings.append(h)
        return h[CONF_HOLDING_ID]
    if target is None:
        raise ValueError("Asset nicht gefunden")
    if action == "update_asset":
        for field in (CONF_NAME,):
            if field in payload:
                target[field] = str(payload[field]).strip()[:128]
        if "watch_only" in payload:
            desired = payload["watch_only"]
            if not isinstance(desired, bool):
                raise ValueError("Ungültiger Watchlist-Wert")
            if desired and (target.get(CONF_TRANSACTIONS) or float(target.get(CONF_QUANTITY, 0) or 0) > 0):
                raise ValueError("Asset mit Transaktionen kann nicht zur Watchlist werden")
            target[CONF_WATCH_ONLY] = desired
        return asset_id
    if action == "remove_asset":
        if (target.get(CONF_TRANSACTIONS) or float(target.get(CONF_QUANTITY, 0) or 0) > 0) and payload.get("confirm_history") is not True:
            raise ValueError("Transaktionshistorie vorhanden; Löschung muss ausdrücklich bestätigt werden")
        holdings.remove(target)
        return asset_id
    if action == "set_alerts":
        below = payload.get("below")
        above = payload.get("above")
        below = None if below in (None, "") else _number(below, positive=True)
        above = None if above in (None, "") else _number(above, positive=True)
        if below is not None and above is not None and below >= above:
            raise ValueError("Unterer Alarm muss kleiner als oberer Alarm sein")
        for field, value in ((CONF_ALERT_BELOW, below), (CONF_ALERT_ABOVE, above)):
            if value is None:
                target.pop(field, None)
            else:
                target[field] = value
        return asset_id
    if action in ("add_transaction", "update_transaction", "remove_transaction"):
        ledger = target.setdefault(CONF_TRANSACTIONS, [])
        transaction_id = str(payload.get("transaction_id", ""))
        existing = next((t for t in ledger if t.get(CONF_TRANSACTION_ID) == transaction_id), None)
        if action == "add_transaction" and existing is not None:
            raise ValueError("Transaktion wurde bereits erfasst")
        if action != "add_transaction" and existing is None:
            raise ValueError("Transaktion nicht gefunden")
        if action == "remove_transaction":
            ledger.remove(existing)
        else:
            kind = str(payload.get("type", "buy"))
            if kind not in ("buy", "sell", "opening"):
                raise ValueError("Ungültiger Transaktionstyp")
            try:
                trade_date = date.fromisoformat(str(payload.get("date"))).isoformat()
            except (ValueError, TypeError) as exc:
                raise ValueError("Ungültiges Handelsdatum") from exc
            currency = str(payload.get("currency") or base_currency).upper()
            if len(currency) != 3 or not currency.isalpha():
                raise ValueError("Ungültige Transaktionswährung")
            if existing is None and transaction_id:
                if any(t.get(CONF_TRANSACTION_ID) == transaction_id for h in holdings for t in h.get(CONF_TRANSACTIONS, [])):
                    raise ValueError("Transaktion wurde bereits erfasst")
            transaction = {
                CONF_TRANSACTION_ID: transaction_id if transaction_id else uuid4().hex,
                CONF_TRANSACTION_TYPE: kind,
                CONF_TRANSACTION_DATE: trade_date,
                CONF_QUANTITY: _number(payload.get("quantity"), positive=True),
                CONF_TRANSACTION_PRICE: _number(payload.get("price"), positive=True),
                CONF_TRANSACTION_PRICE_MODE: (
                    existing.get(CONF_TRANSACTION_PRICE_MODE, "per_unit") if existing
                    else "per_unit"
                ),
                CONF_TRANSACTION_CURRENCY: currency,
                CONF_TRANSACTION_MARKET_PRICE: 0.0,
                CONF_TRANSACTION_MARKET_CURRENCY: "",
                CONF_TRANSACTION_FEES: _number(payload.get("fees", 0)),
                CONF_TRANSACTION_TAXES: _number(payload.get("taxes", 0)),
                CONF_TRANSACTION_EXCHANGE: str(payload.get("exchange", ""))[:128],
                CONF_TRANSACTION_NOTE: str(payload.get("note", ""))[:512],
            }
            if existing:
                # Preserve optional market-price, broker and future transaction metadata.
                transaction = {**existing, **transaction}
                transaction[CONF_TRANSACTION_MARKET_PRICE] = existing.get(CONF_TRANSACTION_MARKET_PRICE, 0.0)
                transaction[CONF_TRANSACTION_MARKET_CURRENCY] = existing.get(CONF_TRANSACTION_MARKET_CURRENCY, "")
                if "exchange" not in payload:
                    transaction[CONF_TRANSACTION_EXCHANGE] = existing.get(CONF_TRANSACTION_EXCHANGE, "")
                if "note" not in payload:
                    transaction[CONF_TRANSACTION_NOTE] = existing.get(CONF_TRANSACTION_NOTE, "")
                ledger[ledger.index(existing)] = transaction
            else:
                ledger.append(transaction)
        if not transaction_balances_are_valid(target):
            raise ValueError("Buchung erzeugt einen negativen historischen Bestand")
        if target.get(CONF_WATCH_ONLY) and ledger:
            target[CONF_WATCH_ONLY] = False
        return asset_id
    raise ValueError("Unbekannte Aktion")


def register(hass: HomeAssistant) -> None:
    """Register once; commands locate the active config entry on each request."""
    if hass.data.get('portfolio_tracker_websocket_registered'):
        return
    hass.data['portfolio_tracker_websocket_registered'] = True

    @websocket_api.websocket_command({
        vol.Required("type"): "portfolio_tracker/manage",
        vol.Required("entry_id"): str,
        vol.Required("action"): vol.In([
            "get_assets", "add_asset", "update_asset", "remove_asset",
            "set_alerts", "add_transaction", "update_transaction", "remove_transaction",
        ]),
        vol.Optional("payload", default={}): dict,
    })
    @websocket_api.async_response
    async def manage(hass, connection, msg):
        if not connection.user.is_admin:
            connection.send_error(msg["id"], "unauthorized", "Administratorrechte erforderlich")
            return
        entry = hass.config_entries.async_get_entry(msg["entry_id"])
        if entry is None or entry.domain != DOMAIN:
            connection.send_error(msg["id"], "not_found", "Portfolio nicht gefunden")
            return
        holdings = deepcopy(entry_value(entry, CONF_HOLDINGS, []))
        if msg["action"] == "get_assets":
            connection.send_result(msg["id"], {"assets": holdings})
            return
        try:
            changed = _mutate(
                holdings, msg["action"], msg, entry_value(entry, "base_currency", DEFAULT_BASE_CURRENCY)
            )
        except (ValueError, TypeError, KeyError) as exc:
            connection.send_error(msg["id"], "invalid_request", str(exc))
            return
        options = dict(entry.options)
        options[CONF_HOLDINGS] = holdings
        hass.config_entries.async_update_entry(entry, options=options)
        connection.send_result(msg["id"], {"asset_id": changed, "ok": True})

    websocket_api.async_register_command(hass, manage)
