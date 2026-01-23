import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_TOKEN, CONF_DEVICE_ID

from .const import DOMAIN
from .api import SmartThingsAPI

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info=None,
):
    token = config.get(CONF_TOKEN)
    device_id = config.get(CONF_DEVICE_ID)

    api = SmartThingsAPI(token)
    session = aiohttp.ClientSession()

    add_entities([SamsungACLightingSwitch(api, session, device_id)])


class SamsungACLightingSwitch(SwitchEntity):
    _attr_name = "LED do Ar-condicionado Samsung"
    _attr_icon = "mdi:led-on"

    def __init__(self, api, session, device_id):
        self._api = api
        self._session = session
        self._device_id = device_id
        self._is_on = None

    @property
    def is_on(self):
        return self._is_on

    async def async_update(self):
        data = await self._api.get_device(self._session, self._device_id)

        for component in data.get("components", []):
            if component.get("id") != "main":
                continue

            for cap in component.get("capabilities", []):
                if cap.get("id") == "samsungce.airConditionerLighting":
                    status = cap.get("status", {})
                    lighting = status.get("lighting", {})
                    value = lighting.get("value")

                    if value in ("on", "off"):
                        self._is_on = value == "on"
                    else:
                        self._is_on = None
                    return

        self._is_on = None

    async def async_turn_on(self, **kwargs):
        await self._api.set_lighting(self._session, self._device_id, "on")
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        await self._api.set_lighting(self._session, self._device_id, "off")
        self._is_on = False
