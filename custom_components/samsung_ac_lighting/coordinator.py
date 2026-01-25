from datetime import timedelta
import logging
import asyncio
import time

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import SmartThingsAPI
from .const import CONF_AUTO_LED_OFF, CONF_AUTO_LED_OFF_DELAY

_LOGGER = logging.getLogger(__name__)

COMMAND_COOLDOWN = 2  # segundos


class SamsungACCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api: SmartThingsAPI, session, device_id, entry):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="Samsung AC Coordinator",
            update_interval=timedelta(seconds=15),
        )
        self.api = api
        self.session = session
        self.device_id = device_id
        self.entry = entry

        self._command_lock = asyncio.Lock()
        self._last_command_ts = 0.0
        
        # Variável para controlar o timer do LED
        # Armazena o timestamp (time.monotonic) de quando detectamos o LED ligado
        self._led_on_start_time = None

    async def _async_update_data(self):
        try:
            data = await self.api.get_device(self.session, self.device_id)
            
            # Executa a lógica do timer após pegar os dados
            await self._check_auto_led_off(data)
            
            return data
        except Exception as err:
            raise UpdateFailed(f"Erro ao buscar estado do ar-condicionado: {err}")

    async def _check_auto_led_off(self, data):
        """Verifica se deve desligar o LED baseado no tempo."""
        # 1. Verifica se a opção está ativada nas configurações
        if not self.entry.options.get(CONF_AUTO_LED_OFF, False):
            self._led_on_start_time = None # Reseta se a opção for desativada
            return

        try:
            # 2. Pega o estado do LED
            led_state = (
                data.get("components", {})
                .get("main", {})
                .get("samsungce.airConditionerLighting", {})
                .get("lighting", {})
                .get("value")
            )

            # 3. Pega o estado do Ar Condicionado
            ac_state = (
                data.get("components", {})
                .get("main", {})
                .get("switch", {})
                .get("switch", {})
                .get("value")
            )

            # LÓGICA DO TIMER
            # Só conta tempo se Ar estiver ON e LED estiver ON
            if ac_state == "on" and led_state == "on":
                if self._led_on_start_time is None:
                    # Começa a contar agora
                    self._led_on_start_time = time.monotonic()
                    _LOGGER.debug("Auto LED: Timer iniciado.")
                else:
                    # Já estava ligado, verifica quanto tempo passou
                    elapsed = time.monotonic() - self._led_on_start_time
                    delay_setting = self.entry.options.get(CONF_AUTO_LED_OFF_DELAY, 60)
                    
                    if elapsed >= delay_setting:
                        _LOGGER.debug(f"Auto LED: {elapsed:.1f}s passaram. Desligando LED.")
                        # Dispara o comando de desligar
                        asyncio.create_task(self.async_send_lighting_command("off"))
                        # Reseta o timer para não ficar mandando comando repetido
                        self._led_on_start_time = None 
            else:
                # Se o ar desligou ou o LED já desligou, reseta o timer
                if self._led_on_start_time is not None:
                    _LOGGER.debug("Auto LED: Timer cancelado (LED ou AC desligaram).")
                self._led_on_start_time = None

        except Exception as e:
            _LOGGER.warning(f"Erro na lógica Auto LED Off: {e}")

    async def async_send_lighting_command(self, value: str):
        async with self._command_lock:
            now = time.monotonic()
            if now - self._last_command_ts < COMMAND_COOLDOWN:
                _LOGGER.debug("Comando ignorado por debounce")
                return

            await self.api.set_lighting(
                self.session,
                self.device_id,
                value,
            )

            self._last_command_ts = now
            # Não pedimos refresh imediato para respeitar a lógica otimista do switch