"""Cash-flow-adjusted portfolio performance calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from .const import (
    CONF_ASSET_TYPE,
    CONF_QUANTITY,
    CONF_SYMBOL,
    CONF_TRANSACTION_CURRENCY,
    CONF_TRANSACTION_DATE,
    CONF_TRANSACTION_TYPE,
    CONF_TRANSACTIONS,
    coingecko_id_for_holding,
    crypto_currency_for_holding,
    crypto_data_key,
)
from .models import PortfolioData
from .transactions import transaction_cash_amount


@dataclass(frozen=True, slots=True)
class PerformancePoint:
    """One cash-flow-adjusted daily portfolio performance point."""

    date: str
    value: Decimal
    portfolio_percent: Decimal
    benchmark_percent: Decimal | None


@dataclass(frozen=True, slots=True)
class PerformanceReport:
    """Professional performance summary for the available history window."""

    time_weighted_return: Decimal | None
    benchmark_return: Decimal | None
    excess_return: Decimal | None
    points: tuple[PerformancePoint, ...]


def build_performance_report(
    data: PortfolioData,
    holdings: list[dict[str, Any]],
    benchmark_symbol: str,
    base_currency: str,
) -> PerformanceReport:
    """Build a daily return series adjusted for purchases and sales."""
    asset_series: list[tuple[dict[str, Any], dict[str, Decimal], Decimal]] = []
    all_dates: set[str] = set()
    for holding in holdings:
        series, currency = _holding_price_series(data, holding, base_currency)
        if not series:
            continue
        rate = data.fx_rates.get(currency)
        if rate is None:
            continue
        asset_series.append((holding, series, rate))
        all_dates.update(series)

    benchmark_series = _stock_close_series(data, benchmark_symbol)
    all_dates.update(benchmark_series)
    if not asset_series or not all_dates:
        return PerformanceReport(None, None, None, ())

    flows = _daily_cash_flows(holdings, data.fx_rates)
    all_dates.update(flows)
    sorted_dates = sorted(all_dates)
    last_prices: dict[str, Decimal] = {}
    previous_value: Decimal | None = None
    cumulative = Decimal(1)
    benchmark_start: Decimal | None = None
    benchmark_last: Decimal | None = None
    points: list[PerformancePoint] = []

    for day in sorted_dates:
        value = Decimal(0)
        complete = True
        for holding, series, rate in asset_series:
            symbol = str(holding[CONF_SYMBOL])
            if day in series:
                last_prices[symbol] = series[day]
            quantity = _quantity_on_date(holding, day)
            if quantity <= 0:
                continue
            price = last_prices.get(symbol)
            if price is None:
                complete = False
                break
            value += quantity * price * rate
        if not complete or value <= 0:
            continue

        if previous_value is not None and previous_value > 0:
            adjusted_value = value - flows.get(day, Decimal(0))
            if adjusted_value >= 0:
                cumulative *= adjusted_value / previous_value
        previous_value = value

        benchmark_value = benchmark_series.get(day, benchmark_last)
        if benchmark_value is not None:
            benchmark_last = benchmark_value
            if benchmark_start is None:
                benchmark_start = benchmark_value
        benchmark_percent = (
            (benchmark_last / benchmark_start - Decimal(1)) * Decimal(100)
            if benchmark_last is not None and benchmark_start
            else None
        )
        points.append(
            PerformancePoint(
                date=day,
                value=value,
                portfolio_percent=(cumulative - Decimal(1)) * Decimal(100),
                benchmark_percent=benchmark_percent,
            )
        )

    if not points:
        return PerformanceReport(None, None, None, ())
    time_weighted_return = points[-1].portfolio_percent
    benchmark_return = points[-1].benchmark_percent
    return PerformanceReport(
        time_weighted_return=time_weighted_return,
        benchmark_return=benchmark_return,
        excess_return=(
            time_weighted_return - benchmark_return
            if benchmark_return is not None
            else None
        ),
        points=tuple(points),
    )


def _holding_price_series(
    data: PortfolioData, holding: dict[str, Any], base_currency: str
) -> tuple[dict[str, Decimal], str]:
    if holding.get(CONF_ASSET_TYPE) == "crypto":
        coin_id = coingecko_id_for_holding(holding)
        currency = crypto_currency_for_holding(holding, base_currency)
        history = (
            data.crypto_history.get(crypto_data_key(coin_id, currency), ())
            if coin_id
            else ()
        )
        return (
            {
                point.timestamp.date().isoformat(): point.price
                for point in history
                if point.price is not None
            },
            currency,
        )
    quote = data.quotes.get(holding[CONF_SYMBOL])
    return (
        _stock_close_series(data, holding[CONF_SYMBOL]),
        quote.currency if quote else base_currency,
    )


def _stock_close_series(data: PortfolioData, symbol: str) -> dict[str, Decimal]:
    return {
        point.timestamp.date().isoformat(): point.close
        for point in data.stock_history.get(symbol, ())
    }


def _quantity_on_date(holding: dict[str, Any], day: str) -> Decimal:
    transactions = holding.get(CONF_TRANSACTIONS)
    if transactions is None:
        return Decimal(str(holding.get(CONF_QUANTITY, 0)))
    quantity = Decimal(0)
    for transaction in transactions:
        if str(transaction.get(CONF_TRANSACTION_DATE, "")) > day:
            continue
        amount = Decimal(str(transaction.get(CONF_QUANTITY, 0)))
        if transaction.get(CONF_TRANSACTION_TYPE) in {"opening", "buy"}:
            quantity += amount
        elif transaction.get(CONF_TRANSACTION_TYPE) == "sell":
            quantity -= amount
    return quantity


def _daily_cash_flows(
    holdings: list[dict[str, Any]], fx_rates: dict[str, Decimal]
) -> dict[str, Decimal]:
    flows: dict[str, Decimal] = {}
    for holding in holdings:
        for transaction in holding.get(CONF_TRANSACTIONS, []):
            day = str(transaction.get(CONF_TRANSACTION_DATE, ""))
            try:
                date.fromisoformat(day)
            except ValueError:
                continue
            currency = str(transaction.get(CONF_TRANSACTION_CURRENCY, "")).upper()
            rate = fx_rates.get(currency)
            if rate is None:
                continue
            amount = transaction_cash_amount(transaction)
            if transaction.get(CONF_TRANSACTION_TYPE) in {"opening", "buy"}:
                flow = amount * rate
            else:
                flow = -amount * rate
            flows[day] = flows.get(day, Decimal(0)) + flow
    return flows
