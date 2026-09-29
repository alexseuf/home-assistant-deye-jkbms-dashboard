"""PV & Battery Dashboard integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_AUTO_UPDATE, DOMAIN, VERSION
from .dashboard_manager import async_install_or_update_dashboard

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.SELECT, Platform.SENSOR]
STATIC_URL = "/pv-battery-dashboard-static"
HISTORY_RANGE_RESOURCE_PATH = f"{STATIC_URL}/pv-history-range-card.js"
HISTORY_RANGE_RESOURCE_URL = f"{HISTORY_RANGE_RESOURCE_PATH}?v={VERSION}"


async def _async_ensure_history_range_resource(hass: HomeAssistant) -> None:
    """Register the bundled custom history-range card in Lovelace storage mode."""
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        return

    resource_collection = lovelace_data.resources
    if not isinstance(resource_collection, ResourceStorageCollection):
        _LOGGER.warning(
            "Cannot auto-register PV history range card because Lovelace resources "
            "are not in storage mode"
        )
        return

    await resource_collection.async_get_info()
    for item in resource_collection.async_items():
        url = item.get("url", "")
        if url.split("?", 1)[0] != HISTORY_RANGE_RESOURCE_PATH:
            continue
        if url != HISTORY_RANGE_RESOURCE_URL:
            await resource_collection.async_update_item(
                item["id"],
                {"url": HISTORY_RANGE_RESOURCE_URL, "res_type": "module"},
            )
        return

    await resource_collection.async_create_item(
        {"url": HISTORY_RANGE_RESOURCE_URL, "res_type": "module"}
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PV & Battery Dashboard from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get("static_registered"):
        static_dir = Path(__file__).parent / "static"
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(static_dir), cache_headers=False)]
        )
        domain_data["static_registered"] = True

    # Set up entities first. The managed dashboard can then resolve helper
    # entity IDs from the entity registry instead of assuming a fixed object ID.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await _async_ensure_history_range_resource(hass)

    if entry.data.get(CONF_AUTO_UPDATE, True):
        try:
            result = await async_install_or_update_dashboard(hass)
            _LOGGER.info("Managed dashboard %s", result)
        except Exception:
            _LOGGER.exception("Could not install/update the managed dashboard")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    The managed Lovelace dashboard is intentionally kept when the integration
    is unloaded or removed so user history/configuration is not deleted
    unexpectedly.
    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
