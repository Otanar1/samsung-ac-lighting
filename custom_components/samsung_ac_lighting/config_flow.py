from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_TOKEN, CONF_DEVICE_ID
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol
import logging

from .const import DOMAIN
from .api import SmartThingsAPI

CONF_DEVICE_NAME = "device_name"
CONF_DEVICE = "device"

_LOGGER = logging.getLogger(__name__)

class SamsungACLightingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 3

    async def async_step_user(self, user_input=None):
        return await self.async_step_token()

    def __init__(self):
        self._token = None
        self._devices = {}

    async def async_step_init(self, user_input=None):
        return await self.async_step_user()

    async def async_step_token(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._token = user_input[CONF_TOKEN]
            try:
                session = async_get_clientsession(self.hass)
                api = SmartThingsAPI(self._token)
                # Passamos session aqui conforme sua API pede
                devices = await api.get_devices(session)
                
                self._devices = {
                    d["deviceId"]: d["label"]
                    for d in devices
                    if d.get("ocf", {}).get("ocfDeviceType") == "oic.d.airconditioner"
                }
                if not self._devices:
                    errors["base"] = "no_devices"
                else:
                    return await self.async_step_select_device()
            except Exception:
                _LOGGER.exception("Erro ao conectar no SmartThings")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="token",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
            errors=errors,
        )

    async def async_step_select_device(self, user_input=None):
        if user_input is not None:
            device_id = user_input[CONF_DEVICE]
            device_name = self._devices[device_id]
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()
            
            # Mantemos a estrutura exata que seus outros arquivos esperam
            return self.async_create_entry(
                title=f"{device_name}", 
                data={
                    CONF_TOKEN: self._token,
                    CONF_DEVICE_ID: device_id,
                    CONF_DEVICE_NAME: device_name,
                },
            )
        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE): vol.In(self._devices)}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SamsungACOptionsFlowHandler(config_entry)


class SamsungACOptionsFlowHandler(config_entries.OptionsFlow):
    """Fluxo para alterar o Token sem reinstalar."""
    
    # NOTA: Não definimos __init__ aqui para evitar o erro "has no setter".
    # O Home Assistant injeta o config_entry automaticamente na classe pai.

    async def async_step_init(self, user_input=None):
        """Gerencia as opções (Troca de Token)."""
        errors = {}
        
        # Pega o token atual
        current_token = self.config_entry.data.get(CONF_TOKEN, "")

        if user_input is not None:
            new_token = user_input.get(CONF_TOKEN)
            
            # Valida o novo token
            session = async_get_clientsession(self.hass)
            api = SmartThingsAPI(new_token)
            
            try:
                await api.get_devices(session)
                token_valid = True
            except Exception:
                token_valid = False
            
            if not token_valid:
                errors["base"] = "cannot_connect"
            else:
                # Token Válido! 
                # Copiamos os dados antigos para NÃO perder o Device Name e ID
                new_data = self.config_entry.data.copy()
                new_data[CONF_TOKEN] = new_token
                
                # Atualiza a entrada
                self.hass.config_entries.async_update_entry(
                    self.config_entry, 
                    data=new_data
                )
                
                # Recarrega a integração
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN, default=current_token): str,
            }),
            errors=errors
        )