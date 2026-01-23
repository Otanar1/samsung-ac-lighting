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
        """Retorna informações dinâmicas do dispositivo."""
        
        # Tenta pegar os dados do coordinator (cache da API)
        # Estrutura baseada no RAW.txt enviado
        data = self.coordinator.data or {}
        components = data.get("components", {})
        main = components.get("main", {})

        # Tenta buscar Fabricante (ocf -> mnmn)
        manufacturer = (
            main.get("ocf", {})
            .get("mnmn", {})
            .get("value", "Samsung") # Valor padrão se falhar
        )

        # Tenta buscar Modelo. 
        # No seu RAW, 'modelName' é null, então usamos 'description' como principal
        device_id_data = main.get("samsungce.deviceIdentification", {})
        model = device_id_data.get("description", {}).get("value")
        
        if not model:
            # Fallback se description também for nulo
            model = device_id_data.get("modelName", {}).get("value", "Samsung AC")

        # Tenta buscar Firmware (ocf -> mnfv)
        sw_version = (
            main.get("ocf", {})
            .get("mnfv", {})
            .get("value")
        )

        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer=manufacturer,
            model=model,
            sw_version=sw_version,
        )

    @property
    def is_on(self):
        try:
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