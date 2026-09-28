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
            (8, 16, "(min-width: 700px)"),
            (2, 16, "(max-width: 699px)"),
            (4, 4, "(min-width: 700px)"),
            (2, 4, "(max-width: 699px)"),
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
