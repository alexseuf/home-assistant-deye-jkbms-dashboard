# Entity mapping

This document defines the manufacturer-neutral entity model for the dashboard and records verified integration-specific mappings.

## 1. Logical inverter slots

The dashboard supports up to three inverters:

| Logical slot | Required | Example |
|---|---:|---|
| Wechselrichter 1 | yes | Deye hybrid |
| Wechselrichter 2 | no | Solis string inverter |
| Wechselrichter 3 | no | Hoymiles / OpenDTU |

Manufacturers may be mixed freely. The slot number is a dashboard concept, not a manufacturer identifier.

## 2. Per-inverter functions

For every configured inverter, map the functions that actually exist:

| Function | Required? | Notes |
|---|---:|---|
| AC / inverter power | recommended | current inverter output |
| status | optional | running/online/error state |
| daily yield | optional | daily PV production |
| PV1 power | optional | MPPT/string input |
| PV1 voltage | optional | MPPT/string input |
| PV1 current | optional | MPPT/string input |
| PV2 power | optional | MPPT/string input |
| PV2 voltage | optional | MPPT/string input |
| PV2 current | optional | MPPT/string input |
| additional MPPTs | optional | add only when available |

Do not invent missing values. For example, a microinverter may only provide AC power and energy while the hybrid inverter provides battery/grid values.

## 3. System-level functions

These values normally have one authoritative source in the installation and are therefore mapped separately from inverter slots:

- total grid power
- grid import/export energy
- load/house power
- battery SOC
- battery power
- battery voltage
- battery current
- battery charge/discharge energy
- total PV production

If multiple inverters contribute to PV production, a later template/helper may sum their individual power/yield entities.

## 4. Deye reference profile — SolarModbus V2

Source: `comdif/ha-solarmodbus`, branch `V2`.

This is the currently verified reference profile and is used by the existing `dashboard.yaml` for Wechselrichter 1.

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

SolarModbus V2 exposes `solarmodbus.write_register`. Register writes are model-sensitive and apply only to a verified Deye profile.

## 5. Solis profile

Solis is supported by the dashboard architecture, but the concrete entity IDs depend on the Home Assistant integration used.

Before adding Solis entities to production YAML:

1. identify the exact Solis integration,
2. copy the real entity IDs from **Developer Tools → States**,
3. map them to the logical functions above,
4. verify units and sign conventions,
5. verify any writable controls separately.

Do not reuse Deye register numbers or services.

## 6. Hoymiles profile

Hoymiles is supported by the dashboard architecture. Depending on the installation, values may come from OpenDTU, AhoyDTU, SolarAssistant MQTT or another integration.

Map only the functions actually exposed by the selected source. A Hoymiles system commonly acts as an additional PV producer, so battery/grid values may continue to come from another inverter or meter.

## 7. Mixed installations

Example:

| Function | Source |
|---|---|
| Wechselrichter 1 power/status/battery/grid | Deye hybrid |
| Wechselrichter 2 power/yield | Solis |
| Wechselrichter 3 power/yield | Hoymiles |
| total house/grid | Deye or dedicated meter |
| battery | Deye + JK-BMS / Gobel |

The dashboard should later calculate total PV power as the sum of all configured inverter/PV sources when appropriate.

## 8. JK BMS — Gobel Power Home Assistant Integration

Source: `fancyui/Gobel-Battery-HA-Integration`.

The integration currently exposes `sensor` and `binary_sensor` platforms. Entity IDs depend on the configured device name.

Aggregate functions include:

- Packs Count
- Total Full Capacity
- Total Remaining Capacity
- Total Current
- Total SOC
- Total Voltage
- Total Power
- Max Cell Voltage
- Min Cell Voltage
- Cell Voltage Delta

Per-pack functions include:

- Voltage
- Current
- Power
- SOC
- SOH
- Remaining Capacity
- Full Capacity
- Cycle Count
- Balance Current
- Cell voltages
- Temperatures

## Next mapping work

1. Record the actual Solis integration and entity IDs used on the target Home Assistant instance.
2. Record the actual Hoymiles/OpenDTU/SolarAssistant entity IDs.
3. Add live cards for inverter 2 and inverter 3 once their entities are verified.
4. Add template/helper sums for total PV power and energy where required.
5. Keep writable controls isolated per manufacturer and inverter model.