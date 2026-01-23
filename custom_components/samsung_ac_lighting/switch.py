from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import SamsungACCoordinator

CONF_DEVICE_NAME = "device_name"


async def async_setup_entry(hass, entry, add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    add_entities([
        SamsungACLightingSwitch(coordinator, entry)
    ])


class SamsungACLightingSwitch(CoordinatorEntity, SwitchEntity):
    # Isso garante que o ID seja gerado como switch.nome_do_dispositivo_led
    _attr_has_entity_name = True
    
    # O nome curto da entidade. Na UI aparecerá "Ar-condicionado da Sala Superior LED"
    _attr_name = "LED"
    
    _attr_icon = "mdi:led-on"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)

        self._device_id = entry.data[CONF_DEVICE_ID]
        self._device_name = entry.data[CONF_DEVICE_NAME]
        
        # Unique ID garante que você possa editar a entidade na UI, mas não define o entity_id
        self._attr_unique_id = f"{self._device_id}_lighting"

    @property
    def device_info(self) -> DeviceInfo:
        """Informações baseadas no seu RAW data."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name, # "Ar-condicionado da Sala Superior" 
            manufacturer="Samsung Electronics", # 
            # Pegando o modelo exato do RAW data
            model="TP1X_DA-AC-RAC-01001", # [cite: 6]
            # Opcional: Versão do firmware
            sw_version="ARA-WW-TP1-24-ARXX00_11240611", # [cite: 3]
        )

    @property
    def is_on(self):
        try:
            # Caminho verificado no RAW: components -> main -> samsungce.airConditionerLighting -> lighting -> value [cite: 95, 96]
            return (
                self.coordinator.data["components"]["main"]
                ["samsungce.airConditionerLighting"]
                ["lighting"]["value"]
                == "on"
            )
        except (KeyError, TypeError):
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