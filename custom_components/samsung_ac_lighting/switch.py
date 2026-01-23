from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    add_entities([SamsungACLightingSwitch(coordinator)])


class SamsungACLightingSwitch(CoordinatorEntity, SwitchEntity):
    _attr_name = "LED do Ar-condicionado Samsung"
    _attr_icon = "mdi:led-on"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def unique_id(self):
        return f"{self.coordinator.device_id}_lighting"

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
        await self.coordinator.async_send_lighting_command("on")

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_send_lighting_command("off")
