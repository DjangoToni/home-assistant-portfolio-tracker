"""Portfolio Tracker sensor entities."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PortfolioConfigEntry
from .calculator import (
    convert_quote_amount,
    holding_average_price,
    holding_cost,
    holding_daily_percent,
    holding_fees,
    holding_gain,
    holding_gain_percent,
    holding_previous_close,
    holding_price,
    holding_quantity,
    holding_realized_gain,
    holding_taxes,
    holding_transaction_summary,
    holding_value,
    portfolio_cost,
    portfolio_daily_percent,
    portfolio_fees,
    portfolio_gain,
    portfolio_gain_percent,
    portfolio_net_invested,
    portfolio_purchases,
    portfolio_realized_gain,
    portfolio_sales,
    portfolio_taxes,
    portfolio_total_gain,
    portfolio_total_return,
    portfolio_transaction_count,
    portfolio_value,
    portfolio_holdings,
    professional_holdings,
    quote_for,
)
from .const import (
    CONF_ASSET_TYPE,
    CONF_BASE_CURRENCY,
    CONF_HOLDING_ID,
    CONF_HOLDINGS,
    CONF_INDEXES,
    CONF_ISIN,
    CONF_ISSUER,
    CONF_NAME,
    CONF_PRICE_CURRENCY,
    CONF_PRICE_ENTITY,
    CONF_PRICE_MODE,
    CONF_PRICE_SOURCE,
    CONF_RATIO,
    CONF_EXPIRY,
    CONF_STRIKE,
    CONF_PORTFOLIO_NAME,
    CONF_SYMBOL,
    CONF_TRANSACTIONS,
    CONF_TRADING_VENUE,
    CONF_WATCH_ONLY,
    CONF_WARRANT_TYPE,
    CONF_WKN,
    CONF_VALOR,
    CONF_UNDERLYING,
    DEFAULT_BASE_CURRENCY,
    DEFAULT_INDEXES,
    DOMAIN,
    INDEX_PRESETS,
    benchmark_index_for_entry,
    coingecko_id_for_holding,
    crypto_currency_for_holding,
    crypto_data_key,
    entry_value,
)
from .coordinator import PortfolioCoordinator
from .models import CryptoMarket, StockMarket
from .performance import build_performance_report
from .transactions import transaction_summary

CRYPTO_MONEY_METRICS = (
    ("high_24h", "high_24h"),
    ("low_24h", "low_24h"),
    ("volume_24h", "total_volume"),
    ("ath", "ath"),
    ("atl", "atl"),
    ("fully_diluted_valuation", "fully_diluted_valuation"),
    ("market_cap", "market_cap"),
    ("market_cap_change_24h", "market_cap_change_24h"),
    ("price_change_24h", "price_change_24h"),
)

STOCK_MONEY_METRICS = (
    ("fifty_day_average", "fifty_day_average"),
    ("fifty_two_week_high", "fifty_two_week_high"),
    ("fifty_two_week_low", "fifty_two_week_low"),
    ("two_hundred_day_average", "two_hundred_day_average"),
    ("bid", "bid"),
    ("book_value", "book_value"),
    ("day_high", "day_high"),
    ("day_low", "day_low"),
    ("dividend_rate", "dividend_rate"),
    ("earnings_per_share", "earnings_per_share"),
    ("market_cap", "market_cap"),
)
STOCK_COUNT_METRICS = (
    ("average_volume_3month", "average_volume_3month"),
    ("average_volume_10day", "average_volume_10day"),
    ("bid_size", "bid_size"),
    ("shares_outstanding", "shares_outstanding"),
    ("volume", "volume"),
)
STOCK_TEXT_METRICS = (
    ("average_analyst_rating", "average_analyst_rating"),
    ("market_state", "market_state"),
    ("symbol", "symbol"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PortfolioConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create portfolio and holding sensors."""
    coordinator = entry.runtime_data
    holdings = entry_value(entry, CONF_HOLDINGS, [])
    indexes = entry_value(entry, CONF_INDEXES, DEFAULT_INDEXES)
    entities: list[SensorEntity] = [
        PortfolioMoneySensor(coordinator, entry, "value", portfolio_value),
        PortfolioMoneySensor(coordinator, entry, "cost", portfolio_cost),
        PortfolioMoneySensor(coordinator, entry, "gain", portfolio_gain),
        PortfolioMoneySensor(
            coordinator, entry, "realized_gain", portfolio_realized_gain
        ),
        PortfolioMoneySensor(coordinator, entry, "fees", portfolio_fees),
        PortfolioMoneySensor(coordinator, entry, "taxes", portfolio_taxes),
        PortfolioMoneySensor(
            coordinator, entry, "purchases", portfolio_purchases, asset_only=True
        ),
        PortfolioMoneySensor(
            coordinator, entry, "sales", portfolio_sales, asset_only=True
        ),
        PortfolioMoneySensor(
            coordinator, entry, "net_invested", portfolio_net_invested,
            asset_only=True
        ),
        PortfolioMoneySensor(
            coordinator, entry, "total_gain", portfolio_total_gain, asset_only=True
        ),
        PortfolioPercentSensor(
            coordinator, entry, "gain_percent", portfolio_gain_percent
        ),
        PortfolioPercentSensor(
            coordinator, entry, "daily_change", portfolio_daily_percent
        ),
        PortfolioPercentSensor(
            coordinator, entry, "total_return", portfolio_total_return,
            asset_only=True
        ),
        PortfolioCountSensor(
            coordinator, entry, "transaction_count", portfolio_transaction_count,
            asset_only=True
        ),
        PortfolioPerformancePercentSensor(
            coordinator, entry, "time_weighted_return"
        ),
        PortfolioPerformancePercentSensor(
            coordinator, entry, "benchmark_return"
        ),
        PortfolioPerformancePercentSensor(coordinator, entry, "excess_return"),
        PortfolioPerformanceHistorySensor(coordinator, entry),
    ]
    for holding in holdings:
        entities.extend(
            [
                HoldingMoneySensor(
                    coordinator,
                    entry,
                    holding,
                    "price",
                    holding_price,
                    False,
                    True,
                ),
                HoldingQuantitySensor(coordinator, entry, holding),
                HoldingMoneySensor(
                    coordinator,
                    entry,
                    holding,
                    "purchase_price",
                    holding_average_price,
                    False,
                    True,
                ),
                HoldingMoneySensor(
                    coordinator, entry, holding, "cost", holding_cost, True
                ),
                HoldingMoneySensor(
                    coordinator, entry, holding, "value", holding_value, True
                ),
                HoldingMoneySensor(
                    coordinator, entry, holding, "gain", holding_gain, True
                ),
                HoldingMoneySensor(
                    coordinator,
                    entry,
                    holding,
                    "realized_gain",
                    holding_realized_gain,
                    True,
                ),
                HoldingMoneySensor(
                    coordinator, entry, holding, "fees", holding_fees, True
                ),
                HoldingMoneySensor(
                    coordinator, entry, holding, "taxes", holding_taxes, True
                ),
                HoldingTransactionsSensor(coordinator, entry, holding),
                HoldingPercentSensor(
                    coordinator,
                    entry,
                    holding,
                    "gain_percent",
                    holding_gain_percent,
                ),
                HoldingPercentSensor(
                    coordinator,
                    entry,
                    holding,
                    "daily_change",
                    holding_daily_percent,
                ),
                HoldingMoneySensor(
                    coordinator,
                    entry,
                    holding,
                    "previous_close",
                    holding_previous_close,
                    False,
                    True,
                ),
            ]
        )
        if holding[CONF_ASSET_TYPE] == "crypto":
            entities.extend(
                CryptoMoneySensor(coordinator, entry, holding, key, attribute)
                for key, attribute in CRYPTO_MONEY_METRICS
            )
            entities.extend(
                [
                    CryptoSupplySensor(
                        coordinator,
                        entry,
                        holding,
                        "circulating_supply",
                        "circulating_supply",
                    ),
                    CryptoSupplySensor(
                        coordinator,
                        entry,
                        holding,
                        "total_supply",
                        "total_supply",
                    ),
                    CryptoRankSensor(coordinator, entry, holding),
                    CryptoHistorySensor(coordinator, entry, holding),
                ]
            )
        if holding[CONF_ASSET_TYPE] == "stock":
            entities.extend(
                StockMoneySensor(coordinator, entry, holding, key, attribute)
                for key, attribute in STOCK_MONEY_METRICS
            )
            entities.extend(
                StockCountSensor(coordinator, entry, holding, key, attribute)
                for key, attribute in STOCK_COUNT_METRICS
            )
            entities.extend(
                StockTextSensor(coordinator, entry, holding, key, attribute)
                for key, attribute in STOCK_TEXT_METRICS
            )
            entities.extend(
                [
                    StockPercentSensor(
                        coordinator,
                        entry,
                        holding,
                        "dividend_yield",
                        "dividend_yield",
                    ),
                    StockNumberSensor(
                        coordinator,
                        entry,
                        holding,
                        "price_earnings_ratio",
                        "price_earnings_ratio",
                    ),
                    StockHistorySensor(coordinator, entry, holding),
                ]
            )
        if (
            holding[CONF_ASSET_TYPE] == "warrant"
            and holding.get(CONF_PRICE_SOURCE, "yahoo") in {"yahoo", "swissquote"}
        ):
            entities.append(StockHistorySensor(coordinator, entry, holding))
    for symbol in indexes:
        entities.extend(
            [
                IndexQuoteSensor(
                    coordinator, entry, symbol, "price", "holding_price"
                ),
                IndexQuoteSensor(
                    coordinator,
                    entry,
                    symbol,
                    "previous_close",
                    "holding_previous_close",
                ),
                IndexQuoteSensor(
                    coordinator,
                    entry,
                    symbol,
                    "daily_change",
                    "holding_daily_change",
                ),
                IndexMarketSensor(
                    coordinator,
                    entry,
                    symbol,
                    "fifty_day_average",
                    "stock_fifty_day_average",
                ),
                IndexMarketSensor(
                    coordinator,
                    entry,
                    symbol,
                    "two_hundred_day_average",
                    "stock_two_hundred_day_average",
                ),
                IndexMarketSensor(
                    coordinator,
                    entry,
                    symbol,
                    "fifty_two_week_high",
                    "stock_fifty_two_week_high",
                ),
                IndexMarketSensor(
                    coordinator,
                    entry,
                    symbol,
                    "fifty_two_week_low",
                    "stock_fifty_two_week_low",
                ),
                IndexMarketSensor(
                    coordinator, entry, symbol, "day_high", "stock_day_high"
                ),
                IndexMarketSensor(
                    coordinator, entry, symbol, "day_low", "stock_day_low"
                ),
                IndexMarketSensor(
                    coordinator,
                    entry,
                    symbol,
                    "market_state",
                    "stock_market_state",
                    text_value=True,
                ),
                IndexHistorySensor(coordinator, entry, symbol),
            ]
        )
    async_add_entities(entities)


class PortfolioEntity(CoordinatorEntity[PortfolioCoordinator], SensorEntity):
    """Common portfolio entity."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: PortfolioCoordinator, entry: PortfolioConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry_value(entry, CONF_PORTFOLIO_NAME, entry.title),
            manufacturer="Portfolio Tracker",
            model="Yahoo Finance Portfolio",
        )

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None


class PortfolioMoneySensor(PortfolioEntity):
    """A portfolio-level monetary sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator, entry, key, value_fn, *, asset_only=False):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = f"portfolio_{key}"
        self._metric_key = f"portfolio_{key}"
        self._value_fn = value_fn
        self._asset_only = asset_only

    @property
    def extra_state_attributes(self):
        """Expose stable identifiers for dashboard cards."""
        fx_rates = self.coordinator.data.fx_rates if self.coordinator.data else {}
        return {
            "portfolio_id": self._entry.entry_id,
            "metric_key": self._metric_key,
            "base_currency": entry_value(
                self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
            ),
            "currency_conversion": "current_rate",
            "fx_rates": {currency: float(rate) for currency, rate in fx_rates.items()},
        }

    @property
    def native_unit_of_measurement(self):
        return entry_value(self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY)

    @property
    def native_value(self):
        holdings = portfolio_holdings(entry_value(self._entry, CONF_HOLDINGS, []))
        if self._asset_only:
            holdings = professional_holdings(holdings)
        return self._value_fn(
            self.coordinator.data, holdings
        )


class PortfolioPercentSensor(PortfolioMoneySensor):
    """A portfolio-level percentage sensor."""

    _attr_device_class = None
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self):
        return "%"


class PortfolioCountSensor(PortfolioMoneySensor):
    """A portfolio-level count sensor."""

    _attr_device_class = None
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:counter"

    @property
    def native_unit_of_measurement(self):
        return None


class PortfolioPerformanceEntity(PortfolioEntity):
    """Base class for cash-flow-adjusted portfolio performance entities."""

    @property
    def report(self):
        holdings = professional_holdings(
            entry_value(self._entry, CONF_HOLDINGS, [])
        )
        return build_performance_report(
            self.coordinator.data,
            holdings,
            benchmark_index_for_entry(self._entry),
            entry_value(self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY),
        )

    @property
    def extra_state_attributes(self):
        return {
            "portfolio_id": self._entry.entry_id,
            "metric_key": self._metric_key,
            "benchmark_symbol": benchmark_index_for_entry(self._entry),
            "calculation_method": "cash_flow_adjusted_time_weighted_return",
            "fx_method": "current_rate",
        }


class PortfolioPerformancePercentSensor(PortfolioPerformanceEntity):
    """One professional percentage performance metric."""

    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator, entry, key) -> None:
        super().__init__(coordinator, entry)
        self._key = key
        self._metric_key = f"portfolio_{key}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = f"portfolio_{key}"

    @property
    def available(self) -> bool:
        return super().available and self.native_value is not None

    @property
    def native_value(self):
        return getattr(self.report, self._key)


class PortfolioPerformanceHistorySensor(PortfolioPerformanceEntity):
    """Professional portfolio and benchmark history for the dashboard."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:chart-timeline-variant-shimmer"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._metric_key = "portfolio_performance_history"
        self._attr_unique_id = f"{entry.entry_id}_performance_history"
        self._attr_translation_key = "portfolio_performance_history"

    @property
    def available(self) -> bool:
        return super().available and bool(self.report.points)

    @property
    def native_value(self):
        if not self.report.points:
            return None
        return datetime.fromisoformat(self.report.points[-1].date).replace(tzinfo=UTC)

    @property
    def extra_state_attributes(self):
        attributes = dict(super().extra_state_attributes)
        report = self.report
        attributes.update(
            {
                "period_days": len(report.points),
                "history": [
                    {
                        "date": point.date,
                        "value": float(point.value),
                        "portfolio_percent": float(point.portfolio_percent),
                        "benchmark_percent": float(point.benchmark_percent)
                        if point.benchmark_percent is not None
                        else None,
                    }
                    for point in report.points
                ],
            }
        )
        return attributes


class HoldingEntity(PortfolioEntity):
    """Common entity grouped below one asset device."""

    def __init__(self, coordinator, entry, holding):
        super().__init__(coordinator, entry)
        self._holding = holding
        holding_id = holding[CONF_HOLDING_ID]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{holding_id}")},
            name=holding[CONF_NAME],
            manufacturer="Portfolio Tracker",
            model=(
                {
                    "entity": "Home Assistant",
                    "swissquote": "Swissquote",
                }.get(holding.get(CONF_PRICE_SOURCE, "yahoo"), "Yahoo Finance")
                + f" {holding[CONF_ASSET_TYPE].title()}"
            ),
            via_device=(DOMAIN, entry.entry_id),
        )

    @property
    def extra_state_attributes(self):
        quote = quote_for(self.coordinator.data, self._holding)
        spread_percent = None
        if (
            quote is not None
            and quote.bid is not None
            and quote.ask is not None
            and quote.bid + quote.ask > 0
        ):
            midpoint = (quote.bid + quote.ask) / 2
            spread_percent = float((quote.ask - quote.bid) / midpoint * 100)
        average_price = holding_average_price(self.coordinator.data, self._holding)
        base_currency = entry_value(
            self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
        )
        return {
            "portfolio_id": self._entry.entry_id,
            "asset_id": self._holding[CONF_HOLDING_ID],
            "asset_type": self._holding[CONF_ASSET_TYPE],
            "symbol": self._holding[CONF_SYMBOL],
            "quantity": float(holding_quantity(self.coordinator.data, self._holding)),
            "average_price": float(average_price)
            if average_price is not None
            else None,
            "quote_currency": quote.currency if quote else None,
            "exchange": quote.exchange if quote else None,
            "instrument_type": quote.instrument_type if quote else None,
            "coingecko_id": coingecko_id_for_holding(self._holding),
            "display_currency": crypto_currency_for_holding(
                self._holding, base_currency
            )
            if self._holding[CONF_ASSET_TYPE] == "crypto"
            else quote.currency
            if quote
            else None,
            "metric_key": getattr(self, "_metric_key", None),
            "watch_only": bool(self._holding.get(CONF_WATCH_ONLY, False)),
            "price_source": self._holding.get(CONF_PRICE_SOURCE, "yahoo"),
            "price_entity": self._holding.get(CONF_PRICE_ENTITY) or None,
            "price_currency": self._holding.get(CONF_PRICE_CURRENCY) or None,
            "price_mode": self._holding.get(CONF_PRICE_MODE, "state"),
            "bid": float(quote.bid) if quote and quote.bid is not None else None,
            "ask": float(quote.ask) if quote and quote.ask is not None else None,
            "spread_percent": spread_percent,
            "isin": self._holding.get(CONF_ISIN) or None,
            "wkn": self._holding.get(CONF_WKN) or None,
            "valor": self._holding.get(CONF_VALOR) or None,
            "issuer": self._holding.get(CONF_ISSUER) or None,
            "underlying": self._holding.get(CONF_UNDERLYING) or None,
            "warrant_type": self._holding.get(CONF_WARRANT_TYPE) or None,
            "strike": self._holding.get(CONF_STRIKE),
            "ratio": self._holding.get(CONF_RATIO),
            "expiry": self._holding.get(CONF_EXPIRY) or None,
            "trading_venue": self._holding.get(CONF_TRADING_VENUE) or None,
        }


class HoldingMoneySensor(HoldingEntity):
    """A position-level monetary sensor."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        coordinator,
        entry,
        holding,
        key,
        value_fn,
        in_base,
        use_display_currency=False,
    ):
        super().__init__(coordinator, entry, holding)
        self._value_fn = value_fn
        self._in_base = in_base
        self._use_display_currency = use_display_currency
        self._attr_unique_id = f"{entry.entry_id}_{holding[CONF_HOLDING_ID]}_{key}"
        self._attr_translation_key = f"holding_{key}"
        self._metric_key = f"holding_{key}"

    @property
    def available(self) -> bool:
        quote = quote_for(self.coordinator.data, self._holding)
        if not super().available or quote is None:
            return False
        if self._in_base:
            return quote.currency in self.coordinator.data.fx_rates
        if (
            self._use_display_currency
            and self._holding[CONF_ASSET_TYPE] == "crypto"
        ):
            target = crypto_currency_for_holding(
                self._holding,
                entry_value(
                    self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                ),
            )
            return self.native_value is not None and target is not None
        return True

    @property
    def native_unit_of_measurement(self):
        if self._in_base:
            return entry_value(self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY)
        quote = quote_for(self.coordinator.data, self._holding)
        if (
            quote
            and self._use_display_currency
            and self._holding[CONF_ASSET_TYPE] == "crypto"
        ):
            return crypto_currency_for_holding(
                self._holding,
                entry_value(
                    self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                ),
            )
        return quote.currency if quote else None

    @property
    def native_value(self):
        value = self._value_fn(self.coordinator.data, self._holding)
        if (
            not self._in_base
            and self._use_display_currency
            and self._holding[CONF_ASSET_TYPE] == "crypto"
        ):
            return convert_quote_amount(
                self.coordinator.data,
                self._holding,
                value,
                crypto_currency_for_holding(
                    self._holding,
                    entry_value(
                        self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                    ),
                ),
            )
        return value


class HoldingQuantitySensor(HoldingEntity):
    """Configured amount owned for an asset."""

    _attr_icon = "mdi:counter"

    def __init__(self, coordinator, entry, holding):
        super().__init__(coordinator, entry, holding)
        self._attr_unique_id = f"{entry.entry_id}_{holding[CONF_HOLDING_ID]}_quantity"
        self._attr_translation_key = "holding_quantity"
        self._metric_key = "holding_quantity"
        self._attr_suggested_display_precision = (
            8 if holding[CONF_ASSET_TYPE] == "crypto" else 4
        )

    @property
    def native_unit_of_measurement(self):
        return self._holding[CONF_SYMBOL]

    @property
    def native_value(self):
        return holding_quantity(self.coordinator.data, self._holding)


class HoldingTransactionsSensor(HoldingEntity):
    """Transaction count with the complete editable ledger as attributes."""

    _attr_icon = "mdi:swap-horizontal-bold"

    def __init__(self, coordinator, entry, holding):
        super().__init__(coordinator, entry, holding)
        self._attr_unique_id = (
            f"{entry.entry_id}_{holding[CONF_HOLDING_ID]}_transactions"
        )
        self._attr_translation_key = "holding_transactions"
        self._metric_key = "holding_transactions"

    @property
    def native_value(self):
        return transaction_summary(self._holding).transaction_count

    @property
    def extra_state_attributes(self):
        attributes = dict(super().extra_state_attributes)
        summary = holding_transaction_summary(self.coordinator.data, self._holding)
        if summary is None:
            summary = transaction_summary(self._holding)
        quote = quote_for(self.coordinator.data, self._holding)
        attributes.update(
            {
                "accounting_method": "moving_average",
                "accounting_currency": quote.currency if quote else None,
                "realized_gain_quote_currency": float(summary.realized_gain),
                "fees_quote_currency": float(summary.fees),
                "taxes_quote_currency": float(summary.taxes),
                "transactions": sorted(
                    deepcopy(self._holding.get(CONF_TRANSACTIONS, [])),
                    key=lambda item: item.get("transaction_date", ""),
                    reverse=True,
                ),
            }
        )
        return attributes


class HoldingPercentSensor(HoldingMoneySensor):
    """A position-level percentage sensor."""

    _attr_device_class = None
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry, holding, key, value_fn):
        super().__init__(coordinator, entry, holding, key, value_fn, False)

    @property
    def available(self) -> bool:
        return super().available and self.native_value is not None

    @property
    def native_unit_of_measurement(self):
        return "%"


class CryptoMetricSensor(HoldingEntity):
    """Base entity for one CoinGecko market metric."""

    def __init__(self, coordinator, entry, holding, key, market_attribute):
        super().__init__(coordinator, entry, holding)
        self._market_attribute = market_attribute
        self._attr_unique_id = (
            f"{entry.entry_id}_{holding[CONF_HOLDING_ID]}_crypto_{key}"
        )
        self._attr_translation_key = f"crypto_{key}"
        self._metric_key = f"crypto_{key}"

    @property
    def market(self) -> CryptoMarket | None:
        coin_id = coingecko_id_for_holding(self._holding)
        if not coin_id or self.coordinator.data is None:
            return None
        currency = crypto_currency_for_holding(
            self._holding,
            entry_value(self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY),
        )
        return self.coordinator.data.crypto_markets.get(
            crypto_data_key(coin_id, currency)
        )

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.market is not None
            and self.native_value is not None
        )

    @property
    def native_value(self):
        return getattr(self.market, self._market_attribute) if self.market else None


class CryptoMoneySensor(CryptoMetricSensor):
    """CoinGecko monetary metric in the selected display currency."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    @property
    def native_unit_of_measurement(self):
        return self.market.currency if self.market else None


class CryptoSupplySensor(CryptoMetricSensor):
    """Current circulating or total coin supply."""

    _attr_icon = "mdi:chart-donut"
    _attr_suggested_display_precision = 2

    @property
    def native_unit_of_measurement(self):
        return self._holding[CONF_SYMBOL].split("-", 1)[0]


class CryptoRankSensor(CryptoMetricSensor):
    """CoinGecko market-cap rank."""

    _attr_icon = "mdi:podium"

    def __init__(self, coordinator, entry, holding):
        super().__init__(
            coordinator,
            entry,
            holding,
            "market_cap_rank",
            "market_cap_rank",
        )


class CryptoHistorySensor(HoldingEntity):
    """Compact 30-day CoinGecko history exposed as state attributes."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator, entry, holding):
        super().__init__(coordinator, entry, holding)
        self._attr_unique_id = (
            f"{entry.entry_id}_{holding[CONF_HOLDING_ID]}_crypto_history"
        )
        self._attr_translation_key = "crypto_history"
        self._metric_key = "crypto_history"

    @property
    def history(self):
        coin_id = coingecko_id_for_holding(self._holding)
        if not coin_id or self.coordinator.data is None:
            return ()
        currency = crypto_currency_for_holding(
            self._holding,
            entry_value(self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY),
        )
        return self.coordinator.data.crypto_history.get(
            crypto_data_key(coin_id, currency), ()
        )

    @property
    def available(self) -> bool:
        return super().available and bool(self.history)

    @property
    def native_value(self):
        return self.history[-1].timestamp if self.history else None

    @property
    def extra_state_attributes(self):
        attributes = dict(super().extra_state_attributes)
        attributes.update(
            {
                "source": "CoinGecko",
                "period_days": 30,
                "currency": crypto_currency_for_holding(
                    self._holding,
                    entry_value(
                        self._entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY
                    ),
                ),
                "history": [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "price": float(point.price)
                        if point.price is not None
                        else None,
                        "market_cap": float(point.market_cap)
                        if point.market_cap is not None
                        else None,
                        "volume": float(point.volume)
                        if point.volume is not None
                        else None,
                    }
                    for point in self.history
                ],
            }
        )
        return attributes


class StockMetricSensor(HoldingEntity):
    """Base entity for one detailed Yahoo stock metric."""

    def __init__(self, coordinator, entry, holding, key, market_attribute):
        super().__init__(coordinator, entry, holding)
        self._market_attribute = market_attribute
        self._attr_unique_id = (
            f"{entry.entry_id}_{holding[CONF_HOLDING_ID]}_stock_{key}"
        )
        self._attr_translation_key = f"stock_{key}"
        self._metric_key = f"stock_{key}"

    @property
    def market(self) -> StockMarket | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.stock_markets.get(self._holding[CONF_SYMBOL])

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.market is not None
            and self.native_value is not None
        )

    @property
    def native_value(self):
        return getattr(self.market, self._market_attribute) if self.market else None


class StockMoneySensor(StockMetricSensor):
    """Yahoo monetary stock metric in the instrument currency."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    @property
    def native_unit_of_measurement(self):
        return self.market.currency if self.market else None


class StockCountSensor(StockMetricSensor):
    """Yahoo share or market-volume count."""

    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = "shares"


class StockTextSensor(StockMetricSensor):
    """Yahoo textual stock metric."""

    _attr_device_class = None
    _attr_state_class = None
    _attr_native_unit_of_measurement = None
    _attr_suggested_display_precision = None
    _attr_icon = "mdi:information-outline"


class StockNumberSensor(StockMetricSensor):
    """Yahoo dimensionless numeric stock metric."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_icon = "mdi:calculator-variant"


class StockPercentSensor(StockMetricSensor):
    """Yahoo percentage stock metric."""

    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2


class StockHistorySensor(HoldingEntity):
    """Latest 30 daily OHLCV points exposed as attributes."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:chart-candlestick"

    def __init__(self, coordinator, entry, holding):
        super().__init__(coordinator, entry, holding)
        self._attr_unique_id = (
            f"{entry.entry_id}_{holding[CONF_HOLDING_ID]}_stock_history"
        )
        self._attr_translation_key = "stock_history"
        self._metric_key = "stock_history"

    @property
    def history(self):
        if self.coordinator.data is None:
            return ()
        return self.coordinator.data.stock_history.get(self._holding[CONF_SYMBOL], ())

    @property
    def available(self) -> bool:
        return super().available and bool(self.history)

    @property
    def native_value(self):
        return self.history[-1].timestamp if self.history else None

    @property
    def extra_state_attributes(self):
        attributes = dict(super().extra_state_attributes)
        quote = quote_for(self.coordinator.data, self._holding)
        attributes.update(
            {
                "source": (
                    "Swissquote"
                    if self._holding.get(CONF_PRICE_SOURCE) == "swissquote"
                    else "Yahoo Finance"
                ),
                "period_trading_days": len(self.history),
                "currency": quote.currency if quote else None,
                "history": [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "open": float(point.open) if point.open is not None else None,
                        "high": float(point.high) if point.high is not None else None,
                        "low": float(point.low) if point.low is not None else None,
                        "close": float(point.close),
                        "volume": point.volume,
                    }
                    for point in self.history
                ],
            }
        )
        return attributes


class IndexEntity(PortfolioEntity):
    """Common entity grouped below one configured market-index device."""

    def __init__(self, coordinator, entry, symbol: str) -> None:
        super().__init__(coordinator, entry)
        self._symbol = symbol
        self._asset_id = f"index_{symbol.replace('^', '').lower()}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{self._asset_id}")},
            name=INDEX_PRESETS.get(symbol, symbol),
            manufacturer="Portfolio Tracker",
            model="Yahoo Finance Market Index",
            via_device=(DOMAIN, entry.entry_id),
        )

    @property
    def quote(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.quotes.get(self._symbol)

    @property
    def market(self) -> StockMarket | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.stock_markets.get(self._symbol)

    @property
    def extra_state_attributes(self):
        return {
            "portfolio_id": self._entry.entry_id,
            "asset_id": self._asset_id,
            "asset_type": "index",
            "symbol": self._symbol,
            "quote_currency": self.quote.currency if self.quote else None,
            "exchange": self.quote.exchange if self.quote else None,
            "instrument_type": self.quote.instrument_type if self.quote else "INDEX",
            "metric_key": getattr(self, "_metric_key", None),
        }


class IndexQuoteSensor(IndexEntity):
    """Current or previous value of one market index."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_icon = "mdi:chart-timeline-variant"

    def __init__(self, coordinator, entry, symbol, key, metric_key) -> None:
        super().__init__(coordinator, entry, symbol)
        self._key = key
        self._metric_key = metric_key
        self._attr_unique_id = f"{entry.entry_id}_{self._asset_id}_{key}"
        self._attr_translation_key = f"index_{key}"

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.quote is not None
            and self.native_value is not None
        )

    @property
    def native_unit_of_measurement(self):
        return "%" if self._key == "daily_change" else "points"

    @property
    def native_value(self):
        if not self.quote:
            return None
        if self._key == "daily_change":
            return self.quote.daily_change_percent
        return getattr(self.quote, self._key)


class IndexMarketSensor(IndexEntity):
    """Detailed Yahoo metric for one market index."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_icon = "mdi:chart-line"

    def __init__(
        self, coordinator, entry, symbol, market_attribute, metric_key, text_value=False
    ) -> None:
        super().__init__(coordinator, entry, symbol)
        self._market_attribute = market_attribute
        self._metric_key = metric_key
        self._text_value = text_value
        self._attr_unique_id = (
            f"{entry.entry_id}_{self._asset_id}_{market_attribute}"
        )
        self._attr_translation_key = f"index_{market_attribute}"
        if text_value:
            self._attr_device_class = None
            self._attr_state_class = None
            self._attr_native_unit_of_measurement = None
            self._attr_suggested_display_precision = None
            self._attr_icon = "mdi:clock-outline"

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.market is not None
            and self.native_value is not None
        )

    @property
    def native_unit_of_measurement(self):
        return None if self._text_value else "points"

    @property
    def native_value(self):
        return getattr(self.market, self._market_attribute) if self.market else None


class IndexHistorySensor(IndexEntity):
    """Latest 30 daily Yahoo index points exposed as attributes."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:chart-areaspline"

    def __init__(self, coordinator, entry, symbol) -> None:
        super().__init__(coordinator, entry, symbol)
        self._attr_unique_id = f"{entry.entry_id}_{self._asset_id}_history"
        self._attr_translation_key = "index_history"
        self._metric_key = "stock_history"

    @property
    def history(self):
        if self.coordinator.data is None:
            return ()
        return self.coordinator.data.stock_history.get(self._symbol, ())

    @property
    def available(self) -> bool:
        return super().available and bool(self.history)

    @property
    def native_value(self):
        return self.history[-1].timestamp if self.history else None

    @property
    def extra_state_attributes(self):
        attributes = dict(super().extra_state_attributes)
        attributes.update(
            {
                "source": "Yahoo Finance",
                "period_trading_days": len(self.history),
                "unit": "points",
                "history": [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "open": float(point.open) if point.open is not None else None,
                        "high": float(point.high) if point.high is not None else None,
                        "low": float(point.low) if point.low is not None else None,
                        "close": float(point.close),
                        "volume": point.volume,
                    }
                    for point in self.history
                ],
            }
        )
        return attributes
