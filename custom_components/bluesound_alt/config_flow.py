"""Config flow for Hello World integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant import data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_HOST,
    CONF_HOSTS,
    CONF_NAME,
    CONF_PORT,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv

from .media_player import (DEFAULT_PORT, async_setup_platform, PLATFORM_SCHEMA)
from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

# This is the schema that used to display the UI to the user. This simple
# schema has a single required host field, but it could include a number of fields
# such as username, password etc. See other components in the HA core code for
# further examples.
# Note the input displayed to the user will be translated. See the
# translations/<lang>.json file and strings.json. See here for further information:
# https://developers.home-assistant.io/docs/config_entries_config_flow_handler/#translations
# At the time of writing I found the translations created by the scaffold didn't
# quite work as documented and always gave me the "Lokalise key references" string
# (in square brackets), rather than the actual translated value. I did not attempt to
# figure this out or look further into it.
DATA_SCHEMA = vol.Schema(
        {
            vol.Required(CONF_HOST): cv.string,
            vol.Required(CONF_NAME): cv.string
        }
)

async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    hosts = {
        CONF_HOSTS: [
            {
                "CONF_HOST": data[CONF_HOST],
                "CONF_NAME": data[CONF_NAME],
                "CONF_PORT": DEFAULT_PORT
            }
        ]
    }

    _LOGGER.debug("Adding new device.")

    await async_setup_platform(hass, hosts, False, None)

class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy hub will notify HA of
    # changes.
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)

                data = {
                    CONF_HOSTS: [
                        {
                            CONF_NAME: user_input[CONF_NAME],
                            CONF_HOST: user_input[CONF_HOST],
                            CONF_PORT: DEFAULT_PORT,
                        }
                    ]
                }
                
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=data,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["host"] = "invalid host"
            except InvalidName:
                errors["name"] = "invalid name"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""

class InvalidName(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid player name."""