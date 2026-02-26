"""Config flow for the Sleeper integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SleeperApiClient, SleeperApiConnectionError, SleeperApiNotFoundError
from .const import CONF_LEAGUE_ID, CONF_LEAGUE_NAME, CONF_USER_ID, CONF_USERNAME, DOMAIN

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LEAGUE_ID): str,
        vol.Optional(CONF_USERNAME, default=""): str,
    }
)


class SleeperConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sleeper."""

    VERSION = 1

    async def _validate_input(
        self, league_id: str, username: str
    ) -> tuple[dict[str, str], dict[str, Any]]:
        """Validate league_id and optional username.

        Returns (errors, data) where errors is a dict of field->error_key
        and data holds the validated config values.
        """
        errors: dict[str, str] = {}
        session = async_get_clientsession(self.hass)
        client = SleeperApiClient(session)

        # Validate league
        try:
            league = await client.async_get_league(league_id)
        except SleeperApiNotFoundError:
            errors[CONF_LEAGUE_ID] = "league_not_found"
            return errors, {}
        except SleeperApiConnectionError:
            errors["base"] = "cannot_connect"
            return errors, {}

        data: dict[str, Any] = {
            CONF_LEAGUE_ID: league_id,
            CONF_LEAGUE_NAME: league.name,
            CONF_USERNAME: "",
            CONF_USER_ID: "",
        }

        # Validate optional username
        if username:
            try:
                user_info = await client.async_get_user(username)
            except SleeperApiNotFoundError:
                errors[CONF_USERNAME] = "user_not_found"
                return errors, data
            except SleeperApiConnectionError:
                errors["base"] = "cannot_connect"
                return errors, data

            user_id = user_info.get("user_id", "")

            # Verify user is in the league
            try:
                league_users = await client.async_get_users(league_id)
            except SleeperApiConnectionError:
                errors["base"] = "cannot_connect"
                return errors, data

            league_user_ids = {u.user_id for u in league_users}
            if user_id not in league_user_ids:
                errors[CONF_USERNAME] = "user_not_in_league"
                return errors, data

            data[CONF_USERNAME] = username
            data[CONF_USER_ID] = user_id

        return errors, data

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            league_id = user_input[CONF_LEAGUE_ID].strip()
            username = user_input.get(CONF_USERNAME, "").strip()

            errors, data = await self._validate_input(league_id, username)

            if not errors:
                await self.async_set_unique_id(f"sleeper_{league_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=data[CONF_LEAGUE_NAME],
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration to add or change the username."""
        errors: dict[str, str] = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert entry is not None

        if user_input is not None:
            username = user_input.get(CONF_USERNAME, "").strip()
            league_id = entry.data[CONF_LEAGUE_ID]

            errors, data = await self._validate_input(league_id, username)

            if not errors:
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **data},
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_USERNAME,
                        default=entry.data.get(CONF_USERNAME, ""),
                    ): str,
                }
            ),
            errors=errors,
        )
