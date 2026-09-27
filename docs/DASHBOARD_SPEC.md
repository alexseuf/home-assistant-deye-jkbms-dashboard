# Dashboard specification

## System scope

The dashboard supports **one to three inverter slots**. Each slot may use a different manufacturer or Home Assistant integration.

Typical examples:

- Deye only
- Solis only
- Hoymiles only
- Deye + Solis
- Solis + Hoymiles
- hybrid inverter + one or two additional PV inverters

The dashboard must not assume that battery, grid and load values come from every inverter. These system-level values are mapped from the integration that actually measures them.

## Views

### 1 – Aktuelle Werte

SolarAssistant-inspired live overview.

Planned content:
- PV power and MPPT values
- Wechselrichter 1–3 power/status where configured
- house/load power
- battery power, SOC, voltage, current and temperature
- grid import/export
- directional energy-flow visualization
- today's PV yield, consumption, grid import/export and battery charge/discharge energy
- current-day power chart
- inverter and JK-BMS warning/status indicators

### 2 – Historische Werte

Planned selectable ranges: 24 hours, 7 days, 30 days, 12 months and custom where practical.

Charts:
- inverter / PV / load / battery / grid power
- individual inverter power where configured
- battery SOC
- battery voltage and current
- MPPT voltage/power
- temperatures

### 3 – Summierte Werte

- PV yield
- optional yield per inverter
- consumption
- grid import
- grid export
- battery charged energy
- battery discharged energy
- self-sufficiency / self-consumption where calculable
- daily and monthly charts/tables

### 4 – Einstellungen Wechselrichter

The view is manufacturer-neutral.

Each configured inverter may expose:
- status
- operating mode
- export limitation
- charging parameters
- PV-specific settings
- manufacturer-specific settings

Writable controls must only map to entities/services/registers verified for the **exact integration and inverter model**.

The Deye/SolarModbus V2 and Solis Modbus by Pho3niX90 mappings are reference profiles, not generic register definitions. Controls remain model- and integration-specific.

### 5 – Einstellungen JK BMS

Entity source: Gobel Power Home Assistant integration.

Layout:
- aggregate battery status
- master and each slave battery pack
- SOC, voltage, current, power, temperature and SOH
- minimum/maximum cell and cell-voltage delta
- cell voltage bar chart
- charge/discharge MOSFET status
- balancing status
- alarms/errors
- writable BMS settings only where Gobel Power exposes native writable entities

## Inverter slot model

The dashboard uses these logical slots:

- `inverter_1` – required
- `inverter_2` – optional
- `inverter_3` – optional

Each slot may map the following logical values when available:

- `power`
- `status`
- `daily_yield`
- `pv1_power`, `pv1_voltage`, `pv1_current`
- `pv2_power`, `pv2_voltage`, `pv2_current`
- additional MPPT channels where required

System-level values are mapped separately:

- grid power/import/export
- load/house power
- battery power/SOC/voltage/current
- total PV production

This separation allows an additional Solis or Hoymiles inverter to contribute PV production without pretending that it controls the battery or measures the grid.

## Entity policy

No guessed entity IDs in production YAML.

Entity names must be mapped from the actual Home Assistant integrations in use. Deye/SolarModbus V2 and Solis Modbus by Pho3niX90 are the currently documented reference mappings.

A manufacturer name must not be used as a tab title or generic UI label. Use **Wechselrichter** unless a card intentionally identifies a configured device.