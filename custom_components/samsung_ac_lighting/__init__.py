import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import SmartThingsAPI
from .coordinator import SamsungACCoordinator
from .const import DOMAIN, CONF_TOKEN, CONF_DEVICE_ID

PLATFORMS = ["switch"]


async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    token = entry.data[CONF_TOKEN]
    device_id = entry.data[CONF_DEVICE_ID]

    api = SmartThingsAPI(token)
    session = aiohttp.ClientSession()

    coordinator = SamsungACCoordinator(
        hass=hass,
        api=api,
        session=session,
        device_id=device_id,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = hass.data[DOMAIN].pop(entry.entry_id)

    await coordinator.session.close()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
