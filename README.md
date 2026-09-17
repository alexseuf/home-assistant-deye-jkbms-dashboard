# Home Assistant Deye & JK-BMS Dashboard

SolarAssistant-inspired Home Assistant dashboard for a Deye Hybrid inverter and JK-BMS battery systems.

## Project goals

The project provides a ready-to-use Lovelace dashboard with five views:

1. **Aktuelle Werte** – live energy flow and important inverter/battery measurements
2. **Historische Werte** – historical power, energy, SOC, voltage, current and MPPT charts
3. **Summierte Werte** – daily/monthly/total PV production, consumption, grid import/export and battery energy
4. **Einstellungen Deye** – writable Deye inverter parameters including operating mode, charge/discharge limits and System Timer / TOU
5. **Einstellungen JK BMS** – JK-BMS status, individual battery packs, cell voltages and writable settings exposed by the integration

## Data sources

- **Deye:** Home Assistant SolarModbus integration, with direct USB-to-RS485 operation as a target configuration.
- **JK BMS:** Gobel Power Home Assistant integration. Multi-pack systems (master + slaves) should be represented individually as well as through aggregate battery values.

## Design

The UI is intended to follow the information density and workflow of SolarAssistant while remaining a native Home Assistant Lovelace dashboard. It will support desktop/tablet layouts and should remain usable on mobile devices.

## Important implementation rule

The dashboard must only expose controls for parameters that the respective Home Assistant integration actually exposes as writable entities. Read-only Modbus/BMS values must never be represented as writable controls.

## Status

Initial project structure. Entity mapping and the first functional dashboard YAML are the next implementation steps.
