"""UI configuration for Portfolio Tracker."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from math import isfinite
from typing import Any
from uuid import uuid4

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .coingecko import CoinGeckoClient, CoinGeckoCoinNotFound, CoinGeckoError
from .const import (
    CONF_ASSET_TYPE,
    CONF_AVERAGE_PRICE,
    CONF_ALERT_ABOVE,
    CONF_ALERT_BELOW,
    CONF_BASE_CURRENCY,
    CONF_BENCHMARK_INDEX,
    CONF_COINGECKO_ID,
    CONF_DISPLAY_CURRENCY,
    CONF_HOLDING_ID,
    CONF_HOLDINGS,
    CONF_INDEX_SYMBOL,
    CONF_INDEXES,
    CONF_ISIN,
    CONF_ISSUER,
    CONF_NAME,
    CONF_PORTFOLIO_NAME,
    CONF_QUANTITY,
    CONF_PRICE_CURRENCY,
    CONF_PRICE_ENTITY,
    CONF_PRICE_SOURCE,
    CONF_RATIO,
    CONF_EXPIRY,
    CONF_STRIKE,
    CONF_SYMBOL,
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
    CONF_UPDATE_INTERVAL,
    CONF_WATCH_ONLY,
    CONF_WARRANT_TYPE,
    CONF_WKN,
    CONF_VALOR,
    CONF_UNDERLYING,
    CRYPTO_DISPLAY_CURRENCIES,
    DEFAULT_BASE_CURRENCY,
    DEFAULT_BENCHMARK_INDEX,
    DEFAULT_INDEXES,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    INDEX_PRESETS,
    MIN_UPDATE_INTERVAL,
    PRICE_SOURCES,
    STANDARD_ASSET_TYPES,
    TRANSACTION_PRICE_MODES,
    TRANSACTION_TYPES,
    WARRANT_TYPES,
    coingecko_id_for_holding,
    entry_value,
)
from .transactions import opening_transaction, transaction_balances_are_valid
from .yahoo import YahooFinanceClient, YahooFinanceError, YahooSymbolNotFound

CURRENCY_SCHEMA = str

FLOW_TEXT = {
    "de": {
        "active": "Aktiv",
        "watched": "Beobachtet",
        "no_benchmark": "Kein Vergleichsindex",
        "portfolio_name": "Mein Portfolio",
        "opening": "Anfangsbestand",
        "buy": "Kauf",
        "sell": "Verkauf",
    },
    "en": {
        "active": "Active",
        "watched": "Watched",
        "no_benchmark": "No benchmark",
        "portfolio_name": "My Portfolio",
        "opening": "Opening balance",
        "buy": "Purchase",
        "sell": "Sale",
    },
    "fr": {
        "active": "Actif",
        "watched": "Surveillé",
        "no_benchmark": "Aucun indice de référence",
        "portfolio_name": "Mon portefeuille",
        "opening": "Solde initial",
        "buy": "Achat",
        "sell": "Vente",
    },
    "it": {
        "active": "Attivo",
        "watched": "Osservato",
        "no_benchmark": "Nessun indice di riferimento",
        "portfolio_name": "Il mio portafoglio",
        "opening": "Saldo iniziale",
        "buy": "Acquisto",
        "sell": "Vendita",
    },
}


def _flow_text(hass) -> dict[str, str]:
    """Return dynamic option labels in the active Home Assistant language."""
    language = str(getattr(hass.config, "language", "en")).lower()
    language = language.replace("_", "-").split("-", 1)[0]
    return FLOW_TEXT.get(language, FLOW_TEXT["en"])


def _normalize_currency(value: str) -> str | None:
    """Normalize a three-letter ASCII currency code."""
    normalized = value.strip().upper()
    if len(normalized) != 3 or not normalized.isascii() or not normalized.isalpha():
        return None
    return normalized


def _general_schema(
    defaults: dict[str, Any], *, include_name: bool = True, default_name: str = "My Portfolio"
) -> vol.Schema:
    schema: dict[Any, Any] = {}
    if include_name:
        schema[
            vol.Required(
                CONF_PORTFOLIO_NAME,
                default=defaults.get(CONF_PORTFOLIO_NAME, default_name),
            )
        ] = str
    schema[
        vol.Required(
            CONF_BASE_CURRENCY,
            default=defaults.get(CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY),
        )
    ] = CURRENCY_SCHEMA
    schema[
        vol.Required(
            CONF_UPDATE_INTERVAL,
            default=defaults.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
        )
    ] = vol.All(
        vol.Coerce(int),
        vol.Range(min=MIN_UPDATE_INTERVAL, max=1440),
    )
    return vol.Schema(schema)


def _holding_schema(
    defaults: dict[str, Any] | None = None,
    default_currency: str = DEFAULT_BASE_CURRENCY,
    *,
    include_initial_position: bool = True,
    watch_only: bool = False,
) -> vol.Schema:
    defaults = defaults or {}
    display_currencies = list(
        dict.fromkeys([default_currency.upper(), *CRYPTO_DISPLAY_CURRENCIES])
    )
    schema: dict[Any, Any] = {
        vol.Required(CONF_SYMBOL, default=defaults.get(CONF_SYMBOL, "")): selector.TextSelector(),
        vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, "")): selector.TextSelector(),
        vol.Required(
            CONF_ASSET_TYPE, default=defaults.get(CONF_ASSET_TYPE, "stock")
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=STANDARD_ASSET_TYPES,
                translation_key="asset_type",
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(
            CONF_COINGECKO_ID,
            default=defaults.get(CONF_COINGECKO_ID, ""),
        ): str,
        vol.Required(
            CONF_DISPLAY_CURRENCY,
            default=defaults.get(CONF_DISPLAY_CURRENCY, default_currency),
        ): vol.In(display_currencies),
        vol.Optional(
            CONF_ALERT_BELOW, default=defaults.get(CONF_ALERT_BELOW, 0.0)
        ): vol.All(vol.Coerce(float), vol.Range(min=0)),
        vol.Optional(
            CONF_ALERT_ABOVE, default=defaults.get(CONF_ALERT_ABOVE, 0.0)
        ): vol.All(vol.Coerce(float), vol.Range(min=0)),
    }
    if include_initial_position:
        schema[
            vol.Required(CONF_QUANTITY, default=defaults.get(CONF_QUANTITY, 1.0))
        ] = vol.All(vol.Coerce(float), vol.Range(min=0))
        schema[
            vol.Required(
                CONF_AVERAGE_PRICE, default=defaults.get(CONF_AVERAGE_PRICE, 0.0)
            )
        ] = vol.All(vol.Coerce(float), vol.Range(min=0))
        schema[
            vol.Required(
                CONF_TRANSACTION_PRICE_MODE,
                default=defaults.get(CONF_TRANSACTION_PRICE_MODE, "per_unit"),
            )
        ] = vol.In(TRANSACTION_PRICE_MODES)
        schema[
            vol.Optional(
                CONF_TRANSACTION_MARKET_PRICE,
                default=defaults.get(CONF_TRANSACTION_MARKET_PRICE, 0.0),
            )
        ] = vol.All(vol.Coerce(float), vol.Range(min=0))
        schema[
            vol.Optional(
                CONF_TRANSACTION_MARKET_CURRENCY,
                default=defaults.get(CONF_TRANSACTION_MARKET_CURRENCY, ""),
            )
        ] = str
    return vol.Schema(schema)


def _warrant_schema(
    defaults: dict[str, Any] | None = None,
    *,
    include_initial_position: bool = True,
) -> vol.Schema:
    """Return the dedicated warrant editor."""
    defaults = defaults or {}
    price_entity_key: Any = vol.Optional(CONF_PRICE_ENTITY)
    if defaults.get(CONF_PRICE_ENTITY):
        price_entity_key = vol.Optional(
            CONF_PRICE_ENTITY, default=defaults[CONF_PRICE_ENTITY]
        )
    schema: dict[Any, Any] = {
        vol.Required(
            CONF_SYMBOL, default=defaults.get(CONF_SYMBOL, "")
        ): selector.TextSelector(),
        vol.Optional(
            CONF_NAME, default=defaults.get(CONF_NAME, "")
        ): selector.TextSelector(),
        vol.Required(
            CONF_PRICE_SOURCE,
            default=defaults.get(CONF_PRICE_SOURCE, "yahoo"),
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=PRICE_SOURCES,
                translation_key="price_source",
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        price_entity_key: selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Optional(
            CONF_PRICE_CURRENCY,
            default=defaults.get(CONF_PRICE_CURRENCY, ""),
        ): selector.TextSelector(),
        vol.Optional(
            CONF_ISIN, default=defaults.get(CONF_ISIN, "")
        ): selector.TextSelector(),
        vol.Optional(
            CONF_WKN, default=defaults.get(CONF_WKN, "")
        ): selector.TextSelector(),
        vol.Optional(
            CONF_VALOR, default=defaults.get(CONF_VALOR, "")
        ): selector.TextSelector(),
        vol.Optional(
            CONF_ISSUER, default=defaults.get(CONF_ISSUER, "")
        ): selector.TextSelector(),
        vol.Optional(
            CONF_UNDERLYING, default=defaults.get(CONF_UNDERLYING, "")
        ): selector.TextSelector(),
        vol.Required(
            CONF_WARRANT_TYPE,
            default=defaults.get(CONF_WARRANT_TYPE, "call"),
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=WARRANT_TYPES,
                translation_key="warrant_type",
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(
            CONF_STRIKE, default=defaults.get(CONF_STRIKE, 0.0)
        ): vol.All(vol.Coerce(float), vol.Range(min=0, min_included=False)),
        vol.Required(
            CONF_RATIO, default=defaults.get(CONF_RATIO, 1.0)
        ): vol.All(vol.Coerce(float), vol.Range(min=0, min_included=False)),
        vol.Required(
            CONF_EXPIRY,
            default=defaults.get(
                CONF_EXPIRY, (date.today() + timedelta(days=365)).isoformat()
            ),
        ): selector.DateSelector(),
        vol.Optional(
            CONF_ALERT_BELOW, default=defaults.get(CONF_ALERT_BELOW, 0.0)
        ): vol.All(vol.Coerce(float), vol.Range(min=0)),
        vol.Optional(
            CONF_ALERT_ABOVE, default=defaults.get(CONF_ALERT_ABOVE, 0.0)
        ): vol.All(vol.Coerce(float), vol.Range(min=0)),
        vol.Required(
            CONF_WATCH_ONLY, default=bool(defaults.get(CONF_WATCH_ONLY, False))
        ): selector.BooleanSelector(),
    }
    if include_initial_position:
        schema[
            vol.Required(CONF_QUANTITY, default=defaults.get(CONF_QUANTITY, 1.0))
        ] = vol.All(vol.Coerce(float), vol.Range(min=0))
        schema[
            vol.Required(
                CONF_AVERAGE_PRICE, default=defaults.get(CONF_AVERAGE_PRICE, 0.0)
            )
        ] = vol.All(vol.Coerce(float), vol.Range(min=0))
        schema[
            vol.Required(
                CONF_TRANSACTION_PRICE_MODE,
                default=defaults.get(CONF_TRANSACTION_PRICE_MODE, "per_unit"),
            )
        ] = vol.In(TRANSACTION_PRICE_MODES)
        schema[
            vol.Optional(
                CONF_TRANSACTION_MARKET_PRICE,
                default=defaults.get(CONF_TRANSACTION_MARKET_PRICE, 0.0),
            )
        ] = vol.All(vol.Coerce(float), vol.Range(min=0))
        schema[
            vol.Optional(
                CONF_TRANSACTION_MARKET_CURRENCY,
                default=defaults.get(CONF_TRANSACTION_MARKET_CURRENCY, ""),
            )
        ] = str
    return vol.Schema(schema)


def _transaction_schema(
    holdings: list[dict[str, Any]],
    defaults: dict[str, Any] | None = None,
    *,
    include_holding: bool = True,
    default_currency: str = DEFAULT_BASE_CURRENCY,
) -> vol.Schema:
    """Return the serializable transaction editor schema."""
    defaults = defaults or {}
    schema: dict[Any, Any] = {}
    if include_holding:
        holding_options = {
            holding[CONF_HOLDING_ID]: f"{holding[CONF_NAME]} ({holding[CONF_SYMBOL]})"
            for holding in holdings
            if not holding.get(CONF_WATCH_ONLY, False)
        }
        schema[
            vol.Required(
                CONF_HOLDING_ID,
                default=defaults.get(
                    CONF_HOLDING_ID, next(iter(holding_options), "")
                ),
            )
        ] = vol.In(holding_options)
    schema.update(
        {
            vol.Required(
                CONF_TRANSACTION_TYPE,
                default=defaults.get(CONF_TRANSACTION_TYPE, "buy"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=TRANSACTION_TYPES,
                    translation_key="transaction_type",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_TRANSACTION_DATE,
                default=defaults.get(CONF_TRANSACTION_DATE, date.today().isoformat()),
            ): selector.DateSelector(),
            vol.Required(
                CONF_QUANTITY, default=defaults.get(CONF_QUANTITY, 1.0)
            ): vol.All(vol.Coerce(float), vol.Range(min=0.00000001)),
            vol.Required(
                CONF_TRANSACTION_PRICE,
                default=defaults.get(CONF_TRANSACTION_PRICE, 0.0),
            ): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Required(
                CONF_TRANSACTION_PRICE_MODE,
                default=defaults.get(CONF_TRANSACTION_PRICE_MODE, "per_unit"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=TRANSACTION_PRICE_MODES,
                    translation_key="transaction_price_mode",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_TRANSACTION_MARKET_PRICE,
                default=defaults.get(CONF_TRANSACTION_MARKET_PRICE, 0.0),
            ): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Optional(
                CONF_TRANSACTION_MARKET_CURRENCY,
                default=defaults.get(CONF_TRANSACTION_MARKET_CURRENCY, ""),
            ): str,
            vol.Required(
                CONF_TRANSACTION_CURRENCY,
                default=defaults.get(
                    CONF_TRANSACTION_CURRENCY, default_currency.upper()
                ),
            ): str,
            vol.Required(
                CONF_TRANSACTION_FEES,
                default=defaults.get(CONF_TRANSACTION_FEES, 0.0),
            ): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Required(
                CONF_TRANSACTION_TAXES,
                default=defaults.get(CONF_TRANSACTION_TAXES, 0.0),
            ): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Optional(
                CONF_TRANSACTION_EXCHANGE,
                default=defaults.get(CONF_TRANSACTION_EXCHANGE, ""),
            ): str,
            vol.Optional(
                CONF_TRANSACTION_NOTE,
                default=defaults.get(CONF_TRANSACTION_NOTE, ""),
            ): str,
        }
    )
    return vol.Schema(schema)


class PortfolioTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create a portfolio entirely through the UI."""

    VERSION = 5

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Set up a new portfolio."""
        errors: dict[str, str] = {}
        if user_input is not None:
            currency = _normalize_currency(user_input[CONF_BASE_CURRENCY])
            if currency is None:
                errors[CONF_BASE_CURRENCY] = "invalid_currency"
            else:
                user_input[CONF_BASE_CURRENCY] = currency
                user_input[CONF_UPDATE_INTERVAL] = int(user_input[CONF_UPDATE_INTERVAL])
                user_input[CONF_HOLDINGS] = []
                user_input[CONF_INDEXES] = list(DEFAULT_INDEXES)
                user_input[CONF_BENCHMARK_INDEX] = DEFAULT_BENCHMARK_INDEX
                return self.async_create_entry(
                    title=user_input[CONF_PORTFOLIO_NAME], data=user_input
                )
        return self.async_show_form(
            step_id="user",
            data_schema=_general_schema(
                user_input or {},
                default_name=_flow_text(self.hass)["portfolio_name"],
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the portfolio editor."""
        return PortfolioOptionsFlow(config_entry)


class PortfolioOptionsFlow(config_entries.OptionsFlow):
    """Manage portfolio settings and positions."""

    def __init__(self, config_entry) -> None:
        self._entry = config_entry
        self._selected_holding_id: str | None = None
        self._selected_transaction: tuple[str, str] | None = None

    @property
    def _holdings(self) -> list[dict[str, Any]]:
        return deepcopy(entry_value(self._entry, CONF_HOLDINGS, []))

    @property
    def _indexes(self) -> list[str]:
        return list(entry_value(self._entry, CONF_INDEXES, DEFAULT_INDEXES))

    def _save(self, holdings: list[dict[str, Any]]) -> dict[str, Any]:
        options = dict(self._entry.options)
        options[CONF_HOLDINGS] = holdings
        return self.async_create_entry(data=options)

    def _save_indexes(self, indexes: list[str]) -> dict[str, Any]:
        options = dict(self._entry.options)
        options[CONF_INDEXES] = indexes
        current_benchmark = entry_value(
            self._entry, CONF_BENCHMARK_INDEX, DEFAULT_BENCHMARK_INDEX
        )
        options[CONF_BENCHMARK_INDEX] = (
            current_benchmark
            if current_benchmark in indexes
            else ""
        )
        return self.async_create_entry(data=options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Show portfolio management menu."""
        menu = ["assets"]
        if any(
            not holding.get(CONF_WATCH_ONLY, False)
            for holding in self._holdings
        ):
            menu.append("transactions")
        menu.extend(["market", "general"])
        return self.async_show_menu(step_id="init", menu_options=menu)

    async def async_step_assets(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Show actions for active and watched assets."""
        menu = ["add_holding", "add_watchlist", "add_warrant"]
        if self._holdings:
            menu.extend(["edit_holding", "remove_holding"])
        return self.async_show_menu(step_id="assets", menu_options=menu)

    async def async_step_transactions(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Show transaction ledger actions."""
        menu = ["add_transaction"]
        if any(
            holding.get(CONF_TRANSACTIONS, []) for holding in self._holdings
        ):
            menu.extend(["edit_transaction", "remove_transaction"])
        return self.async_show_menu(step_id="transactions", menu_options=menu)

    async def async_step_market(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Show market index and benchmark actions."""
        menu = []
        if any(symbol not in self._indexes for symbol in INDEX_PRESETS):
            menu.append("add_index")
        if self._indexes:
            menu.extend(["configure_benchmark", "remove_index"])
        return self.async_show_menu(step_id="market", menu_options=menu)

    async def async_step_configure_benchmark(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Select the index used for professional performance comparison."""
        if user_input is not None:
            options = dict(self._entry.options)
            options[CONF_BENCHMARK_INDEX] = user_input[CONF_BENCHMARK_INDEX]
            return self.async_create_entry(data=options)
        choices = {"": _flow_text(self.hass)["no_benchmark"]}
        choices.update(
            {
                symbol: INDEX_PRESETS.get(symbol, symbol)
                for symbol in self._indexes
            }
        )
        current = entry_value(
            self._entry, CONF_BENCHMARK_INDEX, DEFAULT_BENCHMARK_INDEX
        )
        return self.async_show_form(
            step_id="configure_benchmark",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_BENCHMARK_INDEX,
                        default=current if current in choices else "",
                    ): vol.In(choices)
                }
            ),
        )

    async def async_step_add_index(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Add one predefined market index."""
        available = {
            symbol: name
            for symbol, name in INDEX_PRESETS.items()
            if symbol not in self._indexes
        }
        if user_input is not None:
            return self._save_indexes(
                [*self._indexes, user_input[CONF_INDEX_SYMBOL]]
            )
        return self.async_show_form(
            step_id="add_index",
            data_schema=vol.Schema(
                {vol.Required(CONF_INDEX_SYMBOL): vol.In(available)}
            ),
        )

    async def async_step_remove_index(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Remove one configured market index."""
        if user_input is not None:
            selected = user_input[CONF_INDEX_SYMBOL]
            return self._save_indexes(
                [symbol for symbol in self._indexes if symbol != selected]
            )
        options = {
            symbol: INDEX_PRESETS.get(symbol, symbol) for symbol in self._indexes
        }
        return self.async_show_form(
            step_id="remove_index",
            data_schema=vol.Schema(
                {vol.Required(CONF_INDEX_SYMBOL): vol.In(options)}
            ),
        )

    async def async_step_general(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Edit portfolio-wide settings."""
        errors: dict[str, str] = {}
        if user_input is not None:
            currency = _normalize_currency(user_input[CONF_BASE_CURRENCY])
            if currency is None:
                errors[CONF_BASE_CURRENCY] = "invalid_currency"
            else:
                options = dict(self._entry.options)
                options.update(user_input)
                options[CONF_BASE_CURRENCY] = currency
                options[CONF_UPDATE_INTERVAL] = int(options[CONF_UPDATE_INTERVAL])
                return self.async_create_entry(data=options)
        defaults = {
            key: entry_value(self._entry, key)
            for key in (
                CONF_BASE_CURRENCY,
                CONF_UPDATE_INTERVAL,
            )
        }
        return self.async_show_form(
            step_id="general",
            data_schema=_general_schema(user_input or defaults, include_name=False),
            errors=errors,
        )

    async def async_step_add_holding(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Validate and add a position."""
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_WATCH_ONLY] = False
            normalized = await self._async_validate_holding(user_input, errors)
            if normalized is not None:
                normalized[CONF_HOLDING_ID] = uuid4().hex
                quote_currency = normalized.pop(
                    "_quote_currency",
                    entry_value(
                        self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                    ),
                )
                opening_currency = (
                    normalized[CONF_DISPLAY_CURRENCY]
                    if normalized[CONF_ASSET_TYPE] == "crypto"
                    else quote_currency
                )
                opening = opening_transaction(normalized, opening_currency)
                normalized.pop(CONF_TRANSACTION_PRICE_MODE, None)
                normalized.pop(CONF_TRANSACTION_MARKET_PRICE, None)
                normalized.pop(CONF_TRANSACTION_MARKET_CURRENCY, None)
                normalized[CONF_TRANSACTIONS] = [opening] if opening else []
                holdings = self._holdings
                holdings.append(normalized)
                return self._save(holdings)
        return self.async_show_form(
            step_id="add_holding",
            data_schema=_holding_schema(
                user_input,
                entry_value(
                    self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                ),
            ),
            errors=errors,
        )

    async def async_step_add_watchlist(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Validate and add an asset that does not affect portfolio totals."""
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_WATCH_ONLY] = True
            normalized = await self._async_validate_holding(user_input, errors)
            if normalized is not None:
                normalized[CONF_HOLDING_ID] = uuid4().hex
                normalized.pop("_quote_currency", None)
                normalized[CONF_TRANSACTIONS] = []
                holdings = self._holdings
                holdings.append(normalized)
                return self._save(holdings)
        return self.async_show_form(
            step_id="add_watchlist",
            data_schema=_holding_schema(
                user_input,
                entry_value(self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY),
                include_initial_position=False,
                watch_only=True,
            ),
            errors=errors,
        )

    async def async_step_add_warrant(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Validate and add an active or watched warrant."""
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_ASSET_TYPE] = "warrant"
            normalized = await self._async_validate_holding(user_input, errors)
            if normalized is not None:
                normalized[CONF_HOLDING_ID] = uuid4().hex
                quote_currency = normalized.pop(
                    "_quote_currency",
                    entry_value(
                        self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                    ),
                )
                opening = opening_transaction(normalized, quote_currency)
                normalized.pop(CONF_TRANSACTION_PRICE_MODE, None)
                normalized.pop(CONF_TRANSACTION_MARKET_PRICE, None)
                normalized.pop(CONF_TRANSACTION_MARKET_CURRENCY, None)
                normalized[CONF_TRANSACTIONS] = (
                    []
                    if normalized.get(CONF_WATCH_ONLY, False)
                    else [opening] if opening else []
                )
                holdings = self._holdings
                holdings.append(normalized)
                return self._save(holdings)
        return self.async_show_form(
            step_id="add_warrant",
            data_schema=_warrant_schema(user_input),
            errors=errors,
        )

    async def async_step_edit_holding(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Select a position to edit."""
        if user_input is not None:
            self._selected_holding_id = user_input[CONF_HOLDING_ID]
            return await self.async_step_edit_holding_details()
        return self.async_show_form(
            step_id="edit_holding", data_schema=self._holding_select_schema()
        )

    async def async_step_edit_holding_details(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Edit the selected position."""
        holdings = self._holdings
        selected = next(
            item
            for item in holdings
            if item[CONF_HOLDING_ID] == self._selected_holding_id
        )
        errors: dict[str, str] = {}
        if user_input is not None:
            normalized = await self._async_validate_holding(
                {**selected, **user_input}, errors
            )
            if normalized is not None:
                normalized[CONF_HOLDING_ID] = selected[CONF_HOLDING_ID]
                normalized.pop("_quote_currency", None)
                normalized[CONF_TRANSACTIONS] = deepcopy(
                    selected.get(CONF_TRANSACTIONS, [])
                )
                holdings[holdings.index(selected)] = normalized
                return self._save(holdings)
        schema = (
            _warrant_schema(
                user_input or selected,
                include_initial_position=False,
            )
            if selected.get(CONF_ASSET_TYPE) == "warrant"
            else _holding_schema(
                user_input or selected,
                entry_value(
                    self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                ),
                include_initial_position=False,
                watch_only=bool(selected.get(CONF_WATCH_ONLY, False)),
            )
        )
        return self.async_show_form(
            step_id="edit_holding_details",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_remove_holding(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Remove a selected position."""
        if user_input is not None:
            selected_id = user_input[CONF_HOLDING_ID]
            return self._save(
                [
                    item
                    for item in self._holdings
                    if item[CONF_HOLDING_ID] != selected_id
                ]
            )
        return self.async_show_form(
            step_id="remove_holding", data_schema=self._holding_select_schema()
        )

    async def async_step_add_transaction(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Add a buy, sell, or opening transaction."""
        errors: dict[str, str] = {}
        holdings = self._holdings
        positions = [
            holding for holding in holdings
            if not holding.get(CONF_WATCH_ONLY, False)
        ]
        if user_input is not None:
            holding = next(
                item
                for item in holdings
                if item[CONF_HOLDING_ID] == user_input[CONF_HOLDING_ID]
            )
            transaction = self._validate_transaction(user_input, errors)
            if transaction is not None:
                transaction[CONF_TRANSACTION_ID] = uuid4().hex
                candidate = deepcopy(holding)
                candidate.setdefault(CONF_TRANSACTIONS, []).append(transaction)
                if transaction_balances_are_valid(candidate):
                    holdings[holdings.index(holding)] = candidate
                    return self._save(holdings)
                errors["base"] = "insufficient_quantity"
        defaults = dict(user_input or {})
        if positions and CONF_TRANSACTION_CURRENCY not in defaults:
            default_holding = next(
                (
                    item
                    for item in positions
                    if item[CONF_HOLDING_ID] == defaults.get(CONF_HOLDING_ID)
                ),
                positions[0],
            )
            defaults[CONF_HOLDING_ID] = default_holding[CONF_HOLDING_ID]
            previous_transactions = default_holding.get(CONF_TRANSACTIONS, [])
            if previous_transactions:
                defaults[CONF_TRANSACTION_CURRENCY] = previous_transactions[-1].get(
                    CONF_TRANSACTION_CURRENCY,
                    entry_value(
                        self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                    ),
                )
        return self.async_show_form(
            step_id="add_transaction",
            data_schema=_transaction_schema(
                positions,
                defaults,
                default_currency=entry_value(
                    self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                ),
            ),
            errors=errors,
        )

    async def async_step_edit_transaction(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Select a transaction to edit."""
        if user_input is not None:
            holding_id, transaction_id = user_input[CONF_TRANSACTION_ID].split("|", 1)
            self._selected_transaction = (holding_id, transaction_id)
            return await self.async_step_edit_transaction_details()
        return self.async_show_form(
            step_id="edit_transaction",
            data_schema=self._transaction_select_schema(),
        )

    async def async_step_edit_transaction_details(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Edit one selected transaction."""
        if self._selected_transaction is None:
            return await self.async_step_init()
        holding_id, transaction_id = self._selected_transaction
        holdings = self._holdings
        holding = next(
            item for item in holdings if item[CONF_HOLDING_ID] == holding_id
        )
        transactions = deepcopy(holding.get(CONF_TRANSACTIONS, []))
        selected = next(
            item
            for item in transactions
            if item[CONF_TRANSACTION_ID] == transaction_id
        )
        errors: dict[str, str] = {}
        if user_input is not None:
            transaction = self._validate_transaction(user_input, errors)
            if transaction is not None:
                transaction[CONF_TRANSACTION_ID] = transaction_id
                transactions[transactions.index(selected)] = transaction
                candidate = deepcopy(holding)
                candidate[CONF_TRANSACTIONS] = transactions
                if transaction_balances_are_valid(candidate):
                    holdings[holdings.index(holding)] = candidate
                    return self._save(holdings)
                errors["base"] = "insufficient_quantity"
        return self.async_show_form(
            step_id="edit_transaction_details",
            data_schema=_transaction_schema(
                holdings,
                user_input or selected,
                include_holding=False,
                default_currency=entry_value(
                    self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                ),
            ),
            errors=errors,
        )

    async def async_step_remove_transaction(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Remove one selected transaction."""
        if user_input is not None:
            holding_id, transaction_id = user_input[CONF_TRANSACTION_ID].split("|", 1)
            holdings = self._holdings
            holding = next(
                item for item in holdings if item[CONF_HOLDING_ID] == holding_id
            )
            candidate = deepcopy(holding)
            candidate[CONF_TRANSACTIONS] = [
                item
                for item in candidate.get(CONF_TRANSACTIONS, [])
                if item[CONF_TRANSACTION_ID] != transaction_id
            ]
            if not transaction_balances_are_valid(candidate):
                return self.async_show_form(
                    step_id="remove_transaction",
                    data_schema=self._transaction_select_schema(),
                    errors={"base": "insufficient_quantity"},
                )
            holdings[holdings.index(holding)] = candidate
            return self._save(holdings)
        return self.async_show_form(
            step_id="remove_transaction",
            data_schema=self._transaction_select_schema(),
        )

    def _holding_select_schema(self) -> vol.Schema:
        labels = _flow_text(self.hass)
        options = {
            item[CONF_HOLDING_ID]: (
                f"{labels['watched'] if item.get(CONF_WATCH_ONLY, False) else labels['active']}"
                f" - {item[CONF_NAME]} ({item[CONF_SYMBOL]})"
            )
            for item in self._holdings
        }
        return vol.Schema({vol.Required(CONF_HOLDING_ID): vol.In(options)})

    def _transaction_select_schema(self) -> vol.Schema:
        labels = _flow_text(self.hass)
        options = {}
        for holding in self._holdings:
            for transaction in holding.get(CONF_TRANSACTIONS, []):
                key = (
                    f"{holding[CONF_HOLDING_ID]}|"
                    f"{transaction[CONF_TRANSACTION_ID]}"
                )
                options[key] = (
                    f"{transaction[CONF_TRANSACTION_DATE]} · "
                    f"{holding[CONF_NAME]} · "
                    f"{labels.get(transaction[CONF_TRANSACTION_TYPE], transaction[CONF_TRANSACTION_TYPE])}"
                )
        return vol.Schema({vol.Required(CONF_TRANSACTION_ID): vol.In(options)})

    def _validate_transaction(
        self, user_input: dict[str, Any], errors: dict[str, str]
    ) -> dict[str, Any] | None:
        try:
            transaction_date = date.fromisoformat(
                user_input[CONF_TRANSACTION_DATE].strip()
            ).isoformat()
        except ValueError:
            errors[CONF_TRANSACTION_DATE] = "invalid_transaction_date"
            return None
        currency = _normalize_currency(user_input[CONF_TRANSACTION_CURRENCY])
        if currency is None:
            errors[CONF_TRANSACTION_CURRENCY] = "invalid_currency"
            return None
        if float(user_input[CONF_TRANSACTION_PRICE]) <= 0:
            errors[CONF_TRANSACTION_PRICE] = "invalid_transaction_price"
            return None
        market_price = float(user_input.get(CONF_TRANSACTION_MARKET_PRICE, 0))
        market_currency_raw = user_input.get(
            CONF_TRANSACTION_MARKET_CURRENCY, ""
        )
        market_currency = (
            _normalize_currency(market_currency_raw) if market_currency_raw else None
        )
        if market_price > 0 and market_currency is None:
            errors[CONF_TRANSACTION_MARKET_CURRENCY] = "invalid_currency"
            return None
        return {
            CONF_TRANSACTION_TYPE: user_input[CONF_TRANSACTION_TYPE],
            CONF_TRANSACTION_DATE: transaction_date,
            CONF_QUANTITY: float(user_input[CONF_QUANTITY]),
            CONF_TRANSACTION_PRICE: float(user_input[CONF_TRANSACTION_PRICE]),
            CONF_TRANSACTION_PRICE_MODE: user_input.get(
                CONF_TRANSACTION_PRICE_MODE, "per_unit"
            ),
            CONF_TRANSACTION_MARKET_PRICE: market_price,
            CONF_TRANSACTION_MARKET_CURRENCY: market_currency or "",
            CONF_TRANSACTION_CURRENCY: currency,
            CONF_TRANSACTION_FEES: float(user_input[CONF_TRANSACTION_FEES]),
            CONF_TRANSACTION_TAXES: float(user_input[CONF_TRANSACTION_TAXES]),
            CONF_TRANSACTION_EXCHANGE: user_input[
                CONF_TRANSACTION_EXCHANGE
            ].strip(),
            CONF_TRANSACTION_NOTE: user_input[CONF_TRANSACTION_NOTE].strip(),
        }

    async def _async_validate_holding(
        self, user_input: dict[str, Any], errors: dict[str, str]
    ) -> dict[str, Any] | None:
        below = float(user_input.get(CONF_ALERT_BELOW, 0))
        above = float(user_input.get(CONF_ALERT_ABOVE, 0))
        if below > 0 and above > 0 and below >= above:
            errors["base"] = "invalid_alert_range"
            return None
        symbol = user_input[CONF_SYMBOL].strip().upper()
        if not symbol:
            errors[CONF_SYMBOL] = "symbol_required"
            return None
        price_source = str(user_input.get(CONF_PRICE_SOURCE, "yahoo"))
        price_entity = str(user_input.get(CONF_PRICE_ENTITY, "")).strip()
        price_currency_raw = str(
            user_input.get(CONF_PRICE_CURRENCY, "")
        ).strip()
        price_currency = (
            _normalize_currency(price_currency_raw) if price_currency_raw else None
        )
        if price_source == "entity":
            state = self.hass.states.get(price_entity) if price_entity else None
            if state is None:
                errors[CONF_PRICE_ENTITY] = "price_entity_not_found"
                return None
            try:
                entity_price = float(state.state)
            except (TypeError, ValueError):
                errors[CONF_PRICE_ENTITY] = "price_entity_not_numeric"
                return None
            if not isfinite(entity_price) or entity_price < 0:
                errors[CONF_PRICE_ENTITY] = "price_entity_not_numeric"
                return None
            if price_currency is None:
                errors[CONF_PRICE_CURRENCY] = "invalid_currency"
                return None
            quote_symbol = symbol
            quote_name = state.name
            quote_currency = price_currency
        else:
            try:
                client = YahooFinanceClient(async_get_clientsession(self.hass))
                quote = await client.async_get_quote(symbol)
            except YahooSymbolNotFound:
                errors[CONF_SYMBOL] = "symbol_not_found"
                return None
            except YahooFinanceError:
                errors["base"] = "cannot_connect"
                return None
            quote_symbol = quote.symbol
            quote_name = quote.name
            quote_currency = quote.currency

        expiry = str(user_input.get(CONF_EXPIRY, "")).strip()
        if user_input[CONF_ASSET_TYPE] == "warrant":
            try:
                date.fromisoformat(expiry)
            except ValueError:
                errors[CONF_EXPIRY] = "invalid_warrant_expiry"
                return None

        coingecko_id = ""
        display_currency = entry_value(
            self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
        )
        if user_input[CONF_ASSET_TYPE] == "crypto":
            display_currency = user_input[CONF_DISPLAY_CURRENCY]
            candidate = dict(user_input)
            candidate[CONF_SYMBOL] = quote_symbol
            coingecko_id = coingecko_id_for_holding(candidate) or ""
            if not coingecko_id:
                errors[CONF_COINGECKO_ID] = "coingecko_id_required"
                return None
            try:
                client = CoinGeckoClient(async_get_clientsession(self.hass))
                await client.async_get_markets(
                    [coingecko_id],
                    display_currency,
                )
            except CoinGeckoCoinNotFound:
                errors[CONF_COINGECKO_ID] = "coingecko_not_found"
                return None
            except CoinGeckoError:
                errors["base"] = "coingecko_cannot_connect"
                return None

        market_price = float(user_input.get(CONF_TRANSACTION_MARKET_PRICE, 0))
        market_currency_raw = user_input.get(
            CONF_TRANSACTION_MARKET_CURRENCY, ""
        )
        market_currency = (
            _normalize_currency(market_currency_raw) if market_currency_raw else None
        )
        if market_price > 0 and market_currency is None:
            errors[CONF_TRANSACTION_MARKET_CURRENCY] = "invalid_currency"
            return None

        return {
            CONF_SYMBOL: quote_symbol,
            CONF_NAME: user_input[CONF_NAME].strip() or quote_name,
            CONF_ASSET_TYPE: user_input[CONF_ASSET_TYPE],
            CONF_QUANTITY: float(user_input.get(CONF_QUANTITY, 0)),
            CONF_AVERAGE_PRICE: float(user_input.get(CONF_AVERAGE_PRICE, 0)),
            CONF_TRANSACTION_PRICE_MODE: user_input.get(
                CONF_TRANSACTION_PRICE_MODE, "per_unit"
            ),
            CONF_TRANSACTION_MARKET_PRICE: market_price,
            CONF_TRANSACTION_MARKET_CURRENCY: market_currency or "",
            CONF_COINGECKO_ID: coingecko_id,
            CONF_DISPLAY_CURRENCY: display_currency,
            CONF_WATCH_ONLY: bool(user_input.get(CONF_WATCH_ONLY, False)),
            CONF_ALERT_BELOW: float(user_input.get(CONF_ALERT_BELOW, 0)),
            CONF_ALERT_ABOVE: float(user_input.get(CONF_ALERT_ABOVE, 0)),
            CONF_PRICE_SOURCE: price_source,
            CONF_PRICE_ENTITY: price_entity,
            CONF_PRICE_CURRENCY: quote_currency,
            CONF_ISIN: str(user_input.get(CONF_ISIN, "")).strip().upper(),
            CONF_WKN: str(user_input.get(CONF_WKN, "")).strip().upper(),
            CONF_VALOR: str(user_input.get(CONF_VALOR, "")).strip(),
            CONF_ISSUER: str(user_input.get(CONF_ISSUER, "")).strip(),
            CONF_UNDERLYING: str(user_input.get(CONF_UNDERLYING, "")).strip(),
            CONF_WARRANT_TYPE: str(
                user_input.get(CONF_WARRANT_TYPE, "")
            ).lower(),
            CONF_STRIKE: float(user_input.get(CONF_STRIKE, 0)),
            CONF_RATIO: float(user_input.get(CONF_RATIO, 0)),
            CONF_EXPIRY: expiry,
            "_quote_currency": quote_currency,
        }
