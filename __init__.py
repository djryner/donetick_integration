from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict):
    # We only support config entries, no YAML config
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Donetick from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api_url": entry.data["api_url"],
        "api_token": entry.data["api_token"],
        "name": entry.data.get("name"),
    }

    # Forward setup to both sensor and button platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "button"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in ["sensor", "button"]
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
