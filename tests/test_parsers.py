"""Tests for normalized provider payloads."""

from decimal import Decimal

from custom_components.portfolio_tracker.swissquote import (
    _find_warrant,
    _normalize_valor,
    _swiss_isin_for_valor,
    parse_swissquote_history,
    parse_swissquote_quote,
)
from custom_components.portfolio_tracker.yahoo import _parse_stock_market


def test_swissquote_quote_prefers_requested_midpoint() -> None:
    payload = {
        "fullQuoteData": {
            "productName": "Example Call",
            "productType": "WAR",
            "stockExchangeName": "SIX Structured Products",
            "stockKey": {"currency": "CHF"},
            "quote": {
                "bidPrice": {
                    "amount": "1.20",
                    "status": "AVAILABLE",
                    "timestamp": "2026-11-05T10:00:00Z",
                },
                "askPrice": {
                    "amount": "1.40",
                    "status": "AVAILABLE",
                    "timestamp": "2026-11-05T10:00:01Z",
                },
                "lastPrice": {
                    "amount": "1.25",
                    "status": "AVAILABLE",
                    "timestamp": "2026-11-05T09:59:00Z",
                },
                "closePrice": {"amount": "1.10", "status": "AVAILABLE"},
            },
        }
    }

    quote = parse_swissquote_quote(payload, symbol="123456", price_mode="midpoint")

    assert quote.price == Decimal("1.30")
    assert quote.bid == Decimal("1.20")
    assert quote.ask == Decimal("1.40")
    assert quote.previous_close == Decimal("1.10")
    assert quote.currency == "CHF"
    assert quote.timestamp is not None


def test_swissquote_history_sorts_and_skips_invalid_points() -> None:
    payload = {
        "productInfo": [
            {"time": "2026-11-02T00:00:00Z", "close": "1.20", "volume": 3},
            {"time": "bad", "close": "1.10"},
            {"time": "2026-11-01T00:00:00Z", "close": "1.00", "volume": 2},
        ]
    }

    history = parse_swissquote_history(payload)

    assert [point.close for point in history] == [Decimal("1.00"), Decimal("1.20")]
    assert [point.volume for point in history] == [2, 3]


def test_swiss_valor_lookup_accepts_formatted_number() -> None:
    assert _normalize_valor("12'345 678") == "12345678"
    isin = _swiss_isin_for_valor("12345678")
    payload = {
        "data": [
            {
                "symbol": "unrelated",
                "isin": isin,
                "type": "WAR",
                "exchangeId": 4,
            }
        ]
    }

    assert _find_warrant(payload, "12345678", 4) is not None
    assert _find_warrant(payload, "12345678", 672) is None


def test_swiss_valor_lookup_accepts_current_swissquote_product_types() -> None:
    """The Swissquote search no longer consistently reports WAR or EXO."""
    isin = _swiss_isin_for_valor("150558611")

    for product_type in ("", "AZE"):
        payload = {
            "data": [
                {
                    "symbol": "AFLBTQ",
                    "isin": isin,
                    "type": product_type,
                    "exchangeId": "4",
                }
            ]
        }

        assert _find_warrant(payload, "150558611", 4) is not None
        assert _find_warrant(payload, "150558611", 672) is None


def test_yahoo_market_parser_preserves_text_state() -> None:
    market = _parse_stock_market(
        {
            "symbol": "novn.sw",
            "currency": "chf",
            "regularMarketPrice": 95,
            "fiftyDayAverage": "91.5",
            "regularMarketVolume": 1234,
            "marketState": "POSTPOST",
        }
    )

    assert market.symbol == "NOVN.SW"
    assert market.currency == "CHF"
    assert market.fifty_day_average == Decimal("91.5")
    assert market.volume == 1234
    assert market.market_state == "POSTPOST"
