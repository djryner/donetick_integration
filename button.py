import logging
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Donetick buttons."""
    api_url = entry.data["api_url"]
    api_token = entry.data["api_token"]

    # The coordinator should be shared between sensor and button
    _LOGGER.debug("Attempting to retrieve coordinator for Donetick buttons. hass.data content for domain %s, entry %s: %s", DOMAIN, entry.entry_id, hass.data.get(DOMAIN, {}).get(entry.entry_id, {}))
    coordinator = hass.data[DOMAIN][entry.entry_id].get("coordinator")
    if not coordinator:
        _LOGGER.warning("Coordinator not found in hass.data for Donetick buttons. No buttons will be set up.")
        return

    if not hasattr(coordinator, 'data') or not coordinator.data:
        _LOGGER.warning("Coordinator data is missing or empty. No Donetick buttons will be created. Coordinator object: %s", coordinator)
        return

    buttons = []
    _LOGGER.debug("Coordinator found with data. Number of chores to process for buttons: %s", len(coordinator.data))
    for chore in coordinator.data:
        button = DonetickChoreCompleteButton(
            chore["id"], chore["name"], api_url, api_token
        )
        buttons.append(button)
        _LOGGER.debug("Created and appended button: %s", button.name)

    if not buttons:
        _LOGGER.warning("No buttons were created to be added for Donetick.")
    _LOGGER.debug("Calling async_add_entities with %s buttons: %s", len(buttons), [b.name for b in buttons])
    async_add_entities(buttons, True)


class DonetickChoreCompleteButton(ButtonEntity):
    """Button to mark a Donetick chore as complete."""

    def __init__(self, chore_id, chore_name, api_url, api_token):
        self._chore_id = chore_id
        self._api_url = api_url
        self._api_token = api_token
        self._attr_name = f"Complete: {chore_name}"
        self._attr_unique_id = f"{DOMAIN}_complete_{chore_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, chore_id)},
            name="Donetick Chores",
            manufacturer="Donetick",
            model="Chore Completion",
        )

    async def async_press(self) -> None:
        """Send a request to mark the chore as complete and refresh sensor."""
        complete_url = f"{self._api_url}/complete/{self._chore_id}"
        headers = {"secretkey": self._api_token}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(complete_url, headers=headers) as resp:
                    if resp.status != 200:
                        _LOGGER.error(
                            "Failed to complete chore %s: HTTP %s",
                            self._chore_id,
                            resp.status,
                        )
                    else:
                        _LOGGER.info("Successfully completed chore %s", self._chore_id)

        except Exception as err:
            _LOGGER.exception("Error completing chore %s: %s", self._chore_id, err)
