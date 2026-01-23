import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_TOKEN, CONF_DEVICE_ID

from .api import SmartThingsAPI


async def async_setup_entry(hass, entry, add_entities):
    token = entry.data[CONF_TOKEN]
    device_id = entry.data[CONF_DEVICE_ID]

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
    def unique_id(self):
        return f"{self._device_id}_lighting"

    @property
    def is_on(self):
        return self._is_on

    async def async_update(self):
        """
        Atualiza o estado lendo o endpoint:
        GET /devices/{deviceId}/status
        """
        try:
            data = await self._api.get_device(self._session, self._device_id)

            lighting = (
                data["components"]["main"]
                ["samsungce.airConditionerLighting"]
                ["lighting"]["value"]
            )

            self._is_on = lighting == "on"

        except KeyError:
            # Capability não disponível ou estrutura inesperada
            self._is_on = None

        except Exception:
            # Erro de rede / API
            self._is_on = None

    async def async_turn_on(self, **kwargs):
        await self._api.set_lighting(self._session, self._device_id, "on")
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        await self._api.set_lighting(self._session, self._device_id, "off")
        self._is_on = False
