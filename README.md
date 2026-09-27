# Home Assistant Multi-Inverter & JK-BMS Dashboard

SolarAssistant-inspired Home Assistant dashboard for PV systems with **one to three inverters** and an optional **JK-BMS battery system**.

The dashboard UI is deliberately manufacturer-neutral. Inverter slots 1–3 can be assigned to **Deye, Solis, Hoymiles or other inverter integrations** as long as the required Home Assistant entities are mapped. Mixed systems are supported conceptually, for example Deye + Solis or Solis + Hoymiles.

The existing Deye/SolarModbus V2 mapping remains the verified reference profile for inverter 1. Other manufacturers are not assigned guessed entity IDs; their actual Home Assistant entity IDs must be mapped from the integration used on the target installation.

## Supported layout

- 1, 2 or 3 inverters
- same or mixed inverter manufacturers
- PV/MPPT values per inverter where available
- inverter status and AC power
- combined battery, grid and load values
- JK-BMS master/slave battery systems via Gobel Power
- manufacturer-specific settings only when the integration exposes verified writable entities/services

## Installation

### Recommended installation

The repository now includes a ready-to-copy Home Assistant setup:

- [Home Assistant installation guide](docs/INSTALLATION_HOME_ASSISTANT.md)
- [configuration.yaml snippet](home-assistant/configuration-snippet.yaml)
- [Solis daily/monthly Utility Meter package](home-assistant/packages/solis_dashboard_helpers.yaml)

This loads `dashboard.yaml` directly as a YAML dashboard from Home Assistant's `/config` directory, so you do not have to paste the complete dashboard into the Raw configuration editor.

A standalone HACS package for this dashboard is still a future milestone. The **Solis Modbus** integration itself can already be installed through HACS.

### 1. Install inverter integration(s)

Use the integration that matches each inverter. Examples:

- **Deye:** SolarModbus V2
- **Solis:** **Solis Modbus** von **Pho3niX90** – https://github.com/Pho3niX90/solis_modbus
- **Hoymiles:** a compatible Home Assistant Hoymiles / OpenDTU / SolarAssistant integration

The dashboard UI does not depend on the manufacturer name. The current `dashboard.yaml` is now a concrete **Solis Modbus reference implementation** using documented entities from Pho3niX90; other inverter integrations can be substituted through the logical mapping in [`docs/ENTITY_MAPPING.md`](docs/ENTITY_MAPPING.md).

Verified reference integrations used by this project:

- **Deye / SolarModbus V2:** https://github.com/comdif/ha-solarmodbus
- **Solis / Solis Modbus by Pho3niX90:** https://github.com/Pho3niX90/solis_modbus

The Solis integration supports TCP and direct serial/RS485 setup and exposes sensor, number, switch, select and time entities depending on inverter type and poll profile. The project uses only entities documented by the integration as reference mappings.

### 2. Optional JK-BMS integration

Project: https://github.com/fancyui/Gobel-Battery-HA-Integration

The Gobel Power integration supports JK BMS systems and can expose aggregate values plus individual master/slave battery packs.

### 3. Verify and map entities

Open **Developer Tools → States** in Home Assistant and identify the actual entities for every configured inverter.

The dashboard uses three logical inverter slots:

- **Wechselrichter 1**
- **Wechselrichter 2**
- **Wechselrichter 3**

Only slot 1 is required. Slots 2 and 3 are optional.

Use [`docs/ENTITY_MAPPING.md`](docs/ENTITY_MAPPING.md) as the mapping checklist. The dashboard must use entity IDs actually present in your Home Assistant instance.

### 4. Install the dashboard

For the recommended file-based installation, follow [`docs/INSTALLATION_HOME_ASSISTANT.md`](docs/INSTALLATION_HOME_ASSISTANT.md).

For a quick manual import through the UI:

1. Open **Settings → Dashboards** and create a new dashboard.
2. Open the dashboard and choose **Edit dashboard**.
3. Open the three-dot menu and select **Raw configuration editor**.
4. Copy [`dashboard.yaml`](dashboard.yaml) into the raw editor.
5. If you use Solis Modbus by Pho3niX90, first test the supplied entity IDs as-is. Home Assistant may alter final entity IDs based on device/location naming.
6. For another inverter integration, replace the Solis entity references according to [`docs/ENTITY_MAPPING.md`](docs/ENTITY_MAPPING.md).
7. Save.

The dashboard contains five views:

1. **Aktuelle Werte**
2. **Historische Werte**
3. **Summierte Werte**
4. **Einstellungen Wechselrichter**
5. **Einstellungen JK BMS**

> **Important:** Writable inverter functions are manufacturer-, integration- and model-specific. Never reuse Deye Modbus register writes for Solis, Hoymiles or another inverter. Only expose controls after the exact writable entity/service/register has been verified for that inverter.

## Multi-inverter concept

The dashboard distinguishes between the visual function and the source integration.

For every inverter slot, map as many of these logical functions as the device provides:

- inverter AC power
- operating status
- PV/MPPT power
- PV/MPPT voltage/current
- daily PV yield
- grid/load values if the inverter is the system source for them
- battery values if the inverter is the system source for them
- optional writable settings

Not every inverter has to expose every function. A Hoymiles microinverter, for example, can be used primarily as an additional PV producer while a hybrid inverter provides battery and grid values.

## Dashboard mock-ups

The following five mock-ups are the original visual reference used before today's graphics changes.

### 1. Aktuelle Werte

![Aktuelle Werte](docs/images/mockups/01-aktuelle-werte.png)

### 2. Historische Werte

![Historische Werte](docs/images/mockups/02-historische-werte.png)

### 3. Summierte Werte

![Summierte Werte](docs/images/mockups/03-summierte-werte.png)

### 4. Einstellungen Wechselrichter

![Einstellungen Deye](docs/images/mockups/04-einstellungen-deye.png)

### 5. Einstellungen JK BMS

![Einstellungen JK BMS](docs/images/mockups/05-einstellungen-jk-bms.png)

## Implementation principles

- UI labels are manufacturer-neutral.
- Up to three inverter slots are supported.
- Different inverter manufacturers may be combined.
- No guessed manufacturer entity IDs in production YAML.
- Deye/SolarModbus V2 and Solis Modbus by Pho3niX90 are verified reference profiles.
- Writable controls are only added for verified entities/services/registers of the exact inverter model.
- Read-only values are never presented as writable controls.
- JK-BMS controls are only added where Gobel Power exposes a corresponding writable Home Assistant entity/service.
- Multi-pack battery installations show aggregate values plus discovered packs.
- Layout should remain usable on desktop, tablet and mobile.
- Target distribution remains a HACS-installable dashboard package.

## Project files

- [`dashboard.yaml`](dashboard.yaml) – Lovelace dashboard
- [`docs/DASHBOARD_SPEC.md`](docs/DASHBOARD_SPEC.md) – functional specification
- [`docs/ENTITY_MAPPING.md`](docs/ENTITY_MAPPING.md) – inverter/BMS mapping model and verified reference entities
- [`docs/images/mockups/`](docs/images/mockups/) – visual references
- [`docs/INSTALLATION_HOME_ASSISTANT.md`](docs/INSTALLATION_HOME_ASSISTANT.md) – installation in Home Assistant
- [`home-assistant/configuration-snippet.yaml`](home-assistant/configuration-snippet.yaml) – YAML dashboard registration
- [`home-assistant/packages/solis_dashboard_helpers.yaml`](home-assistant/packages/solis_dashboard_helpers.yaml) – daily/monthly Utility Meter helpers

## Status

The dashboard is manufacturer-neutral and supports up to three inverter slots. The current `dashboard.yaml` implements all five dashboard views using **Solis Modbus by Pho3niX90 as the concrete example profile**, including 14-day daily-energy charts and monthly summaries based on long-term statistics plus Utility Meter helpers. Deye/SolarModbus V2 remains documented as an alternative verified mapping; Hoymiles remains integration-dependent until a specific source is selected.