import logging
import aiohttp
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .button import DonetickChoreCompleteButton

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up Donetick sensors from a config entry."""

    api_url = entry.data["api_url"]
    api_token = entry.data["api_token"]
    name = entry.data.get("name", "Donetick")

    coordinator = DonetickDataUpdateCoordinator(hass, api_url, api_token)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        _LOGGER.error("Failed to fetch initial data from Donetick API")
        return False

    # Store coordinator in hass.data for button platform to use
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    sensors = []
    buttons = []
    for chore in coordinator.data:
        sensor = DonetickChoreSensor(name, chore, coordinator)
        button = DonetickChoreCompleteButton(
            chore["id"], chore["name"], api_url, api_token, sensor
        )
        sensors.append(sensor)
        buttons.append(button)

    async_add_entities(sensors + buttons, True)


class DonetickDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Donetick data API."""

    def __init__(self, hass, api_url, api_token):
        super().__init__(
            hass,
            _LOGGER,
            name="donetick chores",
            update_interval=timedelta(seconds=300),  # 5 minutes
        )
        self.api_url = api_url
        self.api_token = api_token

    async def _async_update_data(self):
        """Fetch data from Donetick API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_url, headers={"secretkey": self.api_token}
                ) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"API response status: {resp.status}")
                    data = await resp.json()
                    if not isinstance(data, list):
                        raise UpdateFailed("Invalid data format")
                    return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")


class DonetickChoreSensor(SensorEntity):
    def __init__(
        self, base_name, chore_data, coordinator: DonetickDataUpdateCoordinator
    ):
        self.coordinator = coordinator
        self._chore_id = chore_data["id"]
        self._base_name = base_name
        self._chore = chore_data

        self._attr_name = chore_data["name"].strip()
        self._attr_unique_id = f"donetick_chore_{self._chore_id}"
        self._attr_has_entity_name = True

        self._update_state_from_chore(chore_data)

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "chore_id": self._chore["id"],
            "assigned_to": self._chore.get("assignedTo", "Unassigned"),
            "due_date": self._chore.get("dueDate"),
            "notes": self._chore.get("notes"),
            **self._extra_attributes,
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, str(self._chore_id))},
            "name": "Donetick Chores",
            "manufacturer": "Donetick",
            "entry_type": "service",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def unique_id(self):
        return self._attr_unique_id

    async def async_update(self):
        # Coordinator fetches data; sensor updates state accordingly
        await self.coordinator.async_request_refresh()
        chores = self.coordinator.data or []
        chore = next((c for c in chores if c["id"] == self._chore_id), None)
        if chore:
            self._chore = chore
            self._update_state_from_chore(chore)
        else:
            _LOGGER.warning("Chore with ID %s not found during update", self._chore_id)

    def _update_state_from_chore(self, chore):
        self._attr_native_value = (
            "incomplete" if chore.get("status", 0) == 0 else "complete"
        )
        self._extra_attributes = {
            "assigned_to": chore.get("assignedTo"),
            "due_date": chore.get("dueDate"),
            "notes": chore.get("notes"),
        }
