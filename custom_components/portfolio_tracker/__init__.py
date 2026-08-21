"""Portfolio Tracker integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import LOVELACE_DATA, MODE_STORAGE
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    CONF_BASE_CURRENCY,
    CONF_HOLDINGS,
    CONF_INDEXES,
    CONF_PRICE_ENTITY,
    CONF_PRICE_SOURCE,
    DEFAULT_BASE_CURRENCY,
    DEFAULT_INDEXES,
    DOMAIN,
    FRONTEND_VERSION,
    FRONTEND_URL,
    PLATFORMS,
    entry_value,
)
from .coordinator import PortfolioCoordinator
from .registry import active_device_identifiers
from .transactions import migrate_opening_transactions

FRONTEND_PATH = Path(__file__).parent / "frontend"
FRONTEND_CARD_PATH = f"{FRONTEND_URL}/portfolio-asset-card.js"
FRONTEND_LOADER_PATH = f"{FRONTEND_URL}/portfolio-asset-card-loader.js"
FRONTEND_MODULE = f"{FRONTEND_LOADER_PATH}?v={FRONTEND_VERSION}"
FRONTEND_RESOURCE_PATHS = {FRONTEND_CARD_PATH, FRONTEND_LOADER_PATH}
DATA_FRONTEND_REGISTERED = f"{DOMAIN}_frontend_registered"

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the automatically loaded Portfolio Tracker dashboard card."""
    await _async_register_frontend(hass)
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Expose the card and ensure Lovelace loads it as a module."""
    if hass.data.get(DATA_FRONTEND_REGISTERED):
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(FRONTEND_PATH), False)]
    )
    frontend.add_extra_js_url(hass, FRONTEND_MODULE)

    async def async_refresh_resource_after_start(_event) -> None:
        """Republish the module when browsers are connected after startup."""
        try:
            frontend.remove_extra_js_url(hass, FRONTEND_MODULE)
            frontend.add_extra_js_url(hass, FRONTEND_MODULE)
            await _async_ensure_lovelace_resource(hass)
        except Exception:
            _LOGGER.exception(
                "Could not republish the Portfolio Asset Card after startup"
            )

    if hass.state is CoreState.running:
        await async_refresh_resource_after_start(None)
    else:
        hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STARTED,
            async_refresh_resource_after_start,
        )

    try:
        resource_registered = await _async_ensure_lovelace_resource(hass)
    # Resource persistence is a fallback. A failure must not take down the
    # integration because the extra frontend module above can still load it.
    except Exception:
        resource_registered = False
        _LOGGER.exception("Could not register the Portfolio Asset Card resource")

    hass.data[DATA_FRONTEND_REGISTERED] = True
    _LOGGER.info(
        "Portfolio Asset Card registered at %s (Lovelace resource: %s)",
        FRONTEND_MODULE,
        resource_registered,
    )


async def _async_ensure_lovelace_resource(hass: HomeAssistant) -> bool:
    """Create or update the card resource when Lovelace uses storage mode."""
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None or lovelace_data.resource_mode != MODE_STORAGE:
        return False

    resources = lovelace_data.resources
    await resources.async_get_info()

    matching_resources = [
        item
        for item in resources.async_items() or []
        if str(item.get("url", "")).split("?", 1)[0] in FRONTEND_RESOURCE_PATHS
    ]
    if matching_resources:
        primary, *duplicates = matching_resources
        if primary.get("url") != FRONTEND_MODULE or primary.get("type") != "module":
            await resources.async_update_item(
                primary["id"],
                {"url": FRONTEND_MODULE, "res_type": "module"},
            )
        for duplicate in duplicates:
            await resources.async_delete_item(duplicate["id"])
        return True

    await resources.async_create_item(
        {"url": FRONTEND_MODULE, "res_type": "module"}
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a portfolio config entry."""
    await _async_register_frontend(hass)
    # Also clean positions removed before this version was installed.
    _async_remove_stale_devices(hass, entry)
    coordinator = PortfolioCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    external_price_entities = {
        str(holding.get(CONF_PRICE_ENTITY, "")).strip()
        for holding in entry_value(entry, CONF_HOLDINGS, [])
        if holding.get(CONF_PRICE_SOURCE, "yahoo") == "entity"
        and holding.get(CONF_PRICE_ENTITY)
    }
    if external_price_entities:

        @callback
        def _external_price_changed(_event) -> None:
            """Refresh promptly when a configured external price changes."""
            hass.async_create_task(coordinator.async_request_refresh())

        entry.async_on_unload(
            async_track_state_change_event(
                hass,
                external_price_entities,
                _external_price_changed,
            )
        )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate legacy quantities into editable opening transactions."""
    if entry.version > 5:
        return False
    options = dict(entry.options)
    if entry.version < 2:
        holdings, _changed = migrate_opening_transactions(
            entry_value(entry, CONF_HOLDINGS, []),
            entry_value(entry, CONF_BASE_CURRENCY, DEFAULT_BASE_CURRENCY),
        )
        options[CONF_HOLDINGS] = holdings
        _LOGGER.info("Migrated portfolio %s to transaction ledger", entry.entry_id)
    if entry.version < 5:
        hass.config_entries.async_update_entry(entry, options=options, version=5)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a portfolio config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload after UI options change."""
    _async_remove_stale_devices(hass, entry)
    await hass.config_entries.async_reload(entry.entry_id)


def _async_remove_stale_devices(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove registry devices and entities no longer present in the options."""
    keep_identifiers = active_device_identifiers(
        entry.entry_id,
        entry_value(entry, CONF_HOLDINGS, []),
        entry_value(entry, CONF_INDEXES, DEFAULT_INDEXES),
    )
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    removed_devices = 0
    removed_entities = 0
    for device in list(
        dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    ):
        portfolio_identifiers = {
            identifier
            for domain, identifier in device.identifiers
            if domain == DOMAIN
        }
        if not portfolio_identifiers or portfolio_identifiers & keep_identifiers:
            continue
        for entity in er.async_entries_for_device(
            entity_registry,
            device.id,
            include_disabled_entities=True,
        ):
            entity_registry.async_remove(entity.entity_id)
            removed_entities += 1
        device_registry.async_remove_device(device.id)
        removed_devices += 1
    if removed_devices:
        _LOGGER.info(
            "Removed %s stale Portfolio Tracker device(s) and %s entities",
            removed_devices,
            removed_entities,
        )
