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

## Installation and updates via HACS

The project now contains a real Home Assistant custom integration. HACS installs the integration into `custom_components/pv_battery_dashboard` and can manage later updates.

### 1. Open this repository directly in HACS

[![Open your Home Assistant instance and open this repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=alexseuf&repository=home-assistant-deye-jkbms-dashboard&category=integration)

If the button is not used, add this repository manually in **HACS → ⋮ → Custom repositories**:

- Repository: `https://github.com/alexseuf/home-assistant-deye-jkbms-dashboard`
- Type: **Integration**

Then choose **Download** in HACS and restart Home Assistant.

### 2. Add the integration

After the restart, use this button:

[![Add PV & Battery Dashboard to Home Assistant.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=pv_battery_dashboard)

Or open **Settings → Devices & services → Add integration** and search for **PV & Battery Dashboard**.

During setup, leave **Dashboard bei Start automatisch aktualisieren** enabled if the HACS version should manage the dashboard automatically.

The integration creates a Lovelace **storage dashboard** named **PV & Batteries** with URL path `pv-battery-dashboard`. No change to `configuration.yaml`, no package file and no Raw configuration editor are required.

### 3. Install the inverter integration

For the current example profile install **Solis Modbus by Pho3niX90**:

https://github.com/Pho3niX90/solis_modbus

The bundled dashboard in version **0.1.1** is mapped to the verified Solis S5-EH1P entity IDs from the target Home Assistant installation and to the verified Gobel/JK-BMS aggregate plus pack 00–02 entities. The generic mapping model remains documented for other installations.

Other inverter profiles remain possible through the mapping model in [`docs/ENTITY_MAPPING.md`](docs/ENTITY_MAPPING.md).

### Verified 0.1.1 target profile

Version **0.1.1** uses the actual entity IDs exported from the target Home Assistant instance on 2026-09-27. It removes non-existent Solis TOU controls from the dashboard and adds the real three-pack Gobel/JK-BMS data.

### Updating

Releases are published with version tags, matching the update model used by `tigo-tap-local`.

1. HACS detects a newer GitHub release.
2. Home Assistant exposes the HACS repository as an available update under **Settings → Updates**.
3. Confirm the update there; HACS downloads and installs the new integration version.
4. If Home Assistant requests a restart, confirm the restart from the update flow.
5. With automatic dashboard updates enabled, the managed dashboard is replaced by the bundled dashboard during startup.

A manual fallback remains available under **Settings → Devices & services → PV & Battery Dashboard → Entities → Dashboard aktualisieren**.

> The dashboard created by this integration is managed content. Manual edits to that specific dashboard can be overwritten by the next automatic dashboard update.

### Manual / legacy installation

The previous YAML/package method remains documented in [`docs/INSTALLATION_HOME_ASSISTANT.md`](docs/INSTALLATION_HOME_ASSISTANT.md) for users who do not want HACS.

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
- HACS integration installs and updates the managed Lovelace dashboard without editing `configuration.yaml`.

## Project files

- [`dashboard.yaml`](dashboard.yaml) – Lovelace dashboard
- [`docs/DASHBOARD_SPEC.md`](docs/DASHBOARD_SPEC.md) – functional specification
- [`docs/ENTITY_MAPPING.md`](docs/ENTITY_MAPPING.md) – inverter/BMS mapping model and verified reference entities
- [`docs/VALIDATION.md`](docs/VALIDATION.md) – automated CI checks and the live desktop/mobile release checklist
- [`docs/images/mockups/`](docs/images/mockups/) – visual references
- [`docs/INSTALLATION_HOME_ASSISTANT.md`](docs/INSTALLATION_HOME_ASSISTANT.md) – installation in Home Assistant
- [`custom_components/pv_battery_dashboard/`](custom_components/pv_battery_dashboard/) – HACS custom integration
- [`hacs.json`](hacs.json) – HACS repository metadata
- [`home-assistant/configuration-snippet.yaml`](home-assistant/configuration-snippet.yaml) – legacy YAML dashboard registration
- [`home-assistant/packages/solis_dashboard_helpers.yaml`](home-assistant/packages/solis_dashboard_helpers.yaml) – optional legacy Utility Meter helpers

## Status

The dashboard is manufacturer-neutral and supports up to three inverter slots. The repository is now structured as a **HACS custom integration**. Its config flow creates and manages a Lovelace storage dashboard automatically; HACS handles integration updates, and the dashboard can be refreshed automatically after restart or manually with the provided Home Assistant button. The bundled reference profile currently uses **Solis Modbus by Pho3niX90**.

## Quality checks

GitHub Actions automatically validates the project:

- **HACS validation** for repository/integration structure
- **hassfest** for Home Assistant manifests, config flow and translations
- **Python compile check** with `compileall`
- **literal \\n guard** to catch accidental escaped newlines outside strings/comments
- **dashboard contract validation** for five visible views, history navigation, responsive layouts, verified JK-BMS detail entities and synchronized YAML copies
- **daily scheduled validation** in addition to push/pull-request checks

The exact automated checks and the required live Home Assistant browser test are
documented in [`docs/VALIDATION.md`](docs/VALIDATION.md). GitHub-hosted runners
cannot access the private Home Assistant LAN, so the repository workflow enforces
all static dashboard contracts while the documented live release gate covers
desktop/mobile rendering and real entity values.

The release workflow mirrors the protection used in `alexseuf/tigo-tap-local`:

- validates that the release/tag version matches `manifest.json`
- recompiles all integration Python files
- repeats the literal-newline guard
- builds `pv_battery_dashboard.zip`
- creates a GitHub release with generated release notes


## Frontend dependencies for dashboard 0.1.3

Version **0.1.3** redesigns the dashboard closer to the visual mock-ups and requires three HACS frontend cards:

1. **Power Flow Card Plus** — central live PV/grid/battery/home energy flow
   - HACS search name: `Power Flow Card Plus`
   - Repository: `flixlix/power-flow-card-plus`
2. **ApexCharts Card** — compact historic, daily and monthly graphs
   - HACS search name: `ApexCharts Card`
   - Repository: `RomRider/apexcharts-card`
3. **Mushroom** — compact metric/status cards and headings
   - HACS search name: `Mushroom`
   - Repository: `piitaya/lovelace-mushroom`

Install all three in HACS **before updating PV & Battery Dashboard to 0.1.3**, then restart Home Assistant once. HACS normally registers their Lovelace resources automatically.

If one of the cards was installed but Home Assistant still shows `Custom element doesn't exist`, hard-refresh the browser with `Ctrl+F5` and verify the resource under **Settings → Dashboards → Resources**.

The actual Solis S5-EH1P and JK-BMS entity mapping from version 0.1.1/0.1.2 remains unchanged.


## Dashboard 0.1.4

Version **0.1.4** concentrates on the first **Aktuelle Werte** page and intentionally leaves the other four views unchanged for iterative visual testing.

Changes:

- replaced the generic Power Flow Card Plus block with a custom picture-elements energy-flow scene
- added a bundled inverter/arrow SVG so no additional HACS dependency is needed
- arranged PV, inverter, load, battery and grid like the visual mock-up
- moved daily energy values into the four energy-flow tiles
- reduced the electrical summary to the five mock-up values
- expanded the daily ApexCharts graph to a single wide chart with PV/load/battery/grid colours matching the mock-up

The existing Mushroom and ApexCharts dependencies remain required. Power Flow Card Plus may remain installed but is no longer used on the first page in 0.1.4.


## Dashboard 0.1.5

Version **0.1.5** makes the first dashboard page responsive and uses the available width more effectively.

- first view changed from masonry to full-width panel layout
- energy-flow text and icons use responsive CSS `clamp()` sizing
- the five electrical summary values use a responsive picture-elements strip instead of a fixed five-column Mushroom grid
- desktop uses almost the full Lovelace content width
- mobile remains single-column and the key labels shrink instead of overflowing
- the other four dashboard pages remain unchanged


## Dashboard 0.1.9

Version **0.1.9** refines the first page against the reference mock-up:

- new versioned energy-flow SVG to avoid stale browser/Home Assistant caching
- PV, Verbrauch, Batterie and Netz icons/headings placed inside the four cards
- only the large live power value remains dynamic in each outer card
- inverter title is static; live status is shown separately below it
- five metric cards use the exact mock-up labels:
  - PV Spannung 1
  - PV Spannung 2
  - Batteriespannung
  - Batteriestrom
  - Batterie Temperatur
- metric values are shown as a second, larger line
- rolling 24-hour power chart remains unchanged


## Dashboard 0.1.10

Version **0.1.10** further aligns the first page with the supplied visual reference:

- outer-card values are left-aligned to the same text edge as the mock-up
- PV / Verbrauch / Batterie / Netz use a clearer title → large power → small secondary-value hierarchy
- main power values are larger and more dominant
- daily energy / SOC lines are smaller and aligned below the main value
- inverter title and live status typography are reduced to the reference proportions
- the five electrical metric cards use smaller labels and larger second-line values
- new versioned SVG assets avoid stale Home Assistant/browser cache
- rolling 24-hour power chart is retained


## Dashboard 0.1.11

Version **0.1.11** performs another mock-up focused refinement of the first page:

- main PV / load / battery / grid power values are larger and more dominant
- secondary daily-energy / SOC lines are larger and moved upward inside the cards
- all dynamic outer-card text stays on the same left text edge as the static heading
- inverter graphic is about 10% smaller and has more internal spacing
- inverter live status is slightly larger and clearer
- five electrical metric cards are left-aligned like the reference mock-up
- metric labels remain on the first line and values are larger on the second line
- the 24-hour chart is slightly taller
- battery history is now a normal line rather than a filled area, matching the reference chart more closely
- versioned SVG assets are used again to avoid stale browser/Home Assistant caching


## Dashboard 0.1.12

Version **0.1.12** combines the next mock-up refinements:

- the four outer energy-flow cards now use a four-line hierarchy:
  - heading
  - large live power
  - small descriptor
  - small live secondary value
- PV shows Tagesertrag on a separate line from its kWh value
- Verbrauch shows Tagesverbrauch on a separate line from its kWh value
- Batterie shows SOC on a separate line from the percentage
- Netz shows Einspeisung heute on a separate line from its kWh value
- the five electrical metric headings are larger
- the last metric heading is written as **Batterietemperatur** and still fits inside the card
- the integration adds a small helper sensor that mirrors the JK-BMS total battery voltage with one decimal place
- the first-page Batteriespannung metric uses that helper so values such as **52,1 V** are displayed consistently


## Dashboard 0.1.13

Version **0.1.13** fixes the first visual issues found after testing the four-line cards:

- outer energy cards are taller so all four text lines have their own vertical space
- main power, descriptor and secondary value no longer overlap
- lower battery/grid cards use the same spacing as the upper PV/load cards
- the five metric headings are slightly larger; `Batterietemperatur` still fits inside its card
- the one-decimal battery-voltage helper is now set up before the managed dashboard is generated
- the dashboard resolves the helper entity by suffix from Home Assistant's entity registry instead of assuming a fixed entity ID
- this removes the unavailable/warning icon caused by the previous startup order


## Dashboard 0.1.14

Version **0.1.14** completes the five-view redesign and validates it against the
live Home Assistant installation:

- all five views now follow the supplied mock-ups with a consistent panel layout
- historical values provide power, battery SOC, battery voltage/current and MPPT charts
- summed values provide daily, 14-day, monthly and long-term energy summaries
- inverter settings show verified Solis S5-EH1P status, BMS and diagnostic data without unsafe write controls
- JK-BMS provides aggregate values, three pack summaries, all 16 Pack 1 cell voltages and pack diagnostics
- the five current-value metrics use robust Mushroom entity cards so their values remain visible
- the previous empty dynamic cell-voltage chart is replaced by a responsive 16-cell comparison grid
- both dashboard YAML copies are kept identical and were checked for YAML/card errors in the live system


## Dashboard 0.1.15

Version **0.1.15** fixes dashboard navigation and makes the historical range
selector functional:

- the JK-BMS view uses a broadly supported battery icon, so all five main tabs are visibly distinct
- the dashboard still exposes exactly five main tabs
- 7-day, 30-day and 12-month history ranges are implemented as hidden subviews
- the four history chips navigate between 24 hours, 7 days, 30 days and 12 months
- longer ranges use progressively coarser aggregation to keep charts responsive
- all four chip transitions and chart titles were verified in a real Home Assistant browser session


## Dashboard 0.1.16

Version **0.1.16** adds a responsive portrait-phone layout and corrects the
three JK-BMS pack detail cards:

- native screen visibility conditions select desktop or mobile grid variants at 700 px
- current-value metrics wrap from five desktop columns to two mobile columns
- historical detail charts and summary/inverter sections stack on narrow screens
- JK-BMS totals and pack summaries stack vertically on phones
- all 16 cell voltages change from eight to two columns on phones
- cell extrema change from four to two columns
- the three pack detail cards change from three columns to a vertical stack
- unreliable charge/discharge-enabled bits are replaced by verified live pack values
- each pack now shows SOC, voltage, current, remaining capacity, temperature and cycle count
- all five main views were browser-tested at 412 × 915 px with no Lovelace card errors
- the JK-BMS view was also browser-tested at desktop width after the responsive changes


## Dashboard 0.1.17

Version **0.1.17** extends the JK-BMS view with pack-level diagnostics and a
persistent pack selector:

- the overall battery section also shows power, maximum cell voltage and cell-voltage delta
- every pack summary also shows measured power plus its calculated maximum cell voltage and delta
- Pack 1, Pack 2 and Pack 3 can be selected above the individual-value section
- the selection is represented by a Home Assistant select entity and survives restarts
- the selected pack shows all 16 cell voltages and all six temperature sensors
- desktop uses compact 8/6-column grids; portrait phones use readable two-column grids
- repository validation requires all three pack options, 48 cell entities, 18 temperature entities and the new aggregate values


## Dashboard 0.1.18

Version **0.1.18** expands all four historical ranges with verified Solis and
JK-BMS diagnostics:

- inverter and Solis battery temperature
- grid voltage and frequency
- backup AC voltage, household load and backup load
- MPPT voltages, currents and individual/total PV power
- battery voltage and current
- one cell-voltage-delta curve for each connected battery pack
- one maximum-cell-temperature curve for each pack, calculated from temperature sensors 1–4
- the complete chart set is available for 24 hours, 7 days, 30 days and 12 months
- aggregation changes from 5 minutes to 30 minutes, 2 hours and 1 day for the longer ranges
- CI now rejects releases if a range is missing one of these charts or uses the wrong span/aggregation


## Dashboard 0.1.20

Version **0.1.20** intentionally discards the household-load fallback introduced in
0.1.19 and restores the verified 0.1.18 Solis entity mapping.

The **Historische Werte** range selector now contains a fifth button:
**Benutzerdefiniert**.

Selecting it opens a dedicated historical subview with:

- freely selectable **Von** and **Bis** date/time fields
- an **Anzeigen** button that applies the selected interval
- a **Letzte 24 h** reset button
- the same historical chart set used by the fixed 24 h / 7 d / 30 d / 12 month views
- automatic aggregation based on the selected interval:
  - up to 2 days: 5 minutes
  - up to 14 days: 30 minutes
  - up to 60 days: 2 hours
  - longer ranges: 1 day
- responsive two-column layout on desktop and one column on mobile

The custom range control is bundled with this integration and registered automatically
as a Lovelace module in storage mode. No additional HACS frontend card is required
beyond the existing ApexCharts Card and Mushroom dependencies.


## Dashboard 0.1.21

Version **0.1.21** fixes the **Benutzerdefiniert** historical-range page introduced
in 0.1.20.

The bundled `pv-history-range-card.js` is now loaded through Home Assistant's
supported frontend module registration API (`frontend.add_extra_js_url`) instead of
being inserted into the Lovelace resources collection.

This makes the custom card available reliably after an integration restart / Home
Assistant restart and avoids the red **Konfigurationsfehler** shown when the card
module was not loaded.

The 0.1.20 behavior remains otherwise unchanged:

- 0.1.19 household-load fallback stays reverted
- **Benutzerdefiniert** remains the fifth history-range button
- freely selectable **Von** and **Bis** date/time fields
- automatic aggregation based on the selected interval
- no additional HACS frontend dependency is required
