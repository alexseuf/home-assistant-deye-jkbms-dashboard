# Installation in Home Assistant

This repository can be installed without copying the dashboard through the Raw configuration editor. The recommended setup loads `dashboard.yaml` directly from Home Assistant's `/config` directory and loads the energy helpers as a package.

## Requirements

1. Install **Solis Modbus** by Pho3niX90:
   https://github.com/Pho3niX90/solis_modbus
2. Verify the Solis entities in **Developer Tools -> States**.
3. The example dashboard expects the entity names documented in `docs/ENTITY_MAPPING.md`.

Home Assistant can create Utility Meter helpers with daily and monthly reset cycles. The helper sensors persist over restarts, although the first active day/month is incomplete until the next reset boundary.

## Files to copy

Copy these repository files to Home Assistant:

| Repository file | Home Assistant target |
|---|---|
| `dashboard.yaml` | `/config/dashboard.yaml` |
| `home-assistant/packages/solis_dashboard_helpers.yaml` | `/config/packages/solis_dashboard_helpers.yaml` |

Then merge the contents of `home-assistant/configuration-snippet.yaml` into `/config/configuration.yaml`.

## Option A - File editor / Studio Code Server

1. Open the **File editor** or **Studio Code Server** add-on.
2. Create `/config/packages` if it does not exist.
3. Copy `dashboard.yaml` to `/config/dashboard.yaml`.
4. Copy `home-assistant/packages/solis_dashboard_helpers.yaml` to `/config/packages/solis_dashboard_helpers.yaml`.
5. Open `configuration.yaml`.
6. Add `homeassistant: packages: !include_dir_named packages` if packages are not already enabled.
7. Add the `lovelace: dashboards: pv-batteries:` block from `configuration-snippet.yaml`.
8. Run **Developer Tools -> YAML -> Check configuration**.
9. Restart Home Assistant.
10. The new **PV & Batteries** dashboard should appear in the sidebar.

## Option B - SSH / Terminal

From the Home Assistant terminal:

```bash
mkdir -p /config/packages

wget -O /config/dashboard.yaml \
  https://raw.githubusercontent.com/alexseuf/home-assistant-deye-jkbms-dashboard/main/dashboard.yaml

wget -O /config/packages/solis_dashboard_helpers.yaml \
  https://raw.githubusercontent.com/alexseuf/home-assistant-deye-jkbms-dashboard/main/home-assistant/packages/solis_dashboard_helpers.yaml
```

Then merge `home-assistant/configuration-snippet.yaml` into `configuration.yaml`, check the configuration and restart Home Assistant.

## Entity names to verify

The Utility Meter package uses these total-increasing Solis source entities:

- `sensor.solis_pv_total_energy_generation`
- `sensor.solis_total_energy_consumption`
- `sensor.solis_total_energy_imported_from_grid`
- `sensor.solis_total_energy_fed_into_grid`
- `sensor.solis_total_battery_charge_energy`
- `sensor.solis_total_battery_discharge_energy`

Depending on how the Solis device was named when the integration was configured, Home Assistant can add a location/device prefix. If one of these entities does not exist, change only the `source:` line in `solis_dashboard_helpers.yaml` to the actual entity ID.

## 14-day and monthly charts

The dashboard uses Home Assistant's built-in `statistics-graph` card. The Solis total energy counters are `total_increasing` sensors, so the dashboard plots their **change** for each day and each month.

No HACS chart card is required for these graphs.

## Updating later

After changes in this GitHub repository, replace `/config/dashboard.yaml` with the new version. If the helper file changed, replace that file too and restart Home Assistant.

## HACS status

The Solis Modbus integration itself is installable through HACS. This dashboard repository is not yet packaged as a standalone HACS dashboard distribution; the YAML-dashboard method above is currently the most direct and transparent installation route.
