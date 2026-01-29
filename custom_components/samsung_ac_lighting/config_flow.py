import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_TOKEN, CONF_DEVICE_ID
from .api import SmartThingsAPI

class SamsungACConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Samsung AC Display Light."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            token = user_input[CONF_TOKEN]
            device_id = user_input.get(CONF_DEVICE_ID)

            # Valida o token e lista dispositivos
            api = SmartThingsAPI(token)
            devices = await api.get_devices()

            if not devices:
                errors["base"] = "auth_error"
            else:
                # Se o usuário não escolheu dispositivo ainda (primeira tela)
                if not device_id:
                    # Se só tem um ar-condicionado, seleciona automático
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
                    # Cria a entrada
                    await self.async_set_unique_id(device_id)
                    self._abort_if_unique_id_configured()
                    
                    # Pega o nome do dispositivo para usar no título
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
        # Reutiliza a lógica do step_user pois ele trata ambos os casos
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
        
        # Valor atual do token
        current_token = self.config_entry.data.get(CONF_TOKEN, "")

        if user_input is not None:
            new_token = user_input.get(CONF_TOKEN)
            
            # Testa o novo token
            api = SmartThingsAPI(new_token)
            devices = await api.get_devices()
            
            if not devices:
                errors["base"] = "auth_error"
            else:
                # Atualiza a entrada de configuração com o novo token
                # Nota: ID do dispositivo mantido, só trocamos a credencial
                new_data = self.config_entry.data.copy()
                new_data[CONF_TOKEN] = new_token
                
                self.hass.config_entries.async_update_entry(
                    self.config_entry, 
                    data=new_data
                )
                
                # Recarrega a integração para aplicar
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN, default=current_token): str,
            }),
            errors=errors
        )