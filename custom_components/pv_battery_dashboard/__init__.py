"""PV & Battery Dashboard integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_AUTO_UPDATE
from .dashboard_manager import async_install_or_update_dashboard

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PV & Battery Dashboard from a config entry."""
    if entry.data.get(CONF_AUTO_UPDATE, True):
        try:
            result = await async_install_or_update_dashboard(hass)
            _LOGGER.info("Managed dashboard %s", result)
        except Exception:
            _LOGGER.exception("Could not install/update the managed dashboard")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    The managed Lovelace dashboard is intentionally kept when the integration
    is unloaded or removed so user history/configuration is not deleted
    unexpectedly.
    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
