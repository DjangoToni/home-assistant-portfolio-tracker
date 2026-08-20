"""Data models for Portfolio Tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import NotRequired, TypedDict


class Holding(TypedDict):
    """A user-managed portfolio position."""

    holding_id: str
    symbol: str
    name: str
    asset_type: str
    quantity: float
    average_price: float
    coingecko_id: NotRequired[str]
    display_currency: NotRequired[str]
    transactions: NotRequired[list[Transaction]]
    watch_only: NotRequired[bool]
    alert_below: NotRequired[float]
    alert_above: NotRequired[float]


class Transaction(TypedDict):
    """One user-managed portfolio transaction."""

    transaction_id: str
    transaction_type: str
    transaction_date: str
    quantity: float
    transaction_price: float
    transaction_price_mode: NotRequired[str]
    transaction_market_price: NotRequired[float]
    transaction_market_currency: NotRequired[str]
    transaction_currency: str
    transaction_fees: float
    transaction_taxes: float
    transaction_exchange: str
    transaction_note: str


@dataclass(frozen=True, slots=True)
class TransactionSummary:
    """Position state derived with the moving-average method."""

    quantity: Decimal
    average_price: Decimal
    realized_gain: Decimal
    fees: Decimal
    taxes: Decimal
    purchase_value: Decimal
    sale_value: Decimal
    transaction_count: int


@dataclass(frozen=True, slots=True)
class Quote:
    """Normalized market quote."""

    symbol: str
    name: str
    price: Decimal
    previous_close: Decimal | None
    currency: str
    exchange: str | None
    instrument_type: str | None
    timestamp: datetime | None

    @property
    def daily_change_percent(self) -> Decimal | None:
        """Return daily percentage change."""
        if not self.previous_close:
            return None
        return (self.price - self.previous_close) / self.previous_close * Decimal(100)


@dataclass(frozen=True, slots=True)
class PortfolioData:
    """Coordinator payload."""

    quotes: dict[str, Quote]
    fx_rates: dict[str, Decimal]
    base_currency: str = "CHF"
    crypto_markets: dict[str, CryptoMarket] = field(default_factory=dict)
    crypto_history: dict[str, tuple[CryptoHistoryPoint, ...]] = field(
        default_factory=dict
    )
    stock_markets: dict[str, StockMarket] = field(default_factory=dict)
    stock_history: dict[str, tuple[StockHistoryPoint, ...]] = field(
        default_factory=dict
    )


@dataclass(frozen=True, slots=True)
class CryptoMarket:
    """Normalized CoinGecko market data in the selected display currency."""

    coin_id: str
    symbol: str
    currency: str
    high_24h: Decimal | None
    low_24h: Decimal | None
    total_volume: Decimal | None
    ath: Decimal | None
    atl: Decimal | None
    circulating_supply: Decimal | None
    fully_diluted_valuation: Decimal | None
    market_cap: Decimal | None
    market_cap_change_24h: Decimal | None
    market_cap_rank: int | None
    price_change_24h: Decimal | None
    total_supply: Decimal | None
    last_updated: datetime | None


@dataclass(frozen=True, slots=True)
class CryptoHistoryPoint:
    """One compact historical CoinGecko data point."""

    timestamp: datetime
    price: Decimal | None
    market_cap: Decimal | None
    volume: Decimal | None


@dataclass(frozen=True, slots=True)
class StockMarket:
    """Normalized Yahoo stock details in the instrument quote currency."""

    symbol: str
    currency: str
    fifty_day_average: Decimal | None
    fifty_two_week_high: Decimal | None
    fifty_two_week_low: Decimal | None
    two_hundred_day_average: Decimal | None
    average_analyst_rating: str | None
    average_volume_3month: int | None
    average_volume_10day: int | None
    bid: Decimal | None
    bid_size: int | None
    book_value: Decimal | None
    day_high: Decimal | None
    day_low: Decimal | None
    dividend_rate: Decimal | None
    dividend_yield: Decimal | None
    earnings_per_share: Decimal | None
    market_cap: Decimal | None
    market_state: str | None
    price_earnings_ratio: Decimal | None
    shares_outstanding: int | None
    volume: int | None


@dataclass(frozen=True, slots=True)
class StockHistoryPoint:
    """One daily Yahoo OHLCV data point."""

    timestamp: datetime
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal
    volume: int | None
