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