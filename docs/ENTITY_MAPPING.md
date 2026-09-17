# Entity mapping

This document records entities verified from the upstream integrations. Do not replace these with guessed IDs.

## Deye — SolarModbus V2

Source: `comdif/ha-solarmodbus`, branch `V2`, including its supplied demo dashboard.

### Verified live entities

| Function | Entity |
|---|---|
| Inverter status | `sensor.solarmodbus_device_running_status` |
| Grid connected | `sensor.solarmodbus_device_grid_connected_status` |
| Load voltage | `sensor.solarmodbus_device_load_voltage` |
| L1 current | `sensor.solarmodbus_device_current_l1` |
| L2 current | `sensor.solarmodbus_device_current_l2` |
| Total inverter power | `sensor.solarmodbus_device_total_power` |
| Inverter L1 power | `sensor.solarmodbus_device_inverter_l1_power` |
| Inverter L2 power | `sensor.solarmodbus_device_inverter_l2_power` |
| Load frequency | `sensor.solarmodbus_device_load_frequency` |
| Load L1 power | `sensor.solarmodbus_device_load_l1_power` |
| Total grid power | `sensor.solarmodbus_device_total_grid_power` |
| External CT L1 | `sensor.solarmodbus_device_external_ct_l1_power` |
| External CT L2 | `sensor.solarmodbus_device_external_ct_l2_power` |
| PV1 power | `sensor.solarmodbus_device_pv1_power` |
| PV2 power | `sensor.solarmodbus_device_pv2_power` |
| PV1 voltage | `sensor.solarmodbus_device_pv1_voltage` |
| PV1 current | `sensor.solarmodbus_device_pv1_current` |
| PV2 voltage | `sensor.solarmodbus_device_pv2_voltage` |
| PV2 current | `sensor.solarmodbus_device_pv2_current` |
| Micro inverter / AUX power | `sensor.solarmodbus_device_micro_inverter_power` |
| Battery voltage | `sensor.solarmodbus_device_battery_voltage` |
| Battery SOC | `sensor.solarmodbus_device_battery_soc` |
| Battery power | `sensor.solarmodbus_device_battery_power` |
| Battery current | `sensor.solarmodbus_device_battery_current` |
| Alert | `sensor.solarmodbus_device_alert` |

### Verified energy entities

| Function | Entity |
|---|---|
| Daily PV production | `sensor.solarmodbus_device_daily_production` |
| Daily load consumption | `sensor.solarmodbus_device_daily_load_consumption` |
| Daily grid import | `sensor.solarmodbus_device_daily_energy_bought` |
| Daily grid export | `sensor.solarmodbus_device_daily_energy_sold` |
| Daily battery charge | `sensor.solarmodbus_device_daily_battery_charge` |
| Daily battery discharge | `sensor.solarmodbus_device_daily_battery_discharge` |

### Verified configuration/status entities

| Function | Entity |
|---|---|
| System work mode | `sensor.solarmodbus_device_system_work_mode` |
| Solar Sell state | `sensor.solarmodbus_device_solar_sell` |
| Grid charge state | `sensor.solarmodbus_device_grid_charge` |
| Smart Load enable status | `sensor.solarmodbus_device_smartload_enable_status` |

SolarModbus V2 exposes the `solarmodbus.write_register` action. The upstream documentation demonstrates Solar Sell on register 247 and the upstream demo dashboard demonstrates System Work Mode on register 244. Register writes are model-sensitive and must not be enabled blindly for an unverified Deye model.

For the production dashboard, potentially destructive writes will be isolated in the Deye settings view and documented individually.

## JK BMS — Gobel Power Home Assistant Integration

Source: `fancyui/Gobel-Battery-HA-Integration`, current `main`.

The current integration forwards only the `sensor` and `binary_sensor` platforms. Therefore the project must currently treat Gobel's JK-BMS integration as **read-only from Home Assistant**. The JK settings view will show configuration/status values but will not present fake writable controls unless upstream adds native writable platforms/actions.

### Aggregate bank sensors exposed by Gobel

The integration creates aggregate sensors with these functions:

- Packs Count
- Total Full Capacity (Ah)
- Total Remaining Capacity (Ah)
- Total Current (A)
- Total SOC (%)
- Total Voltage (V)
- Total Power (kW)
- Max Cell Voltage (mV)
- Min Cell Voltage (mV)
- Cell Voltage Delta (mV)

Actual Home Assistant entity IDs depend on the configured `device_name`; the dashboard therefore cannot safely hard-code a universal `sensor.gobel_...` ID for these entities.

### Per-pack sensors

For every discovered master/slave pack Gobel exposes:

- Voltage
- Current
- Power
- SOC
- SOH
- Remaining Capacity
- Full Capacity
- Cycle Count
- Balance Current (JK only)
- Cell 01 ... Cell N Voltage
- Temperature 01 ... Temperature N

The integration dynamically creates child devices for detected packs, which is suitable for the planned master + slave presentation.

### Dashboard consequence

Deye entities can initially use the verified SolarModbus default IDs. Gobel entity IDs require an installation-specific mapping because Home Assistant derives them from the configured device name. A future setup section will explain how to copy the Gobel entity IDs from Home Assistant into a small mapping block.

## Next mapping work

1. Extract the remaining Deye V2 settings/TOU entities and verified register addresses from the upstream demo dashboard.
2. Extract Gobel binary sensors (MOSFET/protection/alarm states).
3. Define a user-editable Gobel mapping file/template.
4. Build `dashboard.yaml` with five views and safe fallbacks for unavailable optional entities.
