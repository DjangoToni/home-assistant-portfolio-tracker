"""Constants for Portfolio Tracker."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "portfolio_tracker"
PLATFORMS: Final = ["sensor", "binary_sensor"]
FRONTEND_VERSION: Final = "1.4.1"
FRONTEND_URL: Final = "/portfolio_tracker/frontend"

CONF_PORTFOLIO_NAME: Final = "portfolio_name"
CONF_BASE_CURRENCY: Final = "base_currency"
CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_HOLDINGS: Final = "holdings"
CONF_HOLDING_ID: Final = "holding_id"
CONF_SYMBOL: Final = "symbol"
CONF_NAME: Final = "name"
CONF_ASSET_TYPE: Final = "asset_type"
CONF_QUANTITY: Final = "quantity"
CONF_AVERAGE_PRICE: Final = "average_price"
CONF_COINGECKO_ID: Final = "coingecko_id"
CONF_DISPLAY_CURRENCY: Final = "display_currency"
CONF_TRANSACTIONS: Final = "transactions"
CONF_INDEXES: Final = "indexes"
CONF_INDEX_SYMBOL: Final = "index_symbol"
CONF_BENCHMARK_INDEX: Final = "benchmark_index"
CONF_TRANSACTION_ID: Final = "transaction_id"
CONF_TRANSACTION_TYPE: Final = "transaction_type"
CONF_TRANSACTION_DATE: Final = "transaction_date"
CONF_TRANSACTION_PRICE: Final = "transaction_price"
CONF_TRANSACTION_PRICE_MODE: Final = "transaction_price_mode"
CONF_TRANSACTION_MARKET_PRICE: Final = "transaction_market_price"
CONF_TRANSACTION_MARKET_CURRENCY: Final = "transaction_market_currency"
CONF_TRANSACTION_CURRENCY: Final = "transaction_currency"
CONF_TRANSACTION_FEES: Final = "transaction_fees"
CONF_TRANSACTION_TAXES: Final = "transaction_taxes"
CONF_TRANSACTION_EXCHANGE: Final = "transaction_exchange"
CONF_TRANSACTION_NOTE: Final = "transaction_note"
CONF_WATCH_ONLY: Final = "watch_only"
CONF_ALERT_ABOVE: Final = "alert_above"
CONF_ALERT_BELOW: Final = "alert_below"

DEFAULT_BASE_CURRENCY: Final = "CHF"
DEFAULT_UPDATE_INTERVAL: Final = 15
MIN_UPDATE_INTERVAL: Final = 5

ASSET_TYPES: Final = ["stock", "etf", "crypto", "fund", "currency", "other"]
CRYPTO_DISPLAY_CURRENCIES: Final = ["CHF", "EUR", "USD", "GBP", "JPY", "CAD", "AUD"]
TRANSACTION_TYPES: Final = ["opening", "buy", "sell"]
TRANSACTION_PRICE_MODES: Final = ["per_unit", "total"]
INDEX_PRESETS: Final = {
    "^SSMI": "SMI - Swiss Market Index",
    "^GDAXI": "DAX - Deutscher Aktienindex",
    "^DJI": "Dow Jones Industrial Average",
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ Composite",
    "^STOXX50E": "EURO STOXX 50",
}
DEFAULT_INDEXES: Final = ["^SSMI", "^GDAXI", "^DJI", "^GSPC"]
DEFAULT_BENCHMARK_INDEX: Final = "^SSMI"

# Existing portfolios can use common Yahoo crypto symbols without being edited.
# A manually configured CoinGecko ID always takes precedence.
COINGECKO_IDS_BY_SYMBOL: Final = {
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "BCH": "bitcoin-cash",
    "BNB": "binancecoin",
    "BTC": "bitcoin",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "ETH": "ethereum",
    "LINK": "chainlink",
    "LTC": "litecoin",
    "SHIB": "shiba-inu",
    "SOL": "solana",
    "TRX": "tron",
    "USDC": "usd-coin",
    "USDT": "tether",
    "XLM": "stellar",
    "XRP": "ripple",
}


def coingecko_id_for_holding(holding) -> str | None:
    """Return the explicit or well-known CoinGecko coin ID."""
    explicit = str(holding.get(CONF_COINGECKO_ID, "")).strip().lower()
    if explicit:
        return explicit
    ticker = str(holding.get(CONF_SYMBOL, "")).split("-", 1)[0].upper()
    return COINGECKO_IDS_BY_SYMBOL.get(ticker)


def crypto_currency_for_holding(holding, base_currency: str) -> str:
    """Return a crypto position's configured display currency."""
    configured = str(holding.get(CONF_DISPLAY_CURRENCY, "")).strip().upper()
    if len(configured) == 3 and configured.isascii() and configured.isalpha():
        return configured
    return base_currency.upper()


def crypto_data_key(coin_id: str, currency: str) -> str:
    """Return the coordinator key for one coin/currency combination."""
    return f"{coin_id}:{currency.upper()}"


def benchmark_index_for_entry(entry) -> str:
    """Return the selected benchmark, including an explicit no-benchmark choice."""
    indexes = list(entry_value(entry, CONF_INDEXES, DEFAULT_INDEXES))
    if CONF_BENCHMARK_INDEX in entry.options:
        configured = str(entry.options[CONF_BENCHMARK_INDEX]).upper()
    elif CONF_BENCHMARK_INDEX in entry.data:
        configured = str(entry.data[CONF_BENCHMARK_INDEX]).upper()
    else:
        configured = DEFAULT_BENCHMARK_INDEX
    if not configured:
        return ""
    if configured in indexes:
        return configured
    return indexes[0] if indexes else ""


def entry_value(entry, key: str, default=None):
    """Return an option, falling back to config-entry data."""
    return entry.options.get(key, entry.data.get(key, default))
