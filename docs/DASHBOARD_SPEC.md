# Dashboard specification

## Views

### 1 – Aktuelle Werte
SolarAssistant-inspired live overview.

Planned content:
- PV power and MPPT values
- Deye inverter status
- House/load power
- Battery power, SOC, voltage, current and temperature
- Grid import/export
- Directional energy-flow visualization
- Today's PV yield, consumption, grid import/export and battery charge/discharge energy
- Current-day power chart
- Deye and JK-BMS warning/status indicators

### 2 – Historische Werte
Planned selectable ranges: 24 hours, 7 days, 30 days, 12 months and custom where practical.

Charts:
- PV / load / battery / grid power
- Battery SOC
- Battery voltage and current
- MPPT voltage/power
- Temperatures

### 3 – Summierte Werte
- PV yield
- Consumption
- Grid import
- Grid export
- Battery charged energy
- Battery discharged energy
- Self-sufficiency / self-consumption where calculable from available entities
- Daily and monthly charts/tables

### 4 – Einstellungen Deye
Controls must map to writable SolarModbus entities only.

Target controls where supported:
- Work Mode
- Energy Pattern
- Solar Sell / Zero Export
- Maximum export power
- Grid Charge
- Generator Charge
- Smart Load
- Battery maximum charge/discharge current
- SOC limits
- AC/grid charging parameters
- System Timer / TOU
- Six TOU periods with time, SOC, power and grid-charge state

### 5 – Einstellungen JK BMS
Entity source: Gobel Power Home Assistant integration.

Layout:
- Aggregate battery status
- Master and each slave battery pack
- SOC, voltage, current, power, temperature and SOH
- Minimum/maximum cell and cell-voltage delta
- Cell voltage bar chart
- charge/discharge MOSFET status
- balancing status
- alarms/errors
- writable BMS settings only where Gobel Power exposes native writable entities

## Entity policy

No guessed entity IDs in the production dashboard. Entity names must be mapped from the actual SolarModbus and Gobel Power integrations. A mapping layer/document will be maintained so integration naming changes can be handled without redesigning the dashboard.
