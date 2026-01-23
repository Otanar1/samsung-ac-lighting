from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SamsungACCoordinator

CONF_DEVICE_NAME = "device_name"


async def async_setup_entry(hass, entry, add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    add_entities([
        SamsungACLightingSwitch(coordinator, entry)
    ])


class SamsungACLightingSwitch(CoordinatorEntity, SwitchEntity):
    _attr_icon = "mdi:led-on"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)

        self._device_id = entry.data[CONF_DEVICE_ID]
        self._device_name = entry.data[CONF_DEVICE_NAME]

        self._attr_name = f"{self._device_name} LED"
        self._attr_unique_id = f"{self._device_id}_lighting"

    @property
    def is_on(self):
        try:
            return (
                self.coordinator.data["components"]["main"]
                ["samsungce.airConditionerLighting"]
                ["lighting"]["value"]
                == "on"
            )
        except KeyError:
            return None

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_lighting(
            self.coordinator.session,
            self._device_id,
            "on",
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_lighting(
            self.coordinator.session,
            self._device_id,
            "off",
        )
        await self.coordinator.async_request_refresh()
