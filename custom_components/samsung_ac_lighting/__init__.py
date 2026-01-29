import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv

from .api import SmartThingsAPI
from .coordinator import SamsungACCoordinator
from .const import DOMAIN, CONF_TOKEN, CONF_DEVICE_ID

# Define que a config é feita apenas via UI (Config Flow)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = ["switch", "select"]

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    token = entry.data[CONF_TOKEN]
    device_id = entry.data[CONF_DEVICE_ID]

    api = SmartThingsAPI(token)
    session = aiohttp.ClientSession()

    coordinator = SamsungACCoordinator(
        hass=hass,
        api=api,
        session=session,
        device_id=device_id,
        entry=entry
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        # Não impedimos o setup se falhar na primeira vez, apenas logamos
        # Isso ajuda se a internet cair, a integração tenta de novo depois
        await session.close()
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Adiciona o ouvinte para atualizações (Troca de token via botão Configurar)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if entry.entry_id in hass.data[DOMAIN]:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        if coordinator.session:
            await coordinator.session.close()
            
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Recarrega a integração quando as opções mudam."""
    await hass.config_entries.async_reload(entry.entry_id)