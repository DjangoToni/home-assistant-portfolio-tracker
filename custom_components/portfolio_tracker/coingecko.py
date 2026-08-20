"""Asynchronous CoinGecko client for cryptocurrency market metrics."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from aiohttp import ClientError, ClientSession

from .models import CryptoHistoryPoint, CryptoMarket

API_URL = "https://api.coingecko.com/api/v3"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "HomeAssistant PortfolioTracker/0.3",
}


class CoinGeckoError(Exception):
    """Base CoinGecko client error."""


class CoinGeckoCoinNotFound(CoinGeckoError):
    """Raised when CoinGecko does not know a coin ID."""


class CoinGeckoClient:
    """Fetch normalized CoinGecko market and 30-day history data."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_get_markets(
        self, coin_ids: list[str], currency: str
    ) -> dict[str, CryptoMarket]:
        """Fetch market metrics for multiple IDs in a single request."""
        if not coin_ids:
            return {}
        payload = await self._async_get(
            "/coins/markets",
            {
                "vs_currency": currency.lower(),
                "ids": ",".join(coin_ids),
                "order": "market_cap_desc",
                "sparkline": "false",
                "precision": "full",
            },
        )
        if not isinstance(payload, list):
            raise CoinGeckoError("Unexpected market response")
        markets = {
            item["id"]: self._parse_market(item, currency)
            for item in payload
            if isinstance(item, dict) and item.get("id")
        }
        if len(coin_ids) == 1 and not markets:
            raise CoinGeckoCoinNotFound(coin_ids[0])
        return markets

    async def async_get_history(
        self, coin_id: str, currency: str
    ) -> tuple[CryptoHistoryPoint, ...]:
        """Fetch compact daily price, market-cap, and volume history."""
        payload = await self._async_get(
            f"/coins/{coin_id}/market_chart",
            {
                "vs_currency": currency.lower(),
                "days": "30",
                "interval": "daily",
                "precision": "full",
            },
        )
        prices = _series(payload.get("prices"))
        market_caps = _series(payload.get("market_caps"))
        volumes = _series(payload.get("total_volumes"))
        timestamps = sorted(set(prices) | set(market_caps) | set(volumes))
        return tuple(
            CryptoHistoryPoint(
                timestamp=datetime.fromtimestamp(timestamp / 1000, UTC),
                price=prices.get(timestamp),
                market_cap=market_caps.get(timestamp),
                volume=volumes.get(timestamp),
            )
            for timestamp in timestamps
        )

    async def _async_get(self, path: str, params: dict[str, str]) -> Any:
        try:
            async with self._session.get(
                f"{API_URL}{path}",
                params=params,
                headers=HEADERS,
                timeout=20,
            ) as response:
                if response.status == 404:
                    raise CoinGeckoCoinNotFound(path)
                response.raise_for_status()
                return await response.json(content_type=None)
        except CoinGeckoError:
            raise
        except (ClientError, TimeoutError, ValueError) as err:
            raise CoinGeckoError(f"Could not load CoinGecko data: {err}") from err

    @staticmethod
    def _parse_market(item: dict[str, Any], currency: str) -> CryptoMarket:
        rank = item.get("market_cap_rank")
        return CryptoMarket(
            coin_id=item["id"],
            symbol=str(item.get("symbol") or "").upper(),
            currency=currency.upper(),
            high_24h=_decimal(item.get("high_24h")),
            low_24h=_decimal(item.get("low_24h")),
            total_volume=_decimal(item.get("total_volume")),
            ath=_decimal(item.get("ath")),
            atl=_decimal(item.get("atl")),
            circulating_supply=_decimal(item.get("circulating_supply")),
            fully_diluted_valuation=_decimal(item.get("fully_diluted_valuation")),
            market_cap=_decimal(item.get("market_cap")),
            market_cap_change_24h=_decimal(item.get("market_cap_change_24h")),
            market_cap_rank=int(rank) if rank is not None else None,
            price_change_24h=_decimal(item.get("price_change_24h")),
            total_supply=_decimal(item.get("total_supply")),
            last_updated=_datetime(item.get("last_updated")),
        )


def _series(value: Any) -> dict[int, Decimal | None]:
    if not isinstance(value, list):
        return {}
    return {
        int(point[0]): _decimal(point[1])
        for point in value
        if isinstance(point, list) and len(point) >= 2
    }


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
