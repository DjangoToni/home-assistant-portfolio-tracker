"""Data update coordinator for Portfolio Tracker."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.persistent_notification import async_create

from .coingecko import CoinGeckoClient
from .const import (
    CONF_ASSET_TYPE,
    CONF_ALERT_ABOVE,
    CONF_ALERT_BELOW,
    CONF_BASE_CURRENCY,
    CONF_HOLDINGS,
    CONF_INDEXES,
    CONF_NAME,
    CONF_PRICE_CURRENCY,
    CONF_PRICE_ENTITY,
    CONF_PRICE_MODE,
    CONF_PRICE_SOURCE,
    CONF_TRADING_VENUE,
    CONF_VALOR,
    CONF_TRANSACTION_CURRENCY,
    CONF_TRANSACTIONS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_BASE_CURRENCY,
    DEFAULT_INDEXES,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    coingecko_id_for_holding,
    crypto_currency_for_holding,
    crypto_data_key,
    entry_value,
)
from .models import PortfolioData, Quote
from .calculator import holding_alert_price
from .yahoo import YahooFinanceClient
from .swissquote import SwissquoteClient

_LOGGER = logging.getLogger(__name__)

ALERT_TEXT = {
    "de": {
        "title": "Kursalarm: {symbol}",
        "below": "unter",
        "above": "über",
        "message": (
            "{name} ({symbol}) liegt mit {price} {currency} {relation} "
            "dem Grenzwert von {threshold} {currency}."
        ),
    },
    "en": {
        "title": "Price alert: {symbol}",
        "below": "below",
        "above": "above",
        "message": (
            "{name} ({symbol}) is at {price} {currency}, {relation} "
            "the threshold of {threshold} {currency}."
        ),
    },
    "fr": {
        "title": "Alerte de cours : {symbol}",
        "below": "sous",
        "above": "au-dessus de",
        "message": (
            "{name} ({symbol}) est à {price} {currency}, {relation} "
            "le seuil de {threshold} {currency}."
        ),
    },
    "it": {
        "title": "Allarme prezzo: {symbol}",
        "below": "sotto",
        "above": "sopra",
        "message": (
            "{name} ({symbol}) è a {price} {currency}, {relation} "
            "la soglia di {threshold} {currency}."
        ),
    },
}


class PortfolioCoordinator(DataUpdateCoordinator[PortfolioData]):
    """Coordinate quotes and exchange rates for one portfolio."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.client = YahooFinanceClient(async_get_clientsession(hass))
        self.swissquote = SwissquoteClient(async_get_clientsession(hass))
        self.coingecko = CoinGeckoClient(async_get_clientsession(hass))
        self._active_alerts: set[str] = set()
        interval = int(
            entry_value(entry, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(minutes=interval),
        )

    async def _async_update_data(self) -> PortfolioData:
        holdings = entry_value(self.entry, CONF_HOLDINGS, [])
        indexes = entry_value(self.entry, CONF_INDEXES, DEFAULT_INDEXES)
        base = entry_value(
            self.entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
        ).upper()
        external_holdings = [
            holding
            for holding in holdings
            if holding.get(CONF_PRICE_SOURCE, "yahoo") == "entity"
        ]
        swissquote_holdings = [
            holding
            for holding in holdings
            if holding.get(CONF_PRICE_SOURCE, "yahoo") == "swissquote"
        ]
        symbols = sorted(
            {
                holding["symbol"].upper()
                for holding in holdings
                if holding.get(CONF_PRICE_SOURCE, "yahoo") == "yahoo"
            }
            | {symbol.upper() for symbol in indexes}
        )
        if not symbols and not external_holdings and not swissquote_holdings:
            return PortfolioData(
                quotes={}, fx_rates={base: Decimal(1)}, base_currency=base
            )

        previous = self.data if isinstance(self.data, PortfolioData) else None
        request_limit = asyncio.Semaphore(4)

        async def fetch_quote(symbol: str) -> Quote:
            async with request_limit:
                for attempt in range(2):
                    try:
                        return await self.client.async_get_quote(symbol)
                    except Exception:
                        if attempt == 0:
                            await asyncio.sleep(1)
                            continue
                        raise
                raise RuntimeError("Unreachable quote retry state")

        async def fetch_swissquote(holding: dict) -> Quote:
            async with request_limit:
                for attempt in range(2):
                    try:
                        return await self.swissquote.async_get_quote(
                            str(holding.get(CONF_VALOR, "")),
                            price_mode=str(holding.get(CONF_PRICE_MODE, "state")),
                            trading_venue=str(
                                holding.get(CONF_TRADING_VENUE, "")
                            ),
                            symbol=str(holding["symbol"]),
                        )
                    except Exception:
                        if attempt == 0:
                            await asyncio.sleep(1)
                            continue
                        raise
                raise RuntimeError("Unreachable Swissquote retry state")

        results = await asyncio.gather(
            *(fetch_quote(symbol) for symbol in symbols),
            return_exceptions=True,
        )
        swissquote_results = await asyncio.gather(
            *(fetch_swissquote(holding) for holding in swissquote_holdings),
            return_exceptions=True,
        )
        quote_symbols = set(symbols) | {
            holding["symbol"].upper()
            for holding in external_holdings + swissquote_holdings
        }
        quotes: dict[str, Quote] = {
            symbol: quote
            for symbol, quote in (previous.quotes.items() if previous else ())
            if symbol in quote_symbols
        }
        updated_quotes = 0
        for symbol, result in zip(symbols, results, strict=True):
            if isinstance(result, BaseException):
                _LOGGER.warning("Could not update %s: %s", symbol, result)
            else:
                quotes[result.symbol] = result
                updated_quotes += 1
        for holding, result in zip(
            swissquote_holdings, swissquote_results, strict=True
        ):
            if isinstance(result, BaseException):
                _LOGGER.warning(
                    "Could not update Swissquote warrant %s (valor %s): %s",
                    holding.get("symbol"),
                    holding.get(CONF_VALOR),
                    result,
                )
            else:
                quotes[result.symbol] = result
                updated_quotes += 1
        for holding in external_holdings:
            external_quote = self._external_quote(holding)
            if external_quote is not None:
                quotes[external_quote.symbol] = external_quote
        if not quotes:
            _LOGGER.warning(
                "No portfolio price source returned a quote; entities remain loaded "
                "and will retry during the next scheduled update"
            )
        elif (symbols or swissquote_holdings) and updated_quotes == 0:
            _LOGGER.warning(
                "No cloud price source returned a fresh quote; retaining the "
                "last successful portfolio data"
            )

        crypto_groups: dict[str, set[str]] = {}
        for holding in holdings:
            if holding.get(CONF_ASSET_TYPE) != "crypto":
                continue
            coin_id = coingecko_id_for_holding(holding)
            if not coin_id:
                continue
            display_currency = crypto_currency_for_holding(holding, base)
            crypto_groups.setdefault(display_currency, set()).add(coin_id)
        transaction_currencies = {
            str(transaction.get(CONF_TRANSACTION_CURRENCY, "")).upper()
            for holding in holdings
            for transaction in holding.get(CONF_TRANSACTIONS, [])
            if transaction.get(CONF_TRANSACTION_CURRENCY)
        }
        currencies = sorted(
            {
                currency
                for currency in (
                    {item.currency for item in quotes.values()}
                    | set(crypto_groups)
                    | transaction_currencies
                )
                if currency != base
            }
        )
        rate_results = await asyncio.gather(
            *(self.client.async_get_fx_rate(currency, base) for currency in currencies),
            return_exceptions=True,
        )
        fx_rates: dict[str, Decimal] = {
            currency: rate
            for currency, rate in (previous.fx_rates.items() if previous else ())
            if currency in currencies or currency == base
        }
        fx_rates[base] = Decimal(1)
        for currency, result in zip(currencies, rate_results, strict=True):
            if isinstance(result, BaseException):
                _LOGGER.warning(
                    "Could not convert %s to %s: %s", currency, base, result
                )
            else:
                fx_rates[currency] = result

        crypto_markets = dict(previous.crypto_markets) if previous else {}
        crypto_history = dict(previous.crypto_history) if previous else {}
        if crypto_groups:
            crypto_currencies = sorted(crypto_groups)
            crypto_results = await asyncio.gather(
                *(
                    asyncio.gather(
                        self.coingecko.async_get_markets(
                            sorted(crypto_groups[currency]), currency
                        ),
                        *(
                            self.coingecko.async_get_history(coin_id, currency)
                            for coin_id in sorted(crypto_groups[currency])
                        ),
                        return_exceptions=True,
                    )
                    for currency in crypto_currencies
                ),
                return_exceptions=True,
            )
            for currency, bundle in zip(
                crypto_currencies, crypto_results, strict=True
            ):
                if isinstance(bundle, BaseException):
                    _LOGGER.warning(
                        "Could not update CoinGecko data in %s: %s",
                        currency,
                        bundle,
                    )
                    continue
                coin_ids = sorted(crypto_groups[currency])
                market_result = bundle[0]
                if isinstance(market_result, BaseException):
                    _LOGGER.warning(
                        "Could not update CoinGecko markets in %s: %s",
                        currency,
                        market_result,
                    )
                else:
                    crypto_markets.update(
                        {
                            crypto_data_key(coin_id, currency): market
                            for coin_id, market in market_result.items()
                        }
                    )
                for coin_id, result in zip(
                    coin_ids, bundle[1:], strict=True
                ):
                    if isinstance(result, BaseException):
                        _LOGGER.warning(
                            "Could not update CoinGecko history for %s in %s: %s",
                            coin_id,
                            currency,
                            result,
                        )
                    else:
                        crypto_history[crypto_data_key(coin_id, currency)] = result

        detail_symbols = sorted(
            {
                holding["symbol"]
                for holding in holdings
                if holding.get(CONF_ASSET_TYPE) == "stock"
                and holding.get(CONF_PRICE_SOURCE, "yahoo") == "yahoo"
            }
            | set(indexes)
        )
        history_symbols = sorted(
            {
                holding["symbol"]
                for holding in holdings
                if holding.get(CONF_ASSET_TYPE) != "crypto"
                and holding.get(CONF_PRICE_SOURCE, "yahoo") == "yahoo"
            }
            | set(indexes)
        )
        stock_markets = {
            symbol: market
            for symbol, market in (previous.stock_markets.items() if previous else ())
            if symbol in detail_symbols
        }
        stock_history = {
            symbol: history
            for symbol, history in (previous.stock_history.items() if previous else ())
            if symbol in history_symbols
        }
        if history_symbols:
            stock_results = await asyncio.gather(
                self.client.async_get_stock_markets(detail_symbols),
                *(
                    self.client.async_get_stock_history(symbol)
                    for symbol in history_symbols
                ),
                return_exceptions=True,
            )
            market_result = stock_results[0]
            if isinstance(market_result, BaseException):
                _LOGGER.warning(
                    "Could not update detailed Yahoo stock data: %s",
                    market_result,
                )
            else:
                stock_markets.update(market_result)
            for symbol, result in zip(
                history_symbols, stock_results[1:], strict=True
            ):
                if isinstance(result, BaseException):
                    _LOGGER.warning(
                        "Could not update Yahoo stock history for %s: %s",
                        symbol,
                        result,
                    )
                else:
                    stock_history[symbol] = result

        data = PortfolioData(
            quotes=quotes,
            fx_rates=fx_rates,
            base_currency=base,
            crypto_markets=crypto_markets,
            crypto_history=crypto_history,
            stock_markets=stock_markets,
            stock_history=stock_history,
        )
        self._notify_price_alerts(data, holdings)
        return data

    def _external_quote(self, holding: dict) -> Quote | None:
        """Normalize a numeric Home Assistant sensor as a market quote."""
        entity_id = str(holding.get(CONF_PRICE_ENTITY, "")).strip()
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None or str(state.state).lower() in {"unknown", "unavailable"}:
            _LOGGER.warning(
                "External price entity %s for %s is unavailable",
                entity_id or "<not configured>",
                holding.get("symbol"),
            )
            return None
        try:
            price = Decimal(str(state.state))
        except (InvalidOperation, ValueError):
            _LOGGER.warning(
                "External price entity %s has non-numeric state %s",
                entity_id,
                state.state,
            )
            return None
        if not price.is_finite() or price < 0:
            _LOGGER.warning(
                "External price entity %s has invalid price %s",
                entity_id,
                state.state,
            )
            return None
        bid = self._decimal_attribute(state.attributes, "bid")
        ask = self._decimal_attribute(state.attributes, "ask")
        previous_close = self._decimal_attribute(
            state.attributes, "previous_close"
        )
        price_mode = str(holding.get(CONF_PRICE_MODE, "state"))
        selected_price = {
            "bid": bid,
            "ask": ask,
            "midpoint": (
                (bid + ask) / Decimal(2)
                if bid is not None and ask is not None
                else None
            ),
        }.get(price_mode)
        if price_mode != "state" and selected_price is None:
            _LOGGER.warning(
                "External price entity %s has no usable %s quote; using its state",
                entity_id,
                price_mode,
            )
        price = selected_price if selected_price is not None else price
        symbol = str(holding["symbol"]).upper()
        return Quote(
            symbol=symbol,
            name=str(holding.get(CONF_NAME) or state.name or symbol),
            price=price,
            previous_close=previous_close,
            currency=str(holding.get(CONF_PRICE_CURRENCY) or "USD").upper(),
            exchange="Home Assistant",
            instrument_type="EXTERNAL",
            timestamp=state.last_updated,
            bid=bid,
            ask=ask,
        )

    @staticmethod
    def _decimal_attribute(attributes: dict, key: str) -> Decimal | None:
        """Return one finite non-negative decimal state attribute."""
        raw_value = attributes.get(key)
        if raw_value is None:
            return None
        try:
            value = Decimal(str(raw_value))
        except (InvalidOperation, ValueError):
            return None
        return value if value.is_finite() and value >= 0 else None

    def _notify_price_alerts(self, data: PortfolioData, holdings: list[dict]) -> None:
        """Notify once when a configured asset threshold becomes active."""
        hass_config = getattr(self.hass, "config", None)
        language = str(getattr(hass_config, "language", "en"))
        language = language.lower().replace("_", "-").split("-", 1)[0]
        text = ALERT_TEXT.get(language, ALERT_TEXT["en"])
        active: set[str] = set()
        for holding in holdings:
            quote = data.quotes.get(holding["symbol"])
            price = holding_alert_price(data, holding)
            if quote is None or price is None:
                continue
            currency = (
                crypto_currency_for_holding(holding, data.base_currency)
                if holding.get(CONF_ASSET_TYPE) == "crypto"
                else quote.currency
            )
            rules = (
                ("below", Decimal(str(holding.get(CONF_ALERT_BELOW, 0)))),
                ("above", Decimal(str(holding.get(CONF_ALERT_ABOVE, 0)))),
            )
            for direction, threshold in rules:
                if threshold <= 0:
                    continue
                triggered = (
                    price <= threshold
                    if direction == "below"
                    else price >= threshold
                )
                alert_id = f"{holding['holding_id']}_{direction}"
                if not triggered:
                    continue
                active.add(alert_id)
                if alert_id in self._active_alerts:
                    continue
                relation = text[direction]
                async_create(
                    self.hass,
                    text["message"].format(
                        name=holding["name"],
                        symbol=holding["symbol"],
                        price=price,
                        currency=currency,
                        relation=relation,
                        threshold=threshold,
                    ),
                    title=text["title"].format(symbol=holding["symbol"]),
                    notification_id=f"{DOMAIN}_{self.entry.entry_id}_{alert_id}",
                )
        self._active_alerts = active
