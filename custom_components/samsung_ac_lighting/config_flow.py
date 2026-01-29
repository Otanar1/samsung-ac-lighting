import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession # <--- Verifique se esta linha está lá

from .const import DOMAIN, CONF_TOKEN, CONF_DEVICE_ID
from .api import SmartThingsAPI

_LOGGER = logging.getLogger(__name__)

class SamsungACConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Samsung AC Display Light."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            token = user_input[CONF_TOKEN]
            device_id = user_input.get(CONF_DEVICE_ID)

            # Pega a sessão de rede do Home Assistant
            session = async_get_clientsession(self.hass)
            
            # Valida o token e lista dispositivos
            api = SmartThingsAPI(token)
            
            try:
                # O ERRO ACONTECIA AQUI. Agora passamos (session)
                devices = await api.get_devices(session) 
            except Exception:
                _LOGGER.exception("Erro ao conectar na API SmartThings")
                errors["base"] = "auth_error"
                devices = None

            if not devices:
                if "base" not in errors:
                    errors["base"] = "auth_error"
            else:
                # Se o usuário não escolheu dispositivo ainda (primeira tela)
                if not device_id:
                    # Filtra apenas dispositivos que parecem Ar Condicionado
                    ac_devices = {d['deviceId']: d['label'] for d in devices}
                    
                    if not ac_devices:
                        errors["base"] = "no_devices"
                    else:
                        return self.async_show_form(
                            step_id="device",
                            data_schema=vol.Schema({
                                vol.Required(CONF_TOKEN, default=token): str,
                                vol.Required(CONF_DEVICE_ID): vol.In(ac_devices)
                            }),
                            errors=errors
                        )
                else:
                    # Usuário já escolheu o dispositivo e token está ok
                    await self.async_set_unique_id(device_id)
                    self._abort_if_unique_id_configured()
                    
                    device_name = next((d['label'] for d in devices if d['deviceId'] == device_id), "Samsung AC")
                    
                    return self.async_create_entry(
                        title=device_name,
                        data={
                            CONF_TOKEN: token,
                            CONF_DEVICE_ID: device_id
                        }
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN): str
            }),
            errors=errors
        )

    async def async_step_device(self, user_input=None):
        """Segunda etapa: confirmar dispositivo se necessário."""
        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SamsungACOptionsFlowHandler(config_entry)


class SamsungACOptionsFlowHandler(config_entries.OptionsFlow):
    """Permite alterar o Token sem reinstalar."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Gerencia as opções."""
        errors = {}
        
        current_token = self.config_entry.data.get(CONF_TOKEN, "")

        if user_input is not None:
            new_token = user_input.get(CONF_TOKEN)
            
            session = async_get_clientsession(self.hass)
            api = SmartThingsAPI(new_token)
            
            try:
                # Passamos a session aqui também
                devices = await api.get_devices(session)
            except Exception:
                devices = None
            
            if not devices:
                errors["base"] = "auth_error"
            else:
                # Atualiza o token mantendo o resto
                new_data = self.config_entry.data.copy()
                new_data[CONF_TOKEN] = new_token
                
                self.hass.config_entries.async_update_entry(
                    self.config_entry, 
                    data=new_data
                )
                
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN, default=current_token): str,
            }),
            errors=errors
        )