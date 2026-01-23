from homeassistant import config_entries
from homeassistant.const import CONF_TOKEN, CONF_DEVICE_ID
import voluptuous as vol
import aiohttp

from .const import DOMAIN
from .api import SmartThingsAPI

CONF_DEVICE_NAME = "device_name"
CONF_DEVICE = "device"



class SamsungACLightingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._token = None
        self._devices = {}

    async def async_step_init(self, user_input=None):
        return await self.async_step_user()


    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            self._token = user_input[CONF_TOKEN]

            try:
                async with aiohttp.ClientSession() as session:
                    api = SmartThingsAPI(self._token)
                    devices = await api.get_devices(session)

                self._devices = {
                    d["deviceId"]: d["label"]
                    for d in devices
                    if d.get("ocf", {}).get("ocfDeviceType") == "oic.d.airconditioner"
                }

                if not self._devices:
                    errors["base"] = "no_devices"
                else:
                    return await self.async_step_device()

            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICE): vol.In(self._devices),
            }),
            description_placeholders={
                "device_label": "Dispositivo"
            },
            errors=errors,
        )

    async def async_step_device(self, user_input=None):
        if user_input is not None:
            device_id = user_input[CONF_DEVICE]
            device_name = self._devices[device_id]


            return self.async_create_entry(
                title=f"{device_name} LED",
                data={
                    CONF_TOKEN: self._token,
                    CONF_DEVICE_ID: device_id,
                    CONF_DEVICE_NAME: device_name,
                },
            )

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_DEVICE,
                    description={"name": "Dispositivo"}
                ): vol.In(self._devices),
            }),
        )

