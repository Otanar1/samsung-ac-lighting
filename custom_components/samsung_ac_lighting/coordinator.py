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
    def __init__(self, hass, api: SmartThingsAPI, session, device_id):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="Samsung AC Coordinator",
            update_interval=timedelta(seconds=30),
        )
        self.api = api
        self.session = session
        self.device_id = device_id

        self._command_lock = asyncio.Lock()
        self._last_command_ts = 0.0

    async def _async_update_data(self):
        try:
            return await self.api.get_device(self.session, self.device_id)
        except Exception as err:
            raise UpdateFailed(f"Erro ao buscar estado do ar-condicionado: {err}")

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
            await self.async_request_refresh()
