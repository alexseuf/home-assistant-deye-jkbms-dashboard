# Home Assistant Deye & JK-BMS Dashboard

SolarAssistant-inspired Home Assistant dashboard for a Deye Hybrid inverter and JK-BMS battery system.

The dashboard is designed for **SolarModbus V2** on the Deye side and the **Gobel Power Home Assistant integration** for JK-BMS battery packs. The target configuration includes direct USB-to-RS485 communication and support for multi-pack JK-BMS systems (master + slaves).

## Dashboard mock-ups

The following five mock-ups define the current visual target. Values shown in the images are illustrative; the production dashboard will only use verified Home Assistant entities and writable parameters.

### 1. Aktuelle Werte

Live energy flow, PV production, house consumption, grid import/export, battery status and today's power history.

![Aktuelle Werte](docs/images/mockups/01-aktuelle-werte.png)

### 2. Historische Werte

Historical power, battery SOC, battery voltage/current and MPPT charts with selectable time periods.

![Historische Werte](docs/images/mockups/02-historische-werte.png)

### 3. Summierte Werte

Daily and monthly PV production, consumption, grid import/export, battery energy, self-sufficiency and self-consumption.

![Summierte Werte](docs/images/mockups/03-summierte-werte.png)

### 4. Einstellungen Deye

Deye operating parameters and System Timer / TOU. Controls will only be implemented for verified writable SolarModbus entities/registers and must match the inverter model.

![Einstellungen Deye](docs/images/mockups/04-einstellungen-deye.png)

### 5. Einstellungen JK BMS

Aggregate battery-bank data, master/slave packs, cell voltages, temperatures, SOH, balancing and BMS status. Writable controls will only be added where the Gobel Power integration actually exposes them.

![Einstellungen JK BMS](docs/images/mockups/05-einstellungen-jk-bms.png)

## Implementation principles

- No guessed entity IDs in production YAML.
- Deye controls only for verified SolarModbus registers/entities.
- Read-only values are never presented as writable controls.
- JK-BMS controls only where Gobel Power exposes a corresponding writable Home Assistant entity/service.
- Multi-pack installations show both aggregate battery-bank values and each discovered pack.
- The layout should remain usable on desktop, tablet and mobile devices.

## Project files

- [`dashboard.yaml`](dashboard.yaml) – Lovelace dashboard implementation
- [`docs/DASHBOARD_SPEC.md`](docs/DASHBOARD_SPEC.md) – functional specification of the five views
- [`docs/ENTITY_MAPPING.md`](docs/ENTITY_MAPPING.md) – verified entity/register mapping
- [`docs/images/mockups/`](docs/images/mockups/) – individual visual mock-ups

## Status

Entity mapping and dashboard implementation are in progress. Current priorities are completing the Deye System Timer / TOU mapping, matching the Lovelace layout to these mock-ups and mapping the dynamically generated Gobel Power pack entities.