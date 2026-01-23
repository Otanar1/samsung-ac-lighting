from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import SamsungACCoordinator

CONF_DEVICE_NAME = "device_name"


async def async_setup_entry(hass, entry, add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    add_entities([SamsungACLightingSwitch(coordinator, entry)])


class SamsungACLightingSwitch(CoordinatorEntity, SwitchEntity):
    """Switch para controlar o LED do Ar Condicionado Samsung."""

    _attr_has_entity_name = True
    _attr_name = "LED"
    _attr_icon = "mdi:led-on"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._device_id = entry.data[CONF_DEVICE_ID]
        self._device_name = entry.data[CONF_DEVICE_NAME]
        self._attr_unique_id = f"{self._device_id}_lighting"

    @property
    def device_info(self) -> DeviceInfo:
        """Informações do dispositivo para o registro do HA."""
        data = self.coordinator.data or {}
        components = data.get("components", {})
        main = components.get("main", {})
        ocf = main.get("ocf", {})
        
        # Busca segura de dados (Safe Navigation)
        manufacturer = ocf.get("mnmn", {}).get("value", "Samsung Electronics")
        
        # Tenta pegar o modelo de vários lugares possíveis
        device_id_data = main.get("samsungce.deviceIdentification", {})
        model = device_id_data.get("description", {}).get("value")
        if not model:
            model = device_id_data.get("modelName", {}).get("value", "Samsung AC")
            
        sw_version = ocf.get("mnfv", {}).get("value")

        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer=manufacturer,
            model=model,
            sw_version=sw_version,
        )

    @property
    def is_on(self):
        """Retorna True se o LED estiver ligado."""
        # Se o coordinator falhou na última atualização, o entity fica 'unavailable'
        # automaticamente por herança da CoordinatorEntity.
        
        if not self.coordinator.data:
            return None
            
        try:
            # Navegação segura pelo JSON complexo
            return (
                self.coordinator.data
                .get("components", {})
                .get("main", {})
                .get("samsungce.airConditionerLighting", {})
                .get("lighting", {})
                .get("value")
                == "on"
            )
        except (AttributeError, TypeError):
            # Se a estrutura mudar ou for inesperada
            return None

    async def async_turn_on(self, **kwargs):
        """Liga o LED."""
        await self.coordinator.api.set_lighting(
            self.coordinator.session,
            self._device_id,
            "on",
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Desliga o LED."""
        await self.coordinator.api.set_lighting(
            self.coordinator.session,
            self._device_id,
            "off",
        )
        await self.coordinator.async_request_refresh()