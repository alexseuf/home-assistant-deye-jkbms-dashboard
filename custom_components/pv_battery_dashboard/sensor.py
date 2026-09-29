"""Sensor platform for PV & Battery Dashboard."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, State, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, NAME, VERSION

SOURCE_BATTERY_VOLTAGE = "sensor.jk_bms_total_jk_bms_total_voltage"
SOURCE_HOUSEHOLD_LOAD = "sensor.solis_s5_eh1p_household_load_power"
SOURCE_INVERTER_POWER = "sensor.solis_s5_eh1p_active_power"
SOURCE_GRID_POWER = "sensor.solis_s5_eh1p_ac_grid_port_power"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up dashboard helper sensors."""
    entities: list[SensorEntity] = [
        RoundedBatteryVoltageSensor(entry),
        CalculatedHouseholdLoadSensor(entry),
    ]
    for pack in range(3):
        entities.extend(
            [
                PackCellDeltaSensor(entry, pack),
                PackMaximumCellTemperatureSensor(entry, pack),
            ]
        )
    async_add_entities(entities)


class CalculatedHouseholdLoadSensor(SensorEntity):
    """Expose household load with a power-balance fallback.

    Some Solis S5-EH1P meter/CT configurations intermittently report zero for
    the native household-load register even while inverter and grid power are
    changing. Prefer a positive native reading, but fall back to the absolute
    difference between inverter and grid-port power when the native register
    is zero.
    """

    _attr_has_entity_name = False
    _attr_name = "Berechneter Hausverbrauch"
    _attr_icon = "mdi:home-lightning-bolt"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_suggested_display_precision = 0
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the calculated household-load sensor."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_calculated_household_load_power"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="alexseuf",
            model="Managed Lovelace Dashboard",
            sw_version=VERSION,
        )

    async def async_added_to_hass(self) -> None:
        """Start tracking the three power sources."""
        self._update_value()
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [SOURCE_HOUSEHOLD_LOAD, SOURCE_INVERTER_POWER, SOURCE_GRID_POWER],
                self._handle_source_change,
            )
        )

    @callback
    def _handle_source_change(self, _event: Event[EventStateChangedData]) -> None:
        """Recalculate after a source value changes."""
        self._update_value()
        self.async_write_ha_state()

    @callback
    def _update_value(self) -> None:
        """Use the native load when valid, otherwise calculate the balance."""
        values: dict[str, float] = {}
        for entity_id in (
            SOURCE_HOUSEHOLD_LOAD,
            SOURCE_INVERTER_POWER,
            SOURCE_GRID_POWER,
        ):
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                continue
            try:
                values[entity_id] = float(state.state)
            except (TypeError, ValueError):
                continue

        native_load = values.get(SOURCE_HOUSEHOLD_LOAD)
        if native_load is not None and native_load > 0:
            self._attr_native_value = round(native_load)
            self._attr_available = True
            return

        inverter_power = values.get(SOURCE_INVERTER_POWER)
        grid_power = values.get(SOURCE_GRID_POWER)
        if inverter_power is not None and grid_power is not None:
            self._attr_native_value = round(abs(inverter_power - grid_power))
            self._attr_available = True
            return

        if native_load is not None:
            self._attr_native_value = round(max(native_load, 0))
            self._attr_available = True
            return

        self._attr_native_value = None
        self._attr_available = False


class PackAggregateSensor(SensorEntity):
    """Base class for a value calculated from multiple JK-BMS sensors."""

    _attr_has_entity_name = False
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, pack: int, suffix: str) -> None:
        """Initialize a pack aggregate sensor."""
        self._entry = entry
        self._pack = pack
        self._attr_unique_id = f"{entry.entry_id}_pack_{pack + 1}_{suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="alexseuf",
            model="Managed Lovelace Dashboard",
            sw_version=VERSION,
        )

    @property
    def source_entities(self) -> list[str]:
        """Return the source entities used for this aggregate."""
        raise NotImplementedError

    def calculate(self, values: list[float]) -> float:
        """Calculate the aggregate value."""
        raise NotImplementedError

    async def async_added_to_hass(self) -> None:
        """Start tracking all source sensors."""
        self._update_value()
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                self.source_entities,
                self._handle_source_change,
            )
        )

    @callback
    def _handle_source_change(self, _event: Event[EventStateChangedData]) -> None:
        """Recalculate after any source value changes."""
        self._update_value()
        self.async_write_ha_state()

    @callback
    def _update_value(self) -> None:
        """Read all sources and update the native value."""
        values: list[float] = []
        for entity_id in self.source_entities:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                self._attr_native_value = None
                self._attr_available = False
                return
            try:
                values.append(float(state.state))
            except (TypeError, ValueError):
                self._attr_native_value = None
                self._attr_available = False
                return
        self._attr_native_value = self.calculate(values)
        self._attr_available = True


class PackCellDeltaSensor(PackAggregateSensor):
    """Expose the difference between the highest and lowest pack cell."""

    _attr_icon = "mdi:delta"
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
    _attr_suggested_display_precision = 0

    def __init__(self, entry: ConfigEntry, pack: int) -> None:
        """Initialize the cell-delta sensor."""
        super().__init__(entry, pack, "cell_delta")
        self._attr_name = f"Pack {pack + 1} Zell-Delta"

    @property
    def source_entities(self) -> list[str]:
        """Return all 16 cell-voltage entities."""
        return [
            f"sensor.jk_bms_pack_{self._pack:02d}_cell_{cell:02d}_voltage"
            for cell in range(1, 17)
        ]

    def calculate(self, values: list[float]) -> float:
        """Calculate cell delta in millivolts."""
        return round(max(values) - min(values), 0)


class PackMaximumCellTemperatureSensor(PackAggregateSensor):
    """Expose the highest of the four requested cell temperatures."""

    _attr_icon = "mdi:thermometer-high"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 1

    def __init__(self, entry: ConfigEntry, pack: int) -> None:
        """Initialize the maximum-temperature sensor."""
        super().__init__(entry, pack, "maximum_cell_temperature")
        self._attr_name = f"Pack {pack + 1} Max. Zelltemperatur"

    @property
    def source_entities(self) -> list[str]:
        """Return the four cell-temperature entities requested for the chart."""
        return [
            f"sensor.jk_bms_pack_{self._pack:02d}_temperature_{sensor:02d}"
            for sensor in range(1, 5)
        ]

    def calculate(self, values: list[float]) -> float:
        """Calculate the maximum cell temperature."""
        return round(max(values), 1)


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
