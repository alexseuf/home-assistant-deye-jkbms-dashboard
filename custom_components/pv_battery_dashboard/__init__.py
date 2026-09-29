"""PV & Battery Dashboard integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
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
    frontend.add_extra_js_url(hass, HISTORY_RANGE_RESOURCE_URL)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

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
    frontend.remove_extra_js_url(hass, HISTORY_RANGE_RESOURCE_URL)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
