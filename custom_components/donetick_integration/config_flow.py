import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME
from .const import DOMAIN, CONF_API_URL, CONF_API_TOKEN, DEFAULT_NAME
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_API_URL): str,
    vol.Required(CONF_API_TOKEN): str,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
})

class DonetickConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Donetick."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_validate_input(self, user_input):
        """Validate the user input by trying to fetch chores from API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(user_input[CONF_API_URL], headers={"secretkey": user_input[CONF_API_TOKEN]}) as resp:
                    if resp.status != 200:
                        raise Exception(f"API returned status {resp.status}")
                    data = await resp.json()
                    # Optionally check if data is a list or contains expected keys
                    if not isinstance(data, list):
                        raise Exception("Invalid data format from API")
            return True
        except Exception as err:
            _LOGGER.error("API validation failed: %s", err)
            return False

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            is_valid = await self.async_validate_input(user_input)
            if is_valid:
                return self.async_create_entry(title=user_input.get(CONF_NAME, DEFAULT_NAME), data=user_input)
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
