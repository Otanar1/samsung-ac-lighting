import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_TOKEN, CONF_DEVICE_ID

from .api import SmartThingsAPI
from .coordinator import SamsungACCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity



async def async_setup_entry(hass, entry, add_entities):
    token = entry.data[CONF_TOKEN]
    device_id = entry.data[CONF_DEVICE_ID]

    api = SmartThingsAPI(token)
    session = aiohttp.ClientSession()

    coordinator = SamsungACCoordinator(hass, api, session, device_id)
    await coordinator.async_config_entry_first_refresh()

    add_entities([SamsungACLightingSwitch(coordinator)])

class SamsungACLightingSwitch(CoordinatorEntity, SwitchEntity):
    _attr_name = "LED do Ar-condicionado Samsung"
    _attr_icon = "mdi:led-on"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._coordinator = coordinator

    @property
    def unique_id(self):
        return f"{self._coordinator.device_id}_lighting"

    @property
    def is_on(self):
        try:
            lighting = (
                self.coordinator.data["components"]["main"]
                ["samsungce.airConditionerLighting"]
                ["lighting"]["value"]
            )
            return lighting == "on"
        except KeyError:
            return None

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_lighting(
            self.coordinator.session,
            self.coordinator.device_id,
            "on",
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_lighting(
            self.coordinator.session,
            self.coordinator.device_id,
            "off",
        )
        await self.coordinator.async_request_refresh()
