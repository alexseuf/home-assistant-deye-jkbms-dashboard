"""Install and update the managed Lovelace dashboard."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components import frontend
from homeassistant.components.lovelace import dashboard as lovelace_dashboard
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util.yaml import Secrets, load_yaml_dict

from .const import DASHBOARD_ICON, DASHBOARD_TITLE, DASHBOARD_URL_PATH

_LOGGER = logging.getLogger(__name__)


async def _async_load_bundled_dashboard(hass: HomeAssistant) -> dict[str, Any]:
    """Load the bundled dashboard YAML."""
    path = Path(__file__).with_name("dashboard.yaml")
    secrets = Secrets(Path(hass.config.config_dir))
    return await hass.async_add_executor_job(load_yaml_dict, path, secrets)


def _resolve_entity_id(hass: HomeAssistant, template_id: str) -> str:
    """Resolve prefixed Home Assistant entity IDs when there is one clear match."""
    if hass.states.get(template_id) is not None:
        return template_id

    if "." not in template_id:
        return template_id

    domain, object_id = template_id.split(".", 1)
    candidates: set[str] = {
        state.entity_id
        for state in hass.states.async_all(domain)
        if state.entity_id.endswith(object_id)
    }

    registry = er.async_get(hass)
    candidates.update(
        entity.entity_id
        for entity in registry.entities.values()
        if entity.entity_id.startswith(f"{domain}.")
        and entity.entity_id.endswith(object_id)
    )

    if len(candidates) == 1:
        resolved = next(iter(candidates))
        _LOGGER.debug("Resolved dashboard entity %s -> %s", template_id, resolved)
        return resolved

    if len(candidates) > 1:
        _LOGGER.warning(
            "Multiple candidates found for dashboard entity %s: %s",
            template_id,
            ", ".join(sorted(candidates)),
        )

    return template_id


def _resolve_entities(hass: HomeAssistant, value: Any) -> Any:
    """Recursively resolve entity IDs in the dashboard structure."""
    if isinstance(value, dict):
        return {key: _resolve_entities(hass, item) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_entities(hass, item) for item in value]
    if isinstance(value, str):
        # Only replace strings that are exactly entity IDs. Markdown and labels
        # therefore remain untouched.
        if "." in value and " " not in value and "\n" not in value:
            domain = value.split(".", 1)[0]
            if domain in {
                "sensor",
                "binary_sensor",
                "number",
                "switch",
                "select",
                "time",
                "input_number",
                "input_boolean",
            }:
                return _resolve_entity_id(hass, value)
    return value


async def _async_get_dashboard_item(
    hass: HomeAssistant,
) -> tuple[dict[str, Any], bool]:
    """Get or create the Lovelace dashboard metadata item."""
    collection = lovelace_dashboard.DashboardsCollection(hass)
    await collection.async_load()

    for item in collection.async_items():
        if item.get("url_path") == DASHBOARD_URL_PATH:
            return item, False

    item = await collection.async_create_item(
        {
            "url_path": DASHBOARD_URL_PATH,
            "title": DASHBOARD_TITLE,
            "icon": DASHBOARD_ICON,
            "show_in_sidebar": True,
            "require_admin": False,
        }
    )

    # DictStorageCollection returns the created item. Keep a defensive fallback
    # for Home Assistant versions where this return value changes.
    if item is None:
        for stored_item in collection.async_items():
            if stored_item.get("url_path") == DASHBOARD_URL_PATH:
                return stored_item, True
        raise HomeAssistantError("Dashboard metadata was created but cannot be read")

    return item, True


async def async_install_or_update_dashboard(hass: HomeAssistant) -> str:
    """Install or update the managed Lovelace dashboard."""
    if LOVELACE_DATA not in hass.data:
        raise HomeAssistantError("Lovelace is not loaded")

    config = await _async_load_bundled_dashboard(hass)
    config = _resolve_entities(hass, config)

    lovelace_data = hass.data[LOVELACE_DATA]
    store = lovelace_data.dashboards.get(DASHBOARD_URL_PATH)
    created = False

    if store is None:
        item, created = await _async_get_dashboard_item(hass)
        store = lovelace_dashboard.LovelaceStorage(hass, item)
        lovelace_data.dashboards[DASHBOARD_URL_PATH] = store

        if frontend.async_panel_exists(hass, DASHBOARD_URL_PATH):
            raise HomeAssistantError(
                f"Panel path {DASHBOARD_URL_PATH} is already in use"
            )

        frontend.async_register_built_in_panel(
            hass,
            "lovelace",
            frontend_url_path=DASHBOARD_URL_PATH,
            require_admin=False,
            show_in_sidebar=True,
            sidebar_title=DASHBOARD_TITLE,
            sidebar_icon=DASHBOARD_ICON,
            config={"mode": "storage"},
        )

    await store.async_save(config)
    return "installed" if created else "updated"
