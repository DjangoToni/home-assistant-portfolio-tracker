"""Swissquote client for Swiss warrants listed on SIX and Swiss DOTS."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import quote as url_quote

from aiohttp import ClientError, ClientSession

from .models import Quote, StockHistoryPoint

SEARCH_URL = (
    "https://www.swissquote.ch/sqi_web_search/search/quicksearch/init/0/20"
)
FULL_QUOTE_URL = (
    "https://www.swissquote.ch/securities-retail-fullquote-plugin/api/"
    "fullQuote/{isin}/{exchange_id}_{currency}"
)
HISTORY_URL = (
    "https://www.swissquote.ch/securities-retail-chart-plugin/api/"
    "chart/trading-view/histo"
)
HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Home-Assistant-Portfolio-Tracker/1.6.1",
}
VENUE_EXCHANGE_IDS = {"six": 4, "swiss_dots": 672}


class SwissquoteError(Exception):
    """Base Swissquote client error."""


class SwissquoteWarrantNotFound(SwissquoteError):
    """Raised when Swissquote does not know the requested warrant."""


class SwissquoteClient:
    """Resolve a Swiss valor number and normalize its public full quote."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session
        self._instruments: dict[tuple[str, str], dict] = {}

    async def async_get_quote(
        self,
        valor: str,
        *,
        price_mode: str = "state",
        trading_venue: str | None = None,
        symbol: str | None = None,
    ) -> Quote:
        """Fetch one warrant by exact Swiss valor number."""
        normalized_valor, item = await self._async_resolve_instrument(
            valor, trading_venue
        )

        isin = str(item.get("isin") or "").strip().upper()
        currency = str(item.get("currency") or "CHF").strip().upper()
        exchange_id = _integer(item.get("exchangeId"))
        if not isin or exchange_id is None:
            raise SwissquoteError(
                f"Swissquote returned incomplete identifiers for {normalized_valor}"
            )

        payload = await self._async_get_json(
            FULL_QUOTE_URL.format(
                isin=url_quote(isin, safe=""),
                exchange_id=exchange_id,
                currency=url_quote(currency, safe=""),
            ),
            params={"serviceName": "QUOTE"},
        )
        return parse_swissquote_quote(
            payload,
            symbol=(symbol or normalized_valor).strip().upper(),
            price_mode=price_mode,
        )

    async def async_get_history(
        self,
        valor: str,
        *,
        trading_venue: str | None = None,
    ) -> tuple[StockHistoryPoint, ...]:
        """Fetch the most recent 30 calendar days of daily warrant history."""
        _, item = await self._async_resolve_instrument(valor, trading_venue)
        isin = str(item.get("isin") or "").strip().upper()
        currency = str(item.get("currency") or "CHF").strip().upper()
        exchange_id = _integer(item.get("exchangeId"))
        if not isin or exchange_id is None:
            raise SwissquoteError("Swissquote returned incomplete history identifiers")

        end = date.today()
        payload = await self._async_post_json(
            HISTORY_URL,
            params={
                "from": (end - timedelta(days=30)).isoformat(),
                "to": end.isoformat(),
                "countBack": "-1",
            },
            body={
                "isin": isin,
                "exchangeId": exchange_id,
                "currency": currency,
            },
        )
        return parse_swissquote_history(payload)

    async def _async_resolve_instrument(
        self, valor: str, trading_venue: str | None
    ) -> tuple[str, dict]:
        """Resolve and cache the Swissquote stock key for one valor number."""
        normalized_valor = _normalize_valor(valor)
        cache_key = (normalized_valor, trading_venue or "")
        item = self._instruments.get(cache_key)
        if item is not None:
            return normalized_valor, item

        expected_exchange_id = VENUE_EXCHANGE_IDS.get(trading_venue or "")
        search_terms = (
            [_swiss_isin_for_valor(normalized_valor)]
            if trading_venue == "six"
            else [normalized_valor]
        )
        if trading_venue not in VENUE_EXCHANGE_IDS:
            search_terms.append(_swiss_isin_for_valor(normalized_valor))
        for search_term in search_terms:
            search_payload = await self._async_get_json(
                SEARCH_URL,
                params={"searchText": search_term},
            )
            item = _find_warrant(
                search_payload,
                normalized_valor,
                expected_exchange_id,
            )
            if item is not None:
                self._instruments[cache_key] = item
                return normalized_valor, item
        raise SwissquoteWarrantNotFound(normalized_valor)

    async def _async_get_json(self, url: str, *, params: dict[str, str]) -> dict:
        return await self._async_request_json("GET", url, params=params)

    async def _async_post_json(
        self, url: str, *, params: dict[str, str], body: dict
    ) -> dict:
        return await self._async_request_json("POST", url, params=params, body=body)

    async def _async_request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str],
        body: dict | None = None,
    ) -> dict:
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                json=body,
                headers=HEADERS,
                timeout=20,
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise SwissquoteError(f"Could not load Swissquote data: {err}") from err
        if not isinstance(payload, dict):
            raise SwissquoteError("Unexpected Swissquote response")
        return payload


def parse_swissquote_quote(
    payload: dict,
    *,
    symbol: str,
    price_mode: str = "state",
) -> Quote:
    """Normalize one Swissquote full-quote response."""
    data = payload.get("fullQuoteData")
    if not isinstance(data, dict):
        raise SwissquoteError("Swissquote returned no full quote")
    raw_quote = data.get("quote")
    stock_key = data.get("stockKey")
    if not isinstance(raw_quote, dict) or not isinstance(stock_key, dict):
        raise SwissquoteError("Swissquote returned an incomplete full quote")

    bid = _price_amount(raw_quote.get("bidPrice"), positive=True)
    ask = _price_amount(raw_quote.get("askPrice"), positive=True)
    last = _price_amount(raw_quote.get("lastPrice"))
    midpoint = (
        (bid + ask) / Decimal(2)
        if bid is not None and ask is not None
        else _price_amount(raw_quote.get("midPrice"), positive=True)
    )
    selected = {
        "bid": bid,
        "ask": ask,
        "midpoint": midpoint,
    }.get(price_mode)
    if price_mode == "state":
        selected = last
    if selected is None:
        selected = next(
            (value for value in (last, midpoint, bid, ask) if value is not None),
            None,
        )
    if selected is None:
        raise SwissquoteError(f"Swissquote returned no usable price for {symbol}")

    selected_price = {
        "bid": raw_quote.get("bidPrice"),
        "ask": raw_quote.get("askPrice"),
        "state": raw_quote.get("lastPrice"),
    }.get(price_mode)
    timestamp = _price_timestamp(selected_price)
    if timestamp is None:
        timestamp = _price_timestamp(raw_quote.get("lastPrice"))

    return Quote(
        symbol=symbol,
        name=str(data.get("productName") or symbol).strip(),
        price=selected,
        previous_close=_price_amount(raw_quote.get("closePrice")),
        currency=str(stock_key.get("currency") or "CHF").upper(),
        exchange=str(data.get("stockExchangeName") or "Swissquote"),
        instrument_type=str(data.get("productType") or "WARRANT"),
        timestamp=timestamp,
        bid=bid,
        ask=ask,
    )


def parse_swissquote_history(payload: dict) -> tuple[StockHistoryPoint, ...]:
    """Normalize Swissquote daily chart points for the existing detail card."""
    items = payload.get("productInfo")
    if not isinstance(items, list):
        raise SwissquoteError("Swissquote returned no warrant history")
    points: list[StockHistoryPoint] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        timestamp = _timestamp(item.get("time"))
        close = _decimal_value(item.get("close"))
        if timestamp is None or close is None:
            continue
        points.append(
            StockHistoryPoint(
                timestamp=timestamp,
                open=_decimal_value(item.get("open")),
                high=_decimal_value(item.get("high")),
                low=_decimal_value(item.get("low")),
                close=close,
                volume=_integer(item.get("volume")),
            )
        )
    return tuple(sorted(points, key=lambda point: point.timestamp))


def _find_warrant(
    payload: dict,
    valor: str,
    expected_exchange_id: int | None,
) -> dict | None:
    items = payload.get("data")
    if not isinstance(items, list):
        return None
    for item in items:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol", "")).strip()
        isin = str(item.get("isin", "")).strip().upper()
        swiss_isin_matches = (
            isin.startswith("CH")
            and isin[2:11].lstrip("0") == valor.lstrip("0")
        )
        if symbol != valor and not swiss_isin_matches:
            continue
        if str(item.get("type", "")).upper() not in {"EXO", "WAR"}:
            continue
        exchange_id = _integer(item.get("exchangeId"))
        if expected_exchange_id is not None and exchange_id != expected_exchange_id:
            continue
        return item
    return None


def _normalize_valor(value: str) -> str:
    normalized = value.replace("'", "").replace("\u2019", "").replace(" ", "")
    if not normalized.isdigit() or len(normalized) > 9:
        raise SwissquoteWarrantNotFound(value)
    return normalized


def _swiss_isin_for_valor(valor: str) -> str:
    """Return the Swiss ISIN whose national identifier is the valor number."""
    padded_valor = valor.zfill(9)
    numeric_base = f"1217{padded_valor}"
    digits = [int(character) for character in f"{numeric_base}0"]
    checksum_total = 0
    for index, digit in enumerate(reversed(digits)):
        doubled = digit * 2 if index % 2 else digit
        checksum_total += doubled // 10 + doubled % 10
    check_digit = (10 - checksum_total % 10) % 10
    return f"CH{padded_valor}{check_digit}"


def _price_amount(value, *, positive: bool = False) -> Decimal | None:
    if not isinstance(value, dict) or str(value.get("status", "")) == "UNAVAILABLE":
        return None
    raw_amount = value.get("amount")
    if raw_amount is None:
        return None
    try:
        amount = Decimal(str(raw_amount))
    except (InvalidOperation, ValueError):
        return None
    if not amount.is_finite() or amount < 0 or (positive and amount == 0):
        return None
    return amount


def _price_timestamp(value) -> datetime | None:
    if not isinstance(value, dict) or not value.get("timestamp"):
        return None
    return _timestamp(value["timestamp"])


def _timestamp(value) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _decimal_value(value) -> Decimal | None:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return amount if amount.is_finite() and amount >= 0 else None


def _integer(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
