#连接TGFW

import requests
import base64
import json, time, copy


class TGFW:
    def __init__(self, ip, username, password, port=443):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.token = None

    def construct_url(self, uri):
        return f'https://{self.ip}:{self.port}{uri}'
    
    def request(self, method, url, **kwargs):
        method = getattr(requests, method.lower())
        response = method(self.construct_url(url), 
                          verify=False, 
                          **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response
        
    def get_token(self):
        #获取设备的token
        data = json.dumps({
            "id": self.username,
            "val": {
            "username": self.username,
            "passwd": base64.b64encode(self.password.encode('utf-8')).decode('utf-8'),
            "action": "login",
            "autht": 0,
            "code": "",
            }
        })
        response = requests.put(self.construct_url('/api/v1/auth'), data=data, verify=False)
        if response.status_code == 200:         
            return response.json()['token']
        else:
            return response.status_code
        
    def __enter__(self):
        self.token = self.get_token()
        return self
    
    def __exit__(self, ex_type, exc_val, exc_tb):
        requests.get(self.construct_url('/api/v1/logout'), headers= {'Authorization': f'Bearer {self.token}'}, verify=False)


with TGFW('10.113.55.162', 'admin', 'Ngfw@123') as device_a:
    token = device_a.token
    header = {'Authorization': f'Bearer {token}',
          'Content-Type': 'application/json'}
    disable_data = {
    "id": 7,
    "val": {
        "id": 7,
        "dst_network": "13.1.1.2/32",
        "enable": False,
        "next_hop_addr": "11.11.11.2",
        "weight": 0,
        "preference": 1,
        "outgoing_interface": ""
    }}
    enable_data = copy.deepcopy(disable_data)
    enable_data['val']['enable'] = True
    number = 10
    
    while number > 0:
        device_a.request('put', '/api/v1/route', headers=header, data=json.dumps(enable_data))
        time.sleep(1)
        device_a.request('put', '/api/v1/route', headers=header, data=json.dumps(disable_data))
        time.sleep(1)
        number -= 1

