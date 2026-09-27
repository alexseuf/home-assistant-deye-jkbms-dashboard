"""Sensor platform for PV & Battery Dashboard."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, UnitOfElectricPotential
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, State, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, NAME, VERSION

SOURCE_BATTERY_VOLTAGE = "sensor.jk_bms_total_jk_bms_total_voltage"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up dashboard helper sensors."""
    async_add_entities([RoundedBatteryVoltageSensor(entry)])


class RoundedBatteryVoltageSensor(SensorEntity):
    """Mirror the JK-BMS battery voltage with one decimal place."""

    _attr_has_entity_name = False
    _attr_name = "Batteriespannung 1 Dezimal"
    _attr_icon = "mdi:flash"
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_suggested_display_precision = 1
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the helper sensor."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_battery_voltage_1_decimal"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="alexseuf",
            model="Managed Lovelace Dashboard",
            sw_version=VERSION,
        )

    async def async_added_to_hass(self) -> None:
        """Start tracking the source battery voltage."""
        self._update_from_state(self.hass.states.get(SOURCE_BATTERY_VOLTAGE))
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [SOURCE_BATTERY_VOLTAGE],
                self._handle_source_change,
            )
        )

    @callback
    def _handle_source_change(self, event: Event[EventStateChangedData]) -> None:
        """Handle source sensor changes."""
        self._update_from_state(event.data["new_state"])
        self.async_write_ha_state()

    @callback
    def _update_from_state(self, state: State | None) -> None:
        """Copy and round the source voltage."""
        if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            self._attr_native_value = None
            self._attr_available = False
            return

        try:
            self._attr_native_value = round(float(state.state), 1)
            self._attr_available = True
        except (TypeError, ValueError):
            self._attr_native_value = None
            self._attr_available = False
