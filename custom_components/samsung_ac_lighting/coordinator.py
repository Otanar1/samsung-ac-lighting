from datetime import timedelta
import logging
import asyncio
import time

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import SmartThingsAPI

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
        
        # --- Variáveis de Configuração (Controladas pelas Entidades) ---
        self.auto_led_enabled = False # Padrão Desligado
        self.auto_led_delay = 60      # Padrão 60s
        # --------------------------------------------------------------

        # Variável para controlar o timer do LED
        self._led_on_start_time = None

    async def _async_update_data(self):
        try:
            data = await self.api.get_device(self.session, self.device_id)
            await self._check_auto_led_off(data)
            return data
        except Exception as err:
            raise UpdateFailed(f"Erro ao buscar estado do ar-condicionado: {err}")

    async def _check_auto_led_off(self, data):
        """Verifica se deve desligar o LED baseado no tempo."""
        # 1. Verifica se a funcionalidade está ativada na variável do coordinator
        if not self.auto_led_enabled:
            self._led_on_start_time = None
            return

        try:
            # Pega estados com segurança
            main = data.get("components", {}).get("main", {})
            
            led_state = main.get("samsungce.airConditionerLighting", {}).get("lighting", {}).get("value")
            ac_state = main.get("switch", {}).get("switch", {}).get("value")

            # LÓGICA DO TIMER
            if ac_state == "on" and led_state == "on":
                if self._led_on_start_time is None:
                    self._led_on_start_time = time.monotonic()
                    _LOGGER.debug("Auto LED: Timer iniciado.")
                else:
                    elapsed = time.monotonic() - self._led_on_start_time
                    # Usa o delay configurado na variável
                    if elapsed >= self.auto_led_delay:
                        _LOGGER.debug(f"Auto LED: {elapsed:.1f}s > {self.auto_led_delay}s. Desligando...")
                        asyncio.create_task(self.async_send_lighting_command("off"))
                        self._led_on_start_time = None 
            else:
                self._led_on_start_time = None

        except Exception as e:
            _LOGGER.warning(f"Erro na lógica Auto LED Off: {e}")

    async def async_send_lighting_command(self, value: str):
        async with self._command_lock:
            now = time.monotonic()
            if now - self._last_command_ts < COMMAND_COOLDOWN:
                return
            await self.api.set_lighting(self.session, self.device_id, value)
            self._last_command_ts = now