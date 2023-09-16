from homeassistant.components.switch import SwitchEntity

import requests
import hashlib
import json

def get_session_id(username: str, password: str):
    login_url = "https://apiieu.guardingvision.com/api/user/login"

    login_form = {
        "account": username,
        "password": hashlib.md5(password.encode()).hexdigest(),
        "areaId": "111",
        "clientType": "178",
    }

    response = requests.post(login_url, params=login_form)
    return response.json()["loginResp"]["sessionId"]

def get_locks(session_id: str):
    data = {
        'cmdId': '19713',
        'sessionId': session_id,
        'subSerial': 'L15446055',
        'transmissionData': 'GET /ISAPI/Custom/VideoIntercom/locksParams?format=json\r\n',
    }

    response = requests.post('https://apiieu.guardingvision.com/api/device/isapi', data=data)
    
    # check if resultCode is 0
    if response.json()['resultCode'] != '0':
        raise Exception('Error while getting locks')
    
    lock_summary = [(lock['lockId'], lock['lockName']) for lock in json.loads(response.json()["data"]) if lock["enable"]]
    return lock_summary

def lock_action(session_id: str, lock_id: int):
    data = {
        'cmdId': '19713',
        'sessionId': session_id,
        'subSerial': 'L15446055',
        'transmissionData': 'PUT /ISAPI/Custom/VideoIntercom/unlock?format=json\r\n{\n  "lockId" : ' + str(lock_id) + '\n}',
    }

    response = requests.post('https://apiieu.guardingvision.com/api/device/isapi', data=data)

async def async_setup_entry(hass, config_entry, async_add_entities):
    email = config_entry.data["email"]
    password = config_entry.data["password"]

    session_id = get_session_id(email, password)
    locks = get_locks(session_id)

    async_add_entities([GuardingVisionSwitch(session_id, lock) for lock in locks], True)

class GuardingVisionSwitch(SwitchEntity):
    def __init__(self, session_id, lock):
        self._session_id = session_id
        self._lock = lock

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

    def turn_on(self, **kwargs):
        lock_action(self._session_id, self._lock[0])

    def turn_off(self, **kwargs):
        lock_action(self._session_id, self._lock[0])
