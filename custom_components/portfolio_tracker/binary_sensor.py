"""Price-alert binary sensors for Portfolio Tracker."""

from __future__ import annotations

from decimal import Decimal

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_ALERT_ABOVE,
    CONF_ALERT_BELOW,
    CONF_HOLDING_ID,
    CONF_HOLDINGS,
    CONF_NAME,
    CONF_SYMBOL,
    DOMAIN,
    entry_value,
)
from .coordinator import PortfolioCoordinator
from .calculator import holding_alert_price
from .const import CONF_ASSET_TYPE, crypto_currency_for_holding


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one binary sensor for every configured threshold."""
    coordinator: PortfolioCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for holding in entry_value(entry, CONF_HOLDINGS, []):
        if float(holding.get(CONF_ALERT_BELOW, 0)) > 0:
            entities.append(PriceAlertSensor(coordinator, entry, holding, "below"))
        if float(holding.get(CONF_ALERT_ABOVE, 0)) > 0:
            entities.append(PriceAlertSensor(coordinator, entry, holding, "above"))
    async_add_entities(entities)


class PriceAlertSensor(CoordinatorEntity[PortfolioCoordinator], BinarySensorEntity):
    """Turn on while an asset is outside its configured price boundary."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:bell-alert-outline"

    def __init__(self, coordinator, entry, holding, direction: str) -> None:
        super().__init__(coordinator)
        self._holding = holding
        self._entry_id = entry.entry_id
        self._direction = direction
        self._threshold_key = (
            CONF_ALERT_BELOW if direction == "below" else CONF_ALERT_ABOVE
        )
        self._attr_unique_id = (
            f"{entry.entry_id}_{holding[CONF_HOLDING_ID]}_alert_{direction}"
        )
        self._attr_translation_key = f"price_alert_{direction}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{holding[CONF_HOLDING_ID]}")},
            name=holding[CONF_NAME],
            manufacturer="Portfolio Tracker",
            model="Yahoo Finance Asset",
            via_device=(DOMAIN, entry.entry_id),
        )

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        price = holding_alert_price(self.coordinator.data, self._holding)
        if price is None:
            return None
        threshold = Decimal(str(self._holding[self._threshold_key]))
        return price <= threshold if self._direction == "below" else price >= threshold

    @property
    def extra_state_attributes(self) -> dict:
        if self.coordinator.data is None:
            return {
                "portfolio_id": self._entry_id,
                "asset_id": self._holding[CONF_HOLDING_ID],
                "symbol": self._holding[CONF_SYMBOL],
                "direction": self._direction,
                "threshold": float(self._holding[self._threshold_key]),
                "metric_key": f"price_alert_{self._direction}",
            }
        quote = self.coordinator.data.quotes.get(self._holding[CONF_SYMBOL])
        price = holding_alert_price(self.coordinator.data, self._holding)
        currency = (
            crypto_currency_for_holding(self._holding, self.coordinator.data.base_currency)
            if self._holding.get(CONF_ASSET_TYPE) == "crypto"
            else quote.currency if quote else None
        )
        return {
            "portfolio_id": self._entry_id,
            "asset_id": self._holding[CONF_HOLDING_ID],
            "symbol": self._holding[CONF_SYMBOL],
            "direction": self._direction,
            "threshold": float(self._holding[self._threshold_key]),
            "current_price": float(price) if price is not None else None,
            "currency": currency,
            "metric_key": f"price_alert_{self._direction}",
        }
