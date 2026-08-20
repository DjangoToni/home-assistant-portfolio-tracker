"""Pure portfolio calculations.

This module deliberately has no Home Assistant dependencies. Keeping all
financial calculations here makes their behavior explicit and independently
testable.
"""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from decimal import Decimal
from typing import Any

from .const import (
    CONF_ASSET_TYPE,
    CONF_WATCH_ONLY,
    crypto_currency_for_holding,
    CONF_SYMBOL,
    CONF_TRANSACTION_CURRENCY,
    CONF_TRANSACTION_FEES,
    CONF_TRANSACTION_MARKET_CURRENCY,
    CONF_TRANSACTION_MARKET_PRICE,
    CONF_TRANSACTION_PRICE,
    CONF_TRANSACTION_PRICE_MODE,
    CONF_TRANSACTION_TAXES,
    CONF_TRANSACTIONS,
)
from .models import PortfolioData, Quote, TransactionSummary
from .transactions import transaction_summary, transaction_summary_in_currency

HoldingValue = dict[str, Any]


def professional_holdings(holdings: list[HoldingValue]) -> list[HoldingValue]:
    """Return securities used by professional analytics, excluding crypto."""
    return [
        holding
        for holding in holdings
        if holding.get(CONF_ASSET_TYPE) != "crypto"
        and not holding.get(CONF_WATCH_ONLY, False)
    ]


def portfolio_holdings(holdings: list[HoldingValue]) -> list[HoldingValue]:
    """Return owned positions, excluding assets that are watched only."""
    return [holding for holding in holdings if not holding.get(CONF_WATCH_ONLY, False)]


def quote_for(data: PortfolioData, holding: HoldingValue) -> Quote | None:
    """Return the quote belonging to a position."""
    return data.quotes.get(holding[CONF_SYMBOL])


def holding_price(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return a position's price in its quote currency."""
    quote = quote_for(data, holding)
    return quote.price if quote else None


def holding_alert_price(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return the price in the currency shown by the primary price sensor."""
    price = holding_price(data, holding)
    if price is None or holding.get(CONF_ASSET_TYPE) != "crypto":
        return price
    return convert_quote_amount(
        data,
        holding,
        price,
        crypto_currency_for_holding(holding, data.base_currency),
    )


def holding_previous_close(
    data: PortfolioData, holding: HoldingValue
) -> Decimal | None:
    """Return the instrument's previous closing price."""
    quote = quote_for(data, holding)
    return quote.previous_close if quote else None


def holding_quantity(data: PortfolioData, holding: HoldingValue) -> Decimal:
    """Return the configured amount owned.

    ``data`` is accepted so the function shares the entity value-function
    signature used by live quote calculations.
    """
    del data
    return _quantity(holding)


def holding_average_price(
    data: PortfolioData, holding: HoldingValue
) -> Decimal | None:
    """Return the currency-aware average purchase price."""
    summary = _holding_market_summary(data, holding)
    if summary is None:
        summary = holding_transaction_summary(data, holding)
    return summary.average_price if summary else None


def convert_quote_amount(
    data: PortfolioData,
    holding: HoldingValue,
    amount: Decimal | None,
    target_currency: str,
) -> Decimal | None:
    """Convert an amount from the quote currency into another currency."""
    quote = quote_for(data, holding)
    if quote is None or amount is None:
        return None
    target = target_currency.upper()
    if quote.currency == target:
        return amount
    source_rate = data.fx_rates.get(quote.currency)
    target_rate = data.fx_rates.get(target)
    if source_rate is None or target_rate is None:
        return None
    return amount * source_rate / target_rate


def holding_value(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return current position value in the portfolio base currency."""
    quote = quote_for(data, holding)
    if not quote or (rate := data.fx_rates.get(quote.currency)) is None:
        return None
    return quote.price * _quantity(holding) * rate


def holding_cost(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return cost basis converted using the current exchange rate.

    Version 0.1 stores an average purchase price in the instrument currency,
    but no historical purchase-date FX rate. This therefore measures market
    performance while neutralizing historical FX effects.
    """
    if CONF_TRANSACTIONS not in holding:
        quote = quote_for(data, holding)
        if not quote or (rate := data.fx_rates.get(quote.currency)) is None:
            return None
        summary = transaction_summary(holding)
        return summary.average_price * summary.quantity * rate
    summary = _holding_base_summary(data, holding)
    if summary is None:
        return None
    return summary.average_price * summary.quantity


def holding_gain(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return unrealized gain or loss in the base currency."""
    value = holding_value(data, holding)
    cost = holding_cost(data, holding)
    return value - cost if value is not None and cost is not None else None


def holding_gain_percent(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return unrealized return percentage."""
    gain = holding_gain(data, holding)
    cost = holding_cost(data, holding)
    return gain / cost * Decimal(100) if gain is not None and cost else None


def holding_daily_percent(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return the instrument's daily percentage change."""
    quote = quote_for(data, holding)
    return quote.daily_change_percent if quote else None


def holding_realized_gain(
    data: PortfolioData, holding: HoldingValue
) -> Decimal | None:
    """Return realized transaction gain converted to the portfolio currency."""
    summary = _holding_base_summary(data, holding)
    return summary.realized_gain if summary else None


def holding_fees(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return accumulated transaction fees in the portfolio currency."""
    summary = _holding_base_summary(data, holding)
    return summary.fees if summary else None


def holding_taxes(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return accumulated transaction taxes in the portfolio currency."""
    summary = _holding_base_summary(data, holding)
    return summary.taxes if summary else None


def holding_purchases(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return cumulative gross purchases in the portfolio currency."""
    summary = _holding_base_summary(data, holding)
    return summary.purchase_value if summary else None


def holding_sales(data: PortfolioData, holding: HoldingValue) -> Decimal | None:
    """Return cumulative net sale proceeds in the portfolio currency."""
    summary = _holding_base_summary(data, holding)
    return summary.sale_value if summary else None


def holding_transaction_summary(
    data: PortfolioData, holding: HoldingValue
) -> TransactionSummary | None:
    """Return transactions normalized into the instrument quote currency."""
    quote = quote_for(data, holding)
    if quote is None:
        return None
    return transaction_summary_in_currency(holding, quote.currency, data.fx_rates)


def _holding_base_summary(
    data: PortfolioData, holding: HoldingValue
) -> TransactionSummary | None:
    """Return the transaction ledger in the portfolio base currency."""
    if CONF_TRANSACTIONS not in holding:
        quote = quote_for(data, holding)
        if quote is None or (rate := data.fx_rates.get(quote.currency)) is None:
            return None
        summary = transaction_summary(holding)
        return TransactionSummary(
            quantity=summary.quantity,
            average_price=summary.average_price * rate,
            realized_gain=summary.realized_gain * rate,
            fees=summary.fees * rate,
            taxes=summary.taxes * rate,
            purchase_value=summary.purchase_value * rate,
            sale_value=summary.sale_value * rate,
            transaction_count=summary.transaction_count,
        )
    return transaction_summary_in_currency(
        holding, data.base_currency, data.fx_rates
    )


def _holding_market_summary(
    data: PortfolioData, holding: HoldingValue
) -> TransactionSummary | None:
    """Return average execution prices using optional recorded market rates."""
    quote = quote_for(data, holding)
    transactions = holding.get(CONF_TRANSACTIONS)
    if quote is None or not transactions:
        return None
    if not any(
        Decimal(str(item.get(CONF_TRANSACTION_MARKET_PRICE, 0))) > 0
        for item in transactions
    ):
        return None
    adjusted = deepcopy(holding)
    for item in adjusted[CONF_TRANSACTIONS]:
        market_price = Decimal(
            str(item.get(CONF_TRANSACTION_MARKET_PRICE, 0))
        )
        if market_price <= 0:
            continue
        item[CONF_TRANSACTION_PRICE] = market_price
        item[CONF_TRANSACTION_PRICE_MODE] = "per_unit"
        item[CONF_TRANSACTION_MARKET_PRICE] = 0
        item[CONF_TRANSACTION_CURRENCY] = str(
            item.get(CONF_TRANSACTION_MARKET_CURRENCY, quote.currency)
            or quote.currency
        ).upper()
        item[CONF_TRANSACTION_FEES] = 0
        item[CONF_TRANSACTION_TAXES] = 0
    return transaction_summary_in_currency(
        adjusted, quote.currency, data.fx_rates
    )


def portfolio_value(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return total value, or None when any position lacks current data."""
    return _complete_sum(data, holdings, holding_value)


def portfolio_cost(data: PortfolioData, holdings: list[HoldingValue]) -> Decimal | None:
    """Return total cost basis, or None when any position lacks data."""
    return _complete_sum(data, holdings, holding_cost)


def portfolio_gain(data: PortfolioData, holdings: list[HoldingValue]) -> Decimal | None:
    """Return total unrealized gain or loss."""
    value = portfolio_value(data, holdings)
    cost = portfolio_cost(data, holdings)
    return value - cost if value is not None and cost is not None else None


def portfolio_gain_percent(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return total unrealized percentage return."""
    gain = portfolio_gain(data, holdings)
    cost = portfolio_cost(data, holdings)
    return gain / cost * Decimal(100) if gain is not None and cost else None


def portfolio_realized_gain(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return realized gains from all portfolio transactions."""
    return _complete_sum(data, holdings, holding_realized_gain)


def portfolio_fees(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return all transaction fees converted to the portfolio currency."""
    return _complete_sum(data, holdings, holding_fees)


def portfolio_taxes(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return all transaction taxes converted to the portfolio currency."""
    return _complete_sum(data, holdings, holding_taxes)


def portfolio_purchases(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return all gross purchases converted to the portfolio currency."""
    return _complete_sum(data, holdings, holding_purchases)


def portfolio_sales(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return all net sales converted to the portfolio currency."""
    return _complete_sum(data, holdings, holding_sales)


def portfolio_net_invested(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return purchases less sale proceeds."""
    purchases = portfolio_purchases(data, holdings)
    sales = portfolio_sales(data, holdings)
    return purchases - sales if purchases is not None and sales is not None else None


def portfolio_total_gain(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return lifetime result including realized and unrealized performance."""
    value = portfolio_value(data, holdings)
    net_invested = portfolio_net_invested(data, holdings)
    return (
        value - net_invested
        if value is not None and net_invested is not None
        else None
    )


def portfolio_total_return(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return lifetime result as a percentage of cumulative purchases."""
    gain = portfolio_total_gain(data, holdings)
    purchases = portfolio_purchases(data, holdings)
    return gain / purchases * Decimal(100) if gain is not None and purchases else None


def portfolio_transaction_count(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal:
    """Return the total number of recorded transactions."""
    del data
    return Decimal(
        sum(transaction_summary(holding).transaction_count for holding in holdings)
    )


def portfolio_daily_percent(
    data: PortfolioData, holdings: list[HoldingValue]
) -> Decimal | None:
    """Return quantity-weighted daily portfolio performance.

    A missing quote, previous close, or exchange rate makes the result unknown
    instead of silently understating the portfolio.
    """
    current = Decimal(0)
    previous = Decimal(0)
    for holding in holdings:
        quote = quote_for(data, holding)
        if (
            not quote
            or quote.previous_close is None
            or (rate := data.fx_rates.get(quote.currency)) is None
        ):
            return None
        quantity = _quantity(holding)
        current += quote.price * quantity * rate
        previous += quote.previous_close * quantity * rate
    if not holdings:
        return Decimal(0)
    return (current - previous) / previous * Decimal(100) if previous else None


def _complete_sum(
    data: PortfolioData,
    holdings: list[HoldingValue],
    value_fn: Callable[[PortfolioData, HoldingValue], Decimal | None],
) -> Decimal | None:
    values = [value_fn(data, holding) for holding in holdings]
    if any(value is None for value in values):
        return None
    return sum(values, start=Decimal(0))  # type: ignore[arg-type]


def _quantity(holding: HoldingValue) -> Decimal:
    return transaction_summary(holding).quantity
