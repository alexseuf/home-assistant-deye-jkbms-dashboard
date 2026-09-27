"""Button platform for PV & Battery Dashboard."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, NAME, VERSION
from .dashboard_manager import async_install_or_update_dashboard


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up dashboard maintenance buttons."""
    async_add_entities([DashboardUpdateButton(entry)])


class DashboardUpdateButton(ButtonEntity):
    """Button that installs or refreshes the managed dashboard."""

    _attr_has_entity_name = True
    _attr_name = "Dashboard aktualisieren"
    _attr_icon = "mdi:update"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the update button."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_update_dashboard"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="alexseuf",
            model="Managed Lovelace Dashboard",
            sw_version=VERSION,
        )

    async def async_press(self) -> None:
        """Install or update the dashboard."""
        await async_install_or_update_dashboard(self.hass)
