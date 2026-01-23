import aiohttp
from .const import SMARTTHINGS_API_BASE

class SmartThingsAPI:
    def __init__(self, token):
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get_device(self, session, device_id):
        url = f"{SMARTTHINGS_API_BASE}/devices/{device_id}/status"
        async with session.get(url, headers=self._headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_devices(self, session):
        url = f"{SMARTTHINGS_API_BASE}/devices"
        async with session.get(url, headers=self._headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get("items", [])

    async def set_lighting(self, session, device_id, state):
        url = f"{SMARTTHINGS_API_BASE}/devices/{device_id}/commands"

        if state == "off":
            options = ["Light_On"]
        else:
            options = ["Light_Off"]

        payload = {
            "commands": [
                {
                    "component": "main",
                    "capability": "execute",
                    "command": "execute",
                    "arguments": [
                        "mode/vs/0",
                        {"x.com.samsung.da.options": options}
                    ]
                }
            ]
        }

        async with session.post(url, headers=self._headers, json=payload) as resp:
            resp.raise_for_status()

    async def set_auto_clean(self, session, device_id, state):
        url = f"{SMARTTHINGS_API_BASE}/devices/{device_id}/commands"
        # O comando na API da Samsung para isso costuma ser setAutoCleaningMode
        mode = "on" if state == "on" else "off"
        
        payload = {
            "commands": [
                {
                    "component": "main",
                    "capability": "custom.autoCleaningMode",
                    "command": "setAutoCleaningMode",
                    "arguments": [mode]
                }
            ]
        }
        async with session.post(url, headers=self._headers, json=payload) as resp:
            resp.raise_for_status()


