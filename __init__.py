import asyncio
from datetime import timedelta
import logging
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DonetickDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Donetick data API."""

    def __init__(self, hass: HomeAssistant, api_url: str, api_token: str):
        """Initialize."""
        self.api_url = api_url
        self.api_token = api_token
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        url = f"{self.api_url}/chores"  # Assuming /chores is the endpoint
        headers = {"secretkey": self.api_token}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error communicating with API: %s, %s",
                            response.status,
                            await response.text(),
                        )
                        raise UpdateFailed(
                            f"Error communicating with API: {response.status}"
                        )
                    data = await response.json()
                    _LOGGER.debug("Successfully fetched data: %s", data)
                    return data
        except aiohttp.ClientError as err:
            _LOGGER.error("Error during API request: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}")
        except Exception as err:
            _LOGGER.error("Unexpected error during API request: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}")


async def async_setup(hass: HomeAssistant, config: dict):
    # We only support config entries, no YAML config
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Donetick from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    api_url = entry.data["api_url"]
    api_token = entry.data["api_token"]

    coordinator = DonetickDataUpdateCoordinator(hass, api_url, api_token)
    await coordinator.async_config_entry_first_refresh() # Use this for initial refresh

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator, # Store the coordinator
        "name": entry.data.get("name"), # Keep name if needed elsewhere
    }

    # Forward setup to both sensor and button platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "button"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "button"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
