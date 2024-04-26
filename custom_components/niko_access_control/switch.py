from homeassistant.components.switch import SwitchEntity

import aiohttp
import asyncio
import async_timeout
import hashlib
import json


async def async_get_session_id(username: str, password: str):
    login_url = "https://apiieu.guardingvision.com/api/user/login"

    login_form = {
        "account": username,
        "password": hashlib.md5(password.encode()).hexdigest(),
        "areaId": "111",
        "clientType": "178",
    }

    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.post(login_url, params=login_form) as response:
                data = await response.json()
                return data["loginResp"]["sessionId"]


async def async_get_locks(session_id: str):
    data = {
        "cmdId": "19713",
        "sessionId": session_id,
        "subSerial": "L15446055",
        "transmissionData": "GET /ISAPI/Custom/VideoIntercom/locksParams?format=json\r\n",
    }

    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.post(
                "https://apiieu.guardingvision.com/api/device/isapi", data=data
            ) as response:
                resp_json = await response.json()
                if resp_json["resultCode"] != "0":
                    raise Exception("Error while getting locks")

                lock_summary = [
                    (lock["lockId"], lock["lockName"])
                    for lock in json.loads(resp_json["data"])
                    if lock["enable"]
                ]
                return lock_summary


async def async_lock_action(session_id: str, lock_id: int):
    data = {
        "cmdId": "19713",
        "sessionId": session_id,
        "subSerial": "L15446055",
        "transmissionData": f'PUT /ISAPI/Custom/VideoIntercom/unlock?format=json\r\n{{\n  "lockId" : {lock_id}\n}}',
    }

    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.post(
                "https://apiieu.guardingvision.com/api/device/isapi", data=data
            ) as response:
                # Here you can add more error handling based on the response if you want
                return await response.json()


async def async_setup_entry(hass, config_entry, async_add_entities):
    email = config_entry.data["email"]
    password = config_entry.data["password"]

    session_id = await async_get_session_id(email, password)
    locks = await async_get_locks(session_id)

    entities = [GuardingVisionSwitch(lock, config_entry) for lock in locks]
    async_add_entities(entities, True)


class GuardingVisionSwitch(SwitchEntity):
    def __init__(self, lock, config_entry):
        self._lock = lock
        self._config_entry = config_entry

    @property
    def name(self):
        return f"Niko_AC_{self._lock[1]}"

    @property
    def unique_id(self):
        return f"niko_ac_{self._lock[0]}"

    @property
    def is_on(self):
        return None  # No state available

    @property
    def assumed_state(self):
        return True  # Indicate that the state is assumed, not definite

    async def async_turn_on(self, **kwargs):
        session_id = await async_get_session_id(
            self._config_entry.data["email"], self._config_entry.data["password"]
        )
        await async_lock_action(session_id, self._lock[0])

    async def async_turn_off(self, **kwargs):
        session_id = await async_get_session_id(
            self._config_entry.data["email"], self._config_entry.data["password"]
        )
        await async_lock_action(session_id, self._lock[0])
