import logging
import aiohttp
from datetime import timedelta # Keep for now, might be used in extra_state_attributes if parsing dates
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
# from .button import DonetickChoreCompleteButton # Button setup is separate

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up Donetick sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    _LOGGER.debug("Sensor platform received coordinator with data: %s", coordinator.data)

    if not coordinator.data:
        _LOGGER.warning("No data in coordinator for Donetick sensors. Skipping setup.")
        return

    sensors = []
    for chore_data in coordinator.data:
        # Ensure chore_data is a dictionary and has 'id' and 'name'
        if isinstance(chore_data, dict) and 'id' in chore_data and 'name' in chore_data:
            sensors.append(DonetickChoreSensor(coordinator, chore_data))
            _LOGGER.debug("Created DonetickChoreSensor for chore: %s", chore_data.get('name'))
        else:
            _LOGGER.warning("Skipping chore due to missing 'id' or 'name', or incorrect format: %s", chore_data)

    if sensors:
        async_add_entities(sensors, True)
        _LOGGER.debug("Added %s Donetick sensors to Home Assistant.", len(sensors))
    else:
        _LOGGER.warning("No Donetick sensors were created.")


class DonetickChoreSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, chore_data):
        super().__init__(coordinator)
        self._chore_data = chore_data  # Store the specific chore data for this sensor
        self._chore_id = chore_data["id"] # Keep for easier access

        self._attr_name = chore_data["name"].strip()
        self._attr_unique_id = f"{DOMAIN}_chore_{self._chore_id}" # Ensure DOMAIN is used for uniqueness
        self._attr_has_entity_name = True # Use if the entity name is the "name" attribute

        # Configure device info to link to the coordinator or a common device
        # Using chore_data['id'] to make each chore a "device" or identifiable part
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(self._chore_id))}, # Use string for identifier part
            name=f"Donetick Chore: {chore_data['name']}", # More specific name for the device
            manufacturer="Donetick",
            model="Chore Sensor",
            # Link to the coordinator's device if the coordinator has one
            # via_device=(DOMAIN, self.coordinator.config_entry.entry_id) # Example if coordinator has a device
        )

    @property
    def _current_chore_data(self):
        """Helper to get the current chore data from the coordinator."""
        if self.coordinator.data:
            for chore in self.coordinator.data:
                if chore.get("id") == self._chore_id:
                    return chore
        return None # Or self._chore_data as fallback if preferred

    @property
    def native_value(self):
        """Return the state of the sensor."""
        chore = self._current_chore_data
        if chore:
            # Example: Return the status of the chore. Adjust as per actual data structure.
            return "complete" if chore.get("status", 0) == 1 else "incomplete"
        return "unknown" # Fallback state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        chore = self._current_chore_data
        if chore:
            return {
                "chore_id": chore["id"],
                "assigned_to": chore.get("assignedTo", "Unassigned"),
                "due_date": chore.get("dueDate"),
                "notes": chore.get("notes"),
                # Add any other attributes from 'chore' that are relevant
            }
        return {}

    # The 'available' property is inherited from CoordinatorEntity and works based on coordinator.last_update_success
    # The 'async_update' method is also handled by CoordinatorEntity.
    # No need for _update_state_from_chore as properties derive state directly.
