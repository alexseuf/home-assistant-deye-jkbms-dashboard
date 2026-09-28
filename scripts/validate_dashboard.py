#!/usr/bin/env python3
"""Validate the managed Lovelace dashboard and release metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROOT_DASHBOARD = ROOT / "dashboard.yaml"
BUNDLED_DASHBOARD = (
    ROOT / "custom_components" / "pv_battery_dashboard" / "dashboard.yaml"
)
MANIFEST = ROOT / "custom_components" / "pv_battery_dashboard" / "manifest.json"
CONST = ROOT / "custom_components" / "pv_battery_dashboard" / "const.py"
INIT = ROOT / "custom_components" / "pv_battery_dashboard" / "__init__.py"
SELECT = ROOT / "custom_components" / "pv_battery_dashboard" / "select.py"

MAIN_VIEWS = [
    "aktuelle-werte",
    "historische-werte",
    "summierte-werte",
    "einstellungen-wechselrichter",
    "einstellungen-jk-bms",
]
HISTORY_SUBVIEWS = {
    "historische-werte-7-tage": "7d",
    "historische-werte-30-tage": "30d",
    "historische-werte-12-monate": "365d",
}
HISTORY_TARGETS = {
    "/pv-battery-dashboard/historische-werte",
    "/pv-battery-dashboard/historische-werte-7-tage",
    "/pv-battery-dashboard/historische-werte-30-tage",
    "/pv-battery-dashboard/historische-werte-12-monate",
}
HISTORY_CHART_TITLES = {
    "Batteriespannung & Strom",
    "PV Eingänge (MPPT)",
    "Wechselrichtertemperatur",
    "Netzspannung & Frequenz",
    "Backup-AC & Last",
    "MPPT-Ströme",
    "PV- & MPPT-Leistung",
    "Zellspannungsdifferenz je Batteriepack",
    "Maximale Zelltemperatur je Batteriepack",
}
HISTORY_RANGES = {
    "historische-werte": ("24h", "5min"),
    "historische-werte-7-tage": ("7d", "30min"),
    "historische-werte-30-tage": ("30d", "2h"),
    "historische-werte-12-monate": ("365d", "1d"),
}


def fail(message: str) -> None:
    raise SystemExit(f"dashboard validation failed: {message}")


def walk(value: Any) -> Iterable[dict[str, Any]]:
    """Yield every mapping in a nested dashboard structure."""
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def screen_query(card: dict[str, Any]) -> str | None:
    for condition in card.get("visibility", []):
        if condition.get("condition") == "screen":
            return condition.get("media_query")
    return None


def grid_signatures(view: dict[str, Any]) -> set[tuple[int, int, str | None]]:
    return {
        (card.get("columns"), len(card.get("cards", [])), screen_query(card))
        for card in walk(view)
        if card.get("type") == "grid"
    }


def validate() -> None:
    if ROOT_DASHBOARD.read_bytes() != BUNDLED_DASHBOARD.read_bytes():
        fail("dashboard.yaml and bundled dashboard.yaml differ")

    dashboard = yaml.safe_load(ROOT_DASHBOARD.read_text(encoding="utf-8"))
    views = dashboard.get("views", [])
    main_views = [view for view in views if not view.get("subview")]
    subviews = [view for view in views if view.get("subview")]

    if [view.get("path") for view in main_views] != MAIN_VIEWS:
        fail("the five visible views or their order changed")
    icons = [view.get("icon") for view in main_views]
    if any(not icon for icon in icons) or len(set(icons)) != 5:
        fail("all five visible views need distinct non-empty icons")
    if {view.get("path") for view in subviews} != set(HISTORY_SUBVIEWS):
        fail("history subviews must be exactly 7 days, 30 days and 12 months")

    history_views = [
        view for view in views if str(view.get("path", "")).startswith("historische-werte")
    ]
    for view in history_views:
        chips = next(
            (
                card
                for card in walk(view)
                if card.get("type") == "custom:mushroom-chips-card"
            ),
            None,
        )
        if chips is None:
            fail(f"{view['path']} has no history range chips")
        targets = {
            chip.get("tap_action", {}).get("navigation_path")
            for chip in chips.get("chips", [])
        }
        if targets != HISTORY_TARGETS:
            fail(f"{view['path']} does not link all four history ranges")

    for path, graph_span in HISTORY_SUBVIEWS.items():
        view = next(view for view in subviews if view["path"] == path)
        spans = {
            card.get("graph_span")
            for card in walk(view)
            if card.get("type") == "custom:apexcharts-card"
        }
        if graph_span not in spans:
            fail(f"{path} is missing graph_span {graph_span}")

    for path, (graph_span, duration) in HISTORY_RANGES.items():
        view = next(view for view in views if view["path"] == path)
        charts = [
            card
            for card in walk(view)
            if card.get("type") == "custom:apexcharts-card"
            and card.get("header", {}).get("title") in HISTORY_CHART_TITLES
        ]
        titles = {card["header"]["title"] for card in charts}
        if titles != HISTORY_CHART_TITLES:
            fail(f"{path} does not contain the complete switchable chart set")
        for card in charts:
            if card.get("graph_span") != graph_span:
                fail(f"{path} chart {card['header']['title']} has the wrong range")
            configured_duration = (
                card.get("all_series_config", {})
                .get("group_by", {})
                .get("duration")
            )
            if configured_duration != duration:
                fail(
                    f"{path} chart {card['header']['title']} needs grouping {duration}"
                )

    helper_text = (ROOT / "custom_components" / "pv_battery_dashboard" / "sensor.py").read_text(
        encoding="utf-8"
    )
    for helper in ("PackCellDeltaSensor", "PackMaximumCellTemperatureSensor"):
        if helper not in helper_text:
            fail(f"historical helper sensor {helper} is missing")
    if "range(1, 5)" not in helper_text:
        fail("maximum pack temperature must use the four requested cell sensors")

    responsive_requirements = {
        "aktuelle-werte": {(5, 5, "(min-width: 700px)"), (2, 5, "(max-width: 699px)")},
        "historische-werte": {(2, 2, "(min-width: 700px)"), (1, 2, "(max-width: 699px)")},
        "einstellungen-wechselrichter": {
            (3, 3, "(min-width: 700px)"),
            (1, 3, "(max-width: 699px)"),
            (2, 2, "(min-width: 700px)"),
            (1, 2, "(max-width: 699px)"),
        },
        "einstellungen-jk-bms": {
            (3, 6, "(min-width: 700px)"),
            (1, 6, "(max-width: 699px)"),
            (8, 16, "(min-width: 700px)"),
            (2, 16, "(max-width: 699px)"),
            (6, 6, "(min-width: 700px)"),
            (2, 6, "(max-width: 699px)"),
            (3, 3, "(min-width: 700px)"),
            (1, 3, "(max-width: 699px)"),
        },
    }
    for path, required in responsive_requirements.items():
        view = next(view for view in main_views if view["path"] == path)
        missing = required - grid_signatures(view)
        if missing:
            fail(f"{path} is missing responsive grids: {sorted(missing)}")

    bms_view = next(view for view in main_views if view["path"] == "einstellungen-jk-bms")
    selector = "select.solar_pv_battery_dashboard_jk_bms_pack_auswahl"
    selector_chips = next(
        (
            card
            for card in walk(bms_view)
            if card.get("type") == "custom:mushroom-chips-card"
            and any(
                chip.get("tap_action", {}).get("target", {}).get("entity_id") == selector
                for chip in card.get("chips", [])
            )
        ),
        None,
    )
    if selector_chips is None:
        fail("JK-BMS view has no persistent pack selector")
    options = {
        chip.get("tap_action", {}).get("data", {}).get("option")
        for chip in selector_chips.get("chips", [])
    }
    if options != {"Pack 1", "Pack 2", "Pack 3"}:
        fail("JK-BMS selector must offer Pack 1, Pack 2 and Pack 3")

    bms_text = ROOT_DASHBOARD.read_text(encoding="utf-8")
    for pack in range(3):
        prefix = f"sensor.jk_bms_pack_{pack:02d}"
        required_entities = {
            f"{prefix}_power",
            *(f"{prefix}_cell_{cell:02d}_voltage" for cell in range(1, 17)),
            *(f"{prefix}_temperature_{temp:02d}" for temp in range(1, 7)),
        }
        missing = sorted(entity for entity in required_entities if entity not in bms_text)
        if missing:
            fail(f"pack {pack + 1} is missing power/cell/temperature entities: {missing}")
    for entity in (
        "sensor.jk_bms_total_jk_bms_total_power",
        "sensor.jk_bms_total_jk_bms_max_cell_voltage",
        "sensor.jk_bms_total_jk_bms_cell_voltage_delta",
    ):
        if entity not in bms_text:
            fail(f"overall battery is missing {entity}")

    if "Platform.SELECT" not in INIT.read_text(encoding="utf-8"):
        fail("the integration does not load the select platform")
    select_text = SELECT.read_text(encoding="utf-8")
    if not all(option in select_text for option in ("Pack 1", "Pack 2", "Pack 3")):
        fail("select platform does not provide all three pack options")

    detail_cards = [
        card
        for card in walk(bms_view)
        if card.get("type") == "entities" and str(card.get("title", "")).startswith("Pack 0")
    ]
    if len(detail_cards) != 6:
        fail("desktop and mobile layouts must each contain three BMS detail cards")
    required_suffixes = {
        "soc",
        "voltage",
        "current",
        "remaining_capacity",
        "temperature_01",
        "cycle_count",
    }
    for card in detail_cards:
        entity_ids = {
            item["entity"] if isinstance(item, dict) else item
            for item in card.get("entities", [])
        }
        suffixes = {entity_id.rsplit("_", 1)[-1] for entity_id in entity_ids}
        # Multi-word suffixes need an explicit endswith check.
        if not all(any(entity_id.endswith(suffix) for entity_id in entity_ids) for suffix in required_suffixes):
            fail(f"{card['title']} does not contain the six verified live values")
        if any(entity_id.startswith("binary_sensor.") for entity_id in entity_ids):
            fail(f"{card['title']} must not use unreliable enabled-status bits")

    manifest_version = json.loads(MANIFEST.read_text(encoding="utf-8"))["version"]
    match = re.search(r'^VERSION = "([^"]+)"$', CONST.read_text(encoding="utf-8"), re.M)
    if match is None or match.group(1) != manifest_version:
        fail("manifest.json and const.py versions differ")

    print(
        "dashboard validation passed: "
        "5 visible views, 3 history subviews, responsive grids, verified BMS details, "
        f"version {manifest_version}"
    )


if __name__ == "__main__":
    validate()
