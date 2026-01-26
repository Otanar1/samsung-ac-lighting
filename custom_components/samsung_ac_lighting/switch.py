from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity # Importante para salvar estado
import logging

from .const import DOMAIN
from .coordinator import SamsungACCoordinator

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_NAME = "device_name"

async def async_setup_entry(hass, entry, add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    add_entities([
        SamsungACLightingSwitch(coordinator, entry),
        SamsungACAutoCleanSwitch(coordinator, entry),
        SamsungACAutoLedEnableSwitch(coordinator, entry) # <-- Novo Switch de Config
    ])

# ... (Mantenha as classes SamsungACLightingSwitch e SamsungACAutoCleanSwitch IGUAIS a antes) ...
# ... Copie as classes SamsungACLightingSwitch e SamsungACAutoCleanSwitch do código anterior ...
# ... Vou colocar apenas a NOVA classe abaixo para economizar espaço, mas você deve manter as outras ...

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
            return (self.coordinator.data["components"]["main"]["samsungce.airConditionerLighting"]["lighting"]["value"] == "on")
        except (KeyError, TypeError, AttributeError): return None
    async def async_turn_on(self, **kwargs):
        try:
            self.coordinator.data["components"]["main"]["samsungce.airConditionerLighting"]["lighting"]["value"] = "on"
            self.async_write_ha_state()
        except Exception: pass
        await self.coordinator.api.set_lighting(self.coordinator.session, self._device_id, "on")
    async def async_turn_off(self, **kwargs):
        try:
            self.coordinator.data["components"]["main"]["samsungce.airConditionerLighting"]["lighting"]["value"] = "off"
            self.async_write_ha_state()
        except Exception: pass
        await self.coordinator.api.set_lighting(self.coordinator.session, self._device_id, "off")

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
        return _get_device_info_helper(self.coordinator, self._device_id, self._device_name)
    @property
    def is_on(self):
        try:
            return (self.coordinator.data["components"]["main"]["custom.autoCleaningMode"]["autoCleaningMode"]["value"] == "on")
        except (KeyError, TypeError, AttributeError): return None
    async def async_turn_on(self, **kwargs):
        try:
            self.coordinator.data["components"]["main"]["custom.autoCleaningMode"]["autoCleaningMode"]["value"] = "on"
            self.async_write_ha_state()
        except Exception: pass
        await self.coordinator.api.set_auto_clean(self.coordinator.session, self._device_id, "on")
    async def async_turn_off(self, **kwargs):
        try:
            self.coordinator.data["components"]["main"]["custom.autoCleaningMode"]["autoCleaningMode"]["value"] = "off"
            self.async_write_ha_state()
        except Exception: pass
        await self.coordinator.api.set_auto_clean(self.coordinator.session, self._device_id, "off")


# --- NOVA CLASSE ---
class SamsungACAutoLedEnableSwitch(CoordinatorEntity, SwitchEntity, RestoreEntity):
    """Switch virtual para ativar/desativar a lógica de apagar LED."""
    _attr_has_entity_name = True
    _attr_name = "Auto LED Off"
    _attr_icon = "mdi:eye-off-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._device_id = entry.data[CONF_DEVICE_ID]
        self._device_name = entry.data[CONF_DEVICE_NAME]
        self._attr_unique_id = f"{self._device_id}_config_auto_led"

    @property
    def device_info(self) -> DeviceInfo:
        return _get_device_info_helper(self.coordinator, self._device_id, self._device_name)

    @property
    def is_on(self):
        # Lê direto da variável do coordinator
        return self.coordinator.auto_led_enabled

    async def async_added_to_hass(self):
        """Restaura o estado anterior ao reiniciar o HA."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            # Restaura a variável do coordinator
            is_enabled = last_state.state == "on"
            self.coordinator.auto_led_enabled = is_enabled

    async def async_turn_on(self, **kwargs):
        self.coordinator.auto_led_enabled = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self.coordinator.auto_led_enabled = False
        self.async_write_ha_state()

def _get_device_info_helper(coordinator, device_id, device_name):
    data = coordinator.data or {}
    components = data.get("components", {})
    main = components.get("main", {})
    ocf = main.get("ocf", {})
    manufacturer = ocf.get("mnmn", {}).get("value", "Samsung Electronics")
    device_id_data = main.get("samsungce.deviceIdentification", {})
    model = device_id_data.get("description", {}).get("value") or device_id_data.get("modelName", {}).get("value", "Samsung AC")
    sw_version = ocf.get("mnfv", {}).get("value")
    return DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=device_name,
        manufacturer=manufacturer,
        model=model,
        sw_version=sw_version,
    )