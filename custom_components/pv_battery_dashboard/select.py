"""Select platform for PV & Battery Dashboard."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, NAME, VERSION

PACK_OPTIONS = ["Pack 1", "Pack 2", "Pack 3"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the dashboard pack selector."""
    async_add_entities([JKBMSPackSelect(entry)])


class JKBMSPackSelect(SelectEntity, RestoreEntity):
    """Choose which JK-BMS pack is displayed in the cell detail section."""

    _attr_has_entity_name = False
    _attr_name = "JK BMS Pack Auswahl"
    _attr_icon = "mdi:battery-sync"
    _attr_options = PACK_OPTIONS
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the selector."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_jk_bms_pack_selection"
        self._attr_current_option = PACK_OPTIONS[0]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="alexseuf",
            model="Managed Lovelace Dashboard",
            sw_version=VERSION,
        )

    async def async_added_to_hass(self) -> None:
        """Restore the last selected pack after a restart."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state is not None and state.state in PACK_OPTIONS:
            self._attr_current_option = state.state

    async def async_select_option(self, option: str) -> None:
        """Select a JK-BMS pack."""
        if option not in PACK_OPTIONS:
            raise ValueError(f"Unsupported JK-BMS pack option: {option}")
        self._attr_current_option = option
        self.async_write_ha_state()
