from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
import aiohttp

from .const import DOMAIN, CONF_TOKEN, CONF_DEVICE_ID
from .api import SmartThingsAPI

class SamsungACLightingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._token = None
        self._devices = {}

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
                errors["base"] = "auth_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TOKEN): str,
                }
            ),
            errors=errors,
        )

    async def async_step_device(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Samsung AC Display Light",
                data={
                    CONF_TOKEN: self._token,
                    CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                },
            )

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_ID): vol.In(self._devices),
                }
            ),
        )
