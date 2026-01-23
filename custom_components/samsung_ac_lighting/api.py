import aiohttp
from .const import SMARTTHINGS_API_BASE

class SmartThingsAPI:
    def __init__(self, token):
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get_device(self, session, device_id):
        url = f"{SMARTTHINGS_API_BASE}/devices/{device_id}"
        async with session.get(url, headers=self._headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def set_lighting(self, session, device_id, state):
        url = f"{SMARTTHINGS_API_BASE}/devices/{device_id}/commands"
        payload = {
            "commands": [
                {
                    "component": "main",
                    "capability": "samsungce.airConditionerLighting",
                    "command": "setLighting",
                    "arguments": [state],
                }
            ]
        }
        async with session.post(url, headers=self._headers, json=payload) as resp:
            resp.raise_for_status()
