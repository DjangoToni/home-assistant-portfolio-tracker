"""Transaction-ledger helpers using the moving-average accounting method."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import uuid4

from .const import (
    CONF_AVERAGE_PRICE,
    CONF_QUANTITY,
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
)
from .models import TransactionSummary


def opening_transaction(
    holding: dict[str, Any],
    currency: str,
    transaction_date: str | None = None,
) -> dict[str, Any] | None:
    """Create an editable opening transaction from one legacy position."""
    quantity = Decimal(str(holding.get(CONF_QUANTITY, 0)))
    if quantity <= 0:
        return None
    return {
        CONF_TRANSACTION_ID: uuid4().hex,
        CONF_TRANSACTION_TYPE: "opening",
        CONF_TRANSACTION_DATE: transaction_date or date.today().isoformat(),
        CONF_QUANTITY: float(quantity),
        CONF_TRANSACTION_PRICE: float(holding.get(CONF_AVERAGE_PRICE, 0)),
        CONF_TRANSACTION_PRICE_MODE: holding.get(
            CONF_TRANSACTION_PRICE_MODE, "per_unit"
        ),
        CONF_TRANSACTION_MARKET_PRICE: float(
            holding.get(CONF_TRANSACTION_MARKET_PRICE, 0)
        ),
        CONF_TRANSACTION_MARKET_CURRENCY: str(
            holding.get(CONF_TRANSACTION_MARKET_CURRENCY, "")
        ).upper(),
        CONF_TRANSACTION_CURRENCY: currency.upper(),
        CONF_TRANSACTION_FEES: 0.0,
        CONF_TRANSACTION_TAXES: 0.0,
        CONF_TRANSACTION_EXCHANGE: "",
        CONF_TRANSACTION_NOTE: "",
    }


def migrate_opening_transactions(
    holdings: list[dict[str, Any]], base_currency: str
) -> tuple[list[dict[str, Any]], bool]:
    """Add opening transactions to legacy holdings without changing originals."""
    migrated = deepcopy(holdings)
    changed = False
    for holding in migrated:
        if CONF_TRANSACTIONS in holding:
            continue
        symbol = str(holding.get("symbol", ""))
        currency = _legacy_quote_currency(symbol, base_currency)
        opening = opening_transaction(holding, currency)
        holding[CONF_TRANSACTIONS] = [opening] if opening else []
        changed = True
    return migrated, changed


def _legacy_quote_currency(symbol: str, base_currency: str) -> str:
    """Infer the quote currency used by common Yahoo symbols during migration."""
    upper = symbol.upper()
    if "-" in upper:
        candidate = upper.rsplit("-", 1)[-1]
        if len(candidate) == 3 and candidate.isalpha():
            return candidate
    suffix_currencies = {
        ".SW": "CHF",
        ".L": "GBP",
        ".DE": "EUR",
        ".F": "EUR",
        ".PA": "EUR",
        ".AS": "EUR",
        ".MI": "EUR",
        ".TO": "CAD",
        ".V": "CAD",
        ".AX": "AUD",
        ".T": "JPY",
    }
    for suffix, currency in suffix_currencies.items():
        if upper.endswith(suffix):
            return currency
    # Unsuffixed Yahoo equity symbols are predominantly US listings.
    if upper and "=" not in upper and "^" not in upper:
        return "USD"
    return base_currency.upper()


def transaction_summary(holding: dict[str, Any]) -> TransactionSummary:
    """Derive quantity, cost basis, and realized result from transactions."""
    transactions = holding.get(CONF_TRANSACTIONS)
    if transactions is None:
        quantity = Decimal(str(holding.get(CONF_QUANTITY, 0)))
        average_price = Decimal(str(holding.get(CONF_AVERAGE_PRICE, 0)))
        return TransactionSummary(
            quantity=quantity,
            average_price=average_price,
            realized_gain=Decimal(0),
            fees=Decimal(0),
            taxes=Decimal(0),
            purchase_value=quantity * average_price,
            sale_value=Decimal(0),
            transaction_count=0,
        )

    quantity = Decimal(0)
    average_price = Decimal(0)
    realized_gain = Decimal(0)
    fees_total = Decimal(0)
    taxes_total = Decimal(0)
    purchase_value = Decimal(0)
    sale_value = Decimal(0)
    ordered = sorted(
        enumerate(transactions),
        key=lambda item: (str(item[1].get(CONF_TRANSACTION_DATE, "")), item[0]),
    )
    for _, transaction in ordered:
        transaction_type = str(transaction.get(CONF_TRANSACTION_TYPE, "buy"))
        traded_quantity = Decimal(str(transaction.get(CONF_QUANTITY, 0)))
        fees = Decimal(str(transaction.get(CONF_TRANSACTION_FEES, 0)))
        taxes = Decimal(str(transaction.get(CONF_TRANSACTION_TAXES, 0)))
        fees_total += fees
        taxes_total += taxes
        if transaction_type in {"opening", "buy"}:
            gross_cost = transaction_cash_amount(transaction)
            new_quantity = quantity + traded_quantity
            average_price = (
                (quantity * average_price + gross_cost) / new_quantity
                if new_quantity
                else Decimal(0)
            )
            quantity = new_quantity
            purchase_value += gross_cost
        elif transaction_type == "sell":
            proceeds = transaction_cash_amount(transaction)
            realized_gain += proceeds - traded_quantity * average_price
            quantity -= traded_quantity
            sale_value += proceeds
            if quantity == 0:
                average_price = Decimal(0)

    return TransactionSummary(
        quantity=quantity,
        average_price=average_price,
        realized_gain=realized_gain,
        fees=fees_total,
        taxes=taxes_total,
        purchase_value=purchase_value,
        sale_value=sale_value,
        transaction_count=len(transactions),
    )


def transaction_cash_amount(transaction: dict[str, Any]) -> Decimal:
    """Return the complete purchase cost or net sale proceeds."""
    entered_price = Decimal(str(transaction.get(CONF_TRANSACTION_PRICE, 0)))
    market_price = Decimal(
        str(transaction.get(CONF_TRANSACTION_MARKET_PRICE, 0))
    )
    if (
        transaction.get(CONF_TRANSACTION_PRICE_MODE, "per_unit") == "total"
        or market_price > 0
    ):
        return entered_price
    quantity = Decimal(str(transaction.get(CONF_QUANTITY, 0)))
    fees = Decimal(str(transaction.get(CONF_TRANSACTION_FEES, 0)))
    taxes = Decimal(str(transaction.get(CONF_TRANSACTION_TAXES, 0)))
    trade_value = quantity * entered_price
    if transaction.get(CONF_TRANSACTION_TYPE) in {"opening", "buy"}:
        return trade_value + fees + taxes
    return trade_value - fees - taxes


def transaction_summary_in_currency(
    holding: dict[str, Any],
    target_currency: str,
    fx_rates: dict[str, Decimal],
) -> TransactionSummary | None:
    """Return a ledger summary converted into one accounting currency.

    ``fx_rates`` contains current rates from each currency into the portfolio
    base currency. Converting source to target therefore uses source/target.
    """
    transactions = holding.get(CONF_TRANSACTIONS)
    if transactions is None:
        return transaction_summary(holding)

    target = target_currency.upper()
    target_rate = fx_rates.get(target)
    if target_rate is None:
        return None
    converted = deepcopy(holding)
    converted_transactions = []
    for transaction in transactions:
        item = deepcopy(transaction)
        source = str(item.get(CONF_TRANSACTION_CURRENCY, target)).upper()
        source_rate = fx_rates.get(source)
        if source_rate is None:
            return None
        factor = source_rate / target_rate
        for key in (
            CONF_TRANSACTION_PRICE,
            CONF_TRANSACTION_FEES,
            CONF_TRANSACTION_TAXES,
        ):
            item[key] = Decimal(str(item.get(key, 0))) * factor
        item[CONF_TRANSACTION_CURRENCY] = target
        converted_transactions.append(item)
    converted[CONF_TRANSACTIONS] = converted_transactions
    return transaction_summary(converted)


def transaction_balances_are_valid(holding: dict[str, Any]) -> bool:
    """Return whether chronological sells never exceed the available quantity."""
    balance = Decimal(0)
    transactions = holding.get(CONF_TRANSACTIONS, [])
    ordered = sorted(
        enumerate(transactions),
        key=lambda item: (str(item[1].get(CONF_TRANSACTION_DATE, "")), item[0]),
    )
    for _, transaction in ordered:
        quantity = Decimal(str(transaction.get(CONF_QUANTITY, 0)))
        if transaction.get(CONF_TRANSACTION_TYPE) in {"opening", "buy"}:
            balance += quantity
        else:
            balance -= quantity
        if balance < 0:
            return False
    return True
