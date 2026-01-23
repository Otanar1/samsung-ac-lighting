from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
import logging

from .const import DOMAIN
from .coordinator import SamsungACCoordinator

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_NAME = "device_name"

async def async_setup_entry(hass, entry, add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    add_entities([
        SamsungACLightingSwitch(coordinator, entry),
        SamsungACAutoCleanSwitch(coordinator, entry)
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
        return _get_device_info_helper(self.coordinator, self._device_id, self._device_name)

    @property
    def is_on(self):
        try:
            return (
                self.coordinator.data["components"]["main"]
                ["samsungce.airConditionerLighting"]
                ["lighting"]["value"]
                == "on"
            )
        except (KeyError, TypeError, AttributeError):
            return None

    async def async_turn_on(self, **kwargs):
        # 1. Otimista: Tenta atualizar visualmente na hora
        try:
            self.coordinator.data["components"]["main"]["samsungce.airConditionerLighting"]["lighting"]["value"] = "on"
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.warning(f"Erro na atualização otimista do LED: {e}")

        # 2. Comando Real
        await self.coordinator.api.set_lighting(self.coordinator.session, self._device_id, "on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        # 1. Otimista
        try:
            self.coordinator.data["components"]["main"]["samsungce.airConditionerLighting"]["lighting"]["value"] = "off"
            self.async_write_ha_state()
        except Exception as e:
             _LOGGER.warning(f"Erro na atualização otimista do LED: {e}")

        # 2. Comando Real
        await self.coordinator.api.set_lighting(self.coordinator.session, self._device_id, "off")
        await self.coordinator.async_request_refresh()


class SamsungACAutoCleanSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Auto Clean"
    _attr_icon = "mdi:fan-auto"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._device_id = entry.data[CONF_DEVICE_ID]
        self._device_name = entry.data[CONF_DEVICE_NAME]
        self._attr_unique_id = f"{self._device_id}_auto_clean"

    @property
    def device_info(self) -> DeviceInfo:
        # CORREÇÃO: Usando a função helper para não quebrar o código
        return _get_device_info_helper(self.coordinator, self._device_id, self._device_name)

    @property
    def is_on(self):
        try:
            return (
                self.coordinator.data["components"]["main"]
                ["custom.autoCleaningMode"]
                ["autoCleaningMode"]["value"]
                == "on"
            )
        except (KeyError, TypeError, AttributeError):
            return None

    async def async_turn_on(self, **kwargs):
        # Otimista
        try:
            self.coordinator.data["components"]["main"]["custom.autoCleaningMode"]["autoCleaningMode"]["value"] = "on"
            self.async_write_ha_state()
        except Exception:
            pass

        await self.coordinator.api.set_auto_clean(self.coordinator.session, self._device_id, "on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        # Otimista
        try:
            self.coordinator.data["components"]["main"]["custom.autoCleaningMode"]["autoCleaningMode"]["value"] = "off"
            self.async_write_ha_state()
        except Exception:
            pass

        await self.coordinator.api.set_auto_clean(self.coordinator.session, self._device_id, "off")
        await self.coordinator.async_request_refresh()

# Helper para evitar duplicação de código e erros
def _get_device_info_helper(coordinator, device_id, device_name):
    data = coordinator.data or {}
    components = data.get("components", {})
    main = components.get("main", {})
    ocf = main.get("ocf", {})
    
    manufacturer = ocf.get("mnmn", {}).get("value", "Samsung Electronics")
    
    device_id_data = main.get("samsungce.deviceIdentification", {})
    model = device_id_data.get("description", {}).get("value")
    if not model:
        model = device_id_data.get("modelName", {}).get("value", "Samsung AC")
        
    sw_version = ocf.get("mnfv", {}).get("value")

    return DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=device_name,
        manufacturer=manufacturer,
        model=model,
        sw_version=sw_version,
    )