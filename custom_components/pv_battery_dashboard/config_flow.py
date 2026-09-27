"""Config flow for PV & Battery Dashboard."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from .const import CONF_AUTO_UPDATE, DOMAIN, NAME


class PVAndBatteryDashboardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PV & Battery Dashboard."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial setup step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title=NAME, data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(CONF_AUTO_UPDATE, default=True): bool,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
