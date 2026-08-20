"""Small asynchronous Yahoo Finance client.

Yahoo does not publish a supported public market-data API. Keeping the HTTP
client isolated makes it possible to replace this provider without changing
the Home Assistant entity model.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import quote as url_quote

from aiohttp import ClientError, ClientSession

from .models import Quote, StockHistoryPoint, StockMarket

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
CRUMB_URL = "https://query1.finance.yahoo.com/v1/test/getcrumb"
QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/140.0.0.0 Safari/537.36"
    ),
}


class YahooFinanceError(Exception):
    """Base Yahoo client error."""


class YahooSymbolNotFound(YahooFinanceError):
    """Raised when Yahoo does not know a symbol."""


class YahooFinanceClient:
    """Fetch and normalize Yahoo Finance chart responses."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session
        self._crumb: str | None = None
        self._crumb_lock = asyncio.Lock()

    async def async_get_quote(self, symbol: str) -> Quote:
        """Fetch one current quote."""
        normalized = symbol.strip().upper()
        url = CHART_URL.format(symbol=url_quote(normalized, safe=""))
        try:
            async with self._session.get(
                url,
                params={"interval": "1d", "range": "5d"},
                headers=HEADERS,
                timeout=15,
            ) as response:
                if response.status == 404:
                    raise YahooSymbolNotFound(normalized)
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except YahooFinanceError:
            raise
        except (ClientError, TimeoutError, ValueError) as err:
            raise YahooFinanceError(f"Could not load {normalized}: {err}") from err

        chart = payload.get("chart", {})
        error = chart.get("error")
        results = chart.get("result") or []
        if error or not results:
            raise YahooSymbolNotFound(normalized)

        meta = results[0].get("meta", {})
        raw_price = meta.get("regularMarketPrice")
        if raw_price is None:
            quote_indicators = results[0].get("indicators", {}).get("quote") or [{}]
            closes = quote_indicators[0].get("close", [])
            raw_price = next(
                (value for value in reversed(closes) if value is not None), None
            )
        if raw_price is None:
            raise YahooFinanceError(f"No current price for {normalized}")

        try:
            price = Decimal(str(raw_price))
            previous = meta.get("previousClose", meta.get("chartPreviousClose"))
            previous_close = Decimal(str(previous)) if previous is not None else None
        except InvalidOperation as err:
            raise YahooFinanceError(f"Invalid quote for {normalized}") from err

        timestamp = meta.get("regularMarketTime")
        return Quote(
            symbol=normalized,
            name=meta.get("longName") or meta.get("shortName") or normalized,
            price=price,
            previous_close=previous_close,
            currency=(meta.get("currency") or "USD").upper(),
            exchange=meta.get("exchangeName") or meta.get("fullExchangeName"),
            instrument_type=meta.get("instrumentType"),
            timestamp=datetime.fromtimestamp(timestamp, UTC) if timestamp else None,
        )

    async def async_get_fx_rate(self, source: str, target: str) -> Decimal:
        """Return the current conversion rate from source to target."""
        source = source.upper()
        target = target.upper()
        if source == target:
            return Decimal(1)

        try:
            return (await self.async_get_quote(f"{source}{target}=X")).price
        except YahooFinanceError as direct_error:
            try:
                inverse = (await self.async_get_quote(f"{target}{source}=X")).price
                if inverse:
                    return Decimal(1) / inverse
            except YahooFinanceError:
                pass
            raise direct_error

    async def async_get_stock_markets(
        self, symbols: list[str]
    ) -> dict[str, StockMarket]:
        """Fetch detailed stock metrics in one Yahoo quote request."""
        if not symbols:
            return {}
        payload = await self._async_get_quote_payload(symbols)
        results = payload.get("quoteResponse", {}).get("result") or []
        return {
            item["symbol"].upper(): _parse_stock_market(item)
            for item in results
            if isinstance(item, dict) and item.get("symbol")
        }

    async def async_get_stock_history(
        self, symbol: str
    ) -> tuple[StockHistoryPoint, ...]:
        """Fetch the latest 30 daily OHLCV points for dashboard use."""
        normalized = symbol.strip().upper()
        url = CHART_URL.format(symbol=url_quote(normalized, safe=""))
        try:
            async with self._session.get(
                url,
                params={"interval": "1d", "range": "3mo"},
                headers=HEADERS,
                timeout=20,
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise YahooFinanceError(
                f"Could not load history for {normalized}: {err}"
            ) from err

        results = payload.get("chart", {}).get("result") or []
        if not results:
            raise YahooFinanceError(f"No history for {normalized}")
        result = results[0]
        timestamps = result.get("timestamp") or []
        quote = (result.get("indicators", {}).get("quote") or [{}])[0]
        points: list[StockHistoryPoint] = []
        for index, raw_timestamp in enumerate(timestamps):
            close = _item_decimal(quote.get("close"), index)
            if close is None:
                continue
            points.append(
                StockHistoryPoint(
                    timestamp=datetime.fromtimestamp(raw_timestamp, UTC),
                    open=_item_decimal(quote.get("open"), index),
                    high=_item_decimal(quote.get("high"), index),
                    low=_item_decimal(quote.get("low"), index),
                    close=close,
                    volume=_item_int(quote.get("volume"), index),
                )
            )
        return tuple(points[-30:])

    async def _async_get_quote_payload(self, symbols: list[str]) -> dict:
        """Use Yahoo's web cookie and crumb flow for detailed quotes."""
        for attempt in range(2):
            crumb = await self._async_get_crumb()
            try:
                async with self._session.get(
                    QUOTE_URL,
                    params={"symbols": ",".join(symbols), "crumb": crumb},
                    headers=HEADERS,
                    timeout=20,
                ) as response:
                    if response.status in (401, 403) and attempt == 0:
                        self._crumb = None
                        continue
                    response.raise_for_status()
                    payload = await response.json(content_type=None)
                    if not isinstance(payload, dict):
                        raise YahooFinanceError("Unexpected Yahoo quote response")
                    return payload
            except YahooFinanceError:
                raise
            except (ClientError, TimeoutError, ValueError) as err:
                raise YahooFinanceError(
                    f"Could not load detailed Yahoo quotes: {err}"
                ) from err
        raise YahooFinanceError("Yahoo rejected the refreshed quote session")

    async def _async_get_crumb(self) -> str:
        if self._crumb:
            return self._crumb
        async with self._crumb_lock:
            if self._crumb:
                return self._crumb
            try:
                async with self._session.get(
                    CRUMB_URL, headers=HEADERS, timeout=15
                ) as response:
                    response.raise_for_status()
                    crumb = (await response.text()).strip()
            except (ClientError, TimeoutError, ValueError) as err:
                raise YahooFinanceError(
                    f"Could not create Yahoo session: {err}"
                ) from err
            if not crumb or crumb.startswith("{"):
                raise YahooFinanceError("Yahoo returned an invalid session crumb")
            self._crumb = crumb
            return crumb


def _parse_stock_market(item: dict) -> StockMarket:
    """Normalize the detailed Yahoo quote fields used by entities."""
    return StockMarket(
        symbol=str(item["symbol"]).upper(),
        currency=str(item.get("currency") or "USD").upper(),
        fifty_day_average=_decimal(item.get("fiftyDayAverage")),
        fifty_two_week_high=_decimal(item.get("fiftyTwoWeekHigh")),
        fifty_two_week_low=_decimal(item.get("fiftyTwoWeekLow")),
        two_hundred_day_average=_decimal(item.get("twoHundredDayAverage")),
        average_analyst_rating=_text(item.get("averageAnalystRating")),
        average_volume_3month=_int(item.get("averageDailyVolume3Month")),
        average_volume_10day=_int(item.get("averageDailyVolume10Day")),
        bid=_decimal(item.get("bid")),
        bid_size=_int(item.get("bidSize")),
        book_value=_decimal(item.get("bookValue")),
        day_high=_decimal(item.get("regularMarketDayHigh")),
        day_low=_decimal(item.get("regularMarketDayLow")),
        dividend_rate=_decimal(item.get("dividendRate")),
        dividend_yield=_decimal(item.get("dividendYield")),
        earnings_per_share=_decimal(item.get("epsTrailingTwelveMonths")),
        market_cap=_decimal(item.get("marketCap")),
        market_state=_text(item.get("marketState")),
        price_earnings_ratio=_decimal(item.get("trailingPE")),
        shares_outstanding=_int(item.get("sharesOutstanding")),
        volume=_int(item.get("regularMarketVolume")),
    )


def _decimal(value) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _int(value) -> int | None:
    return int(value) if value is not None else None


def _text(value) -> str | None:
    return str(value).strip() if value is not None and str(value).strip() else None


def _item_decimal(values, index: int) -> Decimal | None:
    if not isinstance(values, list) or index >= len(values):
        return None
    return _decimal(values[index])


def _item_int(values, index: int) -> int | None:
    if not isinstance(values, list) or index >= len(values):
        return None
    return _int(values[index])
