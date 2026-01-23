from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import SmartThingsAPI


class SamsungACCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api: SmartThingsAPI, session, device_id):
        super().__init__(
            hass,
            logger=None,
            name="Samsung AC Coordinator",
            update_interval=timedelta(seconds=30),
        )
        self.api = api
        self.session = session
        self.device_id = device_id

    async def _async_update_data(self):
        try:
            return await self.api.get_device(self.session, self.device_id)
        except Exception as err:
            raise UpdateFailed(f"Erro ao buscar estado do ar-condicionado: {err}")

