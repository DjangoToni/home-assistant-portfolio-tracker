"""Tests for transaction-ledger accounting."""

from decimal import Decimal

from custom_components.portfolio_tracker.transactions import (
    transaction_balances_are_valid,
    transaction_cash_amount,
    transaction_summary,
    transaction_summary_in_currency,
)


def _transaction(
    transaction_type: str,
    transaction_date: str,
    quantity: float,
    price: float,
    *,
    currency: str = "CHF",
    fees: float = 0,
    taxes: float = 0,
    price_mode: str = "per_unit",
) -> dict:
    return {
        "transaction_type": transaction_type,
        "transaction_date": transaction_date,
        "quantity": quantity,
        "transaction_price": price,
        "transaction_price_mode": price_mode,
        "transaction_market_price": 0,
        "transaction_market_currency": "",
        "transaction_currency": currency,
        "transaction_fees": fees,
        "transaction_taxes": taxes,
    }


def test_moving_average_sale_includes_costs() -> None:
    holding = {
        "transactions": [
            _transaction("opening", "2026-01-01", 10, 100),
            _transaction("buy", "2026-02-01", 10, 120, fees=10),
            _transaction("sell", "2026-03-01", 5, 150, fees=5, taxes=5),
        ]
    }

    summary = transaction_summary(holding)

    assert summary.quantity == Decimal("15")
    assert summary.average_price == Decimal("110.5")
    assert summary.realized_gain == Decimal("187.5")
    assert summary.fees == Decimal("15")
    assert summary.taxes == Decimal("5")
    assert summary.purchase_value == Decimal("2210")
    assert summary.sale_value == Decimal("740")
    assert summary.transaction_count == 3


def test_total_price_mode_uses_entered_cash_amount() -> None:
    transaction = _transaction(
        "buy", "2026-01-01", 10, 1025, fees=20, taxes=5, price_mode="total"
    )

    assert transaction_cash_amount(transaction) == Decimal("1025")


def test_balances_are_checked_chronologically() -> None:
    invalid = {
        "transactions": [
            _transaction("buy", "2026-02-01", 5, 100),
            _transaction("sell", "2026-01-15", 1, 110),
        ]
    }
    valid = {
        "transactions": [
            _transaction("sell", "2026-02-01", 5, 110),
            _transaction("buy", "2026-01-15", 5, 100),
        ]
    }

    assert transaction_balances_are_valid(invalid) is False
    assert transaction_balances_are_valid(valid) is True


def test_transactions_convert_into_target_currency() -> None:
    holding = {
        "transactions": [
            _transaction("buy", "2026-01-01", 2, 100, currency="USD", fees=10)
        ]
    }

    summary = transaction_summary_in_currency(
        holding,
        "CHF",
        {"CHF": Decimal("1"), "USD": Decimal("0.8")},
    )

    assert summary is not None
    assert summary.quantity == Decimal("2")
    assert summary.average_price == Decimal("84")
    assert summary.purchase_value == Decimal("168")
    assert summary.fees == Decimal("8")


def test_missing_exchange_rate_returns_none() -> None:
    holding = {
        "transactions": [
            _transaction("buy", "2026-01-01", 1, 100, currency="USD")
        ]
    }

    assert transaction_summary_in_currency(
        holding, "CHF", {"CHF": Decimal("1")}
    ) is None
