from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.const import CONF_DEVICE_ID

from .const import DOMAIN

CONF_DEVICE_NAME = "device_name"

async def async_setup_entry(hass, entry, add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    add_entities([SamsungACAutoLedDelaySelect(coordinator, entry)])

class SamsungACAutoLedDelaySelect(CoordinatorEntity, SelectEntity, RestoreEntity):
    """Seletor para escolher o tempo de espera do LED."""
    _attr_has_entity_name = True
    _attr_name = "Tempo Auto Off"
    _attr_icon = "mdi:timer-outline"
    _attr_options = ["5s", "15s", "30s", "60s", "120s"] # Opções disponíveis

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._device_id = entry.data[CONF_DEVICE_ID]
        self._device_name = entry.data[CONF_DEVICE_NAME]
        self._attr_unique_id = f"{self._device_id}_config_delay"

    @property
    def device_info(self) -> DeviceInfo:
        # Recriando helper simplificado para não precisar importar do switch
        # Idealmente o helper ficaria no coordinator, mas vamos duplicar pra manter simples agora
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name
        )

    @property
    def current_option(self):
        # Converte o número (60) para texto ("60s") para exibir
        return f"{self.coordinator.auto_led_delay}s"

    async def async_added_to_hass(self):
        """Restaura o valor selecionado após reinício."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state in self._attr_options:
            # Restaura a variável do coordinator
            seconds = int(last_state.state.replace("s", ""))
            self.coordinator.auto_led_delay = seconds

    async def async_select_option(self, option: str) -> None:
        """Chamado quando o usuário escolhe uma opção."""
        seconds = int(option.replace("s", ""))
        self.coordinator.auto_led_delay = seconds
        self.async_write_ha_state()