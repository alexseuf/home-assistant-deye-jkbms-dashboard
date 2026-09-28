# Dashboard validation

The project uses two validation levels. Both are release requirements.

## 1. Automated repository validation

Run locally:

```bash
python -m pip install PyYAML==6.0.2
python scripts/validate_dashboard.py
python -m compileall -q -f custom_components/pv_battery_dashboard
```

GitHub Actions runs these checks for every push, pull request, daily schedule and
manual workflow dispatch. The release workflow repeats them before it creates a
tag or HACS archive.

`scripts/validate_dashboard.py` checks:

- root and bundled dashboard YAML are byte-identical
- exactly five visible views, in the documented order
- five distinct visible navigation icons
- exactly three hidden history subviews
- all history chips link 24 hours, 7 days, 30 days and 12 months
- history graph spans match their subviews
- desktop/mobile grid pairs exist at the 700 px breakpoint
- the JK-BMS 16-cell and pack-detail layouts have desktop and mobile variants
- every Pack 00/01/02 detail card uses the six verified live sensor types
- unreliable charge/discharge-enabled binary sensors are not used
- `manifest.json` and `const.py` versions match

## 2. Live Home Assistant browser validation

GitHub-hosted runners cannot reach a private Home Assistant LAN. Perform this
check on the target system before publishing a visual release:

1. Back up the current Lovelace storage dashboard.
2. Install the candidate bundled `dashboard.yaml` and trigger the dashboard
   update entity.
3. Render all five main views at **1280 × 1050 px**.
4. Render all five main views at **412 × 915 px** with touch/mobile emulation.
5. Confirm there are five visible main navigation tabs.
6. On **Historische Werte**, click in this order:
   **7 Tage → 30 Tage → 12 Monate → 24 Stunden**.
7. Confirm each click changes the URL and chart title to the selected range.
8. Confirm all three history range views stay hidden from the main tab bar.
9. Confirm no `hui-error-card` exists on any rendered page.
10. Compare the JK-BMS Pack 00/01/02 values against `/api/states`:
    SOC, voltage, current, remaining capacity, temperature 01 and cycle count.
11. Confirm mobile cards do not truncate labels or values and the three pack
    detail cards are stacked vertically.
12. Repeat the JK-BMS page at desktop width to ensure the responsive change did
    not regress the three-column layout.
13. Never store Home Assistant tokens or authenticated screenshots in Git.

The live check performed for release 0.1.16 covered both viewports, all five
main views, all four history ranges and the three live JK-BMS packs with zero
Lovelace card errors.
