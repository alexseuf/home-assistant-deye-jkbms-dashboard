"""PV & Battery Dashboard integration."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Final

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_AUTO_UPDATE, DOMAIN
from .dashboard_manager import async_install_or_update_dashboard

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.SELECT, Platform.SENSOR]
STATIC_URL = "/pv-battery-dashboard-static"
STATISTICS_CARD_VERSION: Final = "4.03"
STATISTICS_CARD_DIR: Final = "statistics-graph-chart-card"
STATISTICS_CARD_RESOURCE: Final = (
    f"/local/community/{STATISTICS_CARD_DIR}/statistics-graph-chart-card.js"
    f"?v={STATISTICS_CARD_VERSION}"
)
STATISTICS_CARD_ASSETS: Final = {
    "statistics-graph-chart-card.js": (
        "https://github.com/cataseven/Statistics-Graph-Chart-Card/releases/"
        "download/v4.03/statistics-graph-chart-card.js",
        "31ecbec9c22ba756eabf33c9ff375640b967b6b917b5416a6f117d7f99452851",
    ),
    "translations.js": (
        "https://github.com/cataseven/Statistics-Graph-Chart-Card/releases/"
        "download/v4.03/translations.js",
        "08af0ab366cb555c08b5014e46c3ac0f3d2c0769105f3fbf3df04b6ae8f186ed",
    ),
}


def _asset_matches(path: Path, expected_sha256: str) -> bool:
    """Return whether a downloaded frontend asset has the expected digest."""
    return (
        path.is_file()
        and hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256
    )


async def _async_install_statistics_card(hass: HomeAssistant) -> None:
    """Install the licensed frontend card from its official release and register it."""
    target_dir = Path(hass.config.config_dir) / "www" / "community" / STATISTICS_CARD_DIR
    await hass.async_add_executor_job(target_dir.mkdir, 0o755, True, True)
    session = async_get_clientsession(hass)

    for filename, (url, expected_sha256) in STATISTICS_CARD_ASSETS.items():
        target = target_dir / filename
        if await hass.async_add_executor_job(_asset_matches, target, expected_sha256):
            continue
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                payload = await response.read()
        except Exception as err:
            raise ConfigEntryNotReady(
                f"Could not download Statistics Graph Chart Card {STATISTICS_CARD_VERSION}"
            ) from err
        actual_sha256 = hashlib.sha256(payload).hexdigest()
        if actual_sha256 != expected_sha256:
            raise HomeAssistantError(
                f"Checksum mismatch for Statistics Graph Chart Card asset {filename}"
            )
        await hass.async_add_executor_job(target.write_bytes, payload)

    resources = hass.data[LOVELACE_DATA].resources
    await resources.async_get_info()
    existing = next(
        (
            item
            for item in resources.async_items()
            if "statistics-graph-chart-card" in item.get("url", "")
        ),
        None,
    )
    if existing is None:
        if not hasattr(resources, "async_create_item"):
            raise HomeAssistantError(
                "Lovelace resources use YAML mode; register "
                f"{STATISTICS_CARD_RESOURCE} manually"
            )
        await resources.async_create_item(
            {"res_type": "module", "url": STATISTICS_CARD_RESOURCE}
        )
    elif existing.get("url") != STATISTICS_CARD_RESOURCE:
        if not hasattr(resources, "async_update_item"):
            raise HomeAssistantError(
                "Lovelace resources use YAML mode; update the Statistics Graph "
                "Chart Card resource manually"
            )
        await resources.async_update_item(
            existing["id"],
            {"res_type": "module", "url": STATISTICS_CARD_RESOURCE},
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PV & Battery Dashboard from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get("static_registered"):
        static_dir = Path(__file__).parent / "static"
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(static_dir), cache_headers=False)]
        )
        domain_data["static_registered"] = True

    await _async_install_statistics_card(hass)

    # Set up entities first. The managed dashboard can then resolve helper
    # entity IDs from the entity registry instead of assuming a fixed object ID.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if entry.data.get(CONF_AUTO_UPDATE, True):
        try:
            result = await async_install_or_update_dashboard(hass)
            _LOGGER.info("Managed dashboard %s", result)
        except Exception:
            _LOGGER.exception("Could not install/update the managed dashboard")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    The managed Lovelace dashboard is intentionally kept when the integration
    is unloaded or removed so user history/configuration is not deleted
    unexpectedly.
    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
