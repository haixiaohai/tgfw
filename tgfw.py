#连接TGFW

import requests
import base64
import json, time, copy, random


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
            return 
        else:
            return response
        
    def _get_token(self):
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
        self.token = self._get_token()
        return self
    
    def __exit__(self, ex_type, exc_val, exc_tb):
        requests.get(self.construct_url('/api/v1/logout'), headers= {'Authorization': f'Bearer {self.token}'}, verify=False)

    def generate_random_ip4pool(self, num, pool_num):
        # 生成随机IPv4地址对象
        # num: 生成对象数量
        # pool_num: 每个对象包含的最大地址数量
        template = {
            "val": {
            "name": '',
            "type": 4,
            "ranges": [],
            "networks": []
            }}
        ip4_random_pools = []        
        network_template = {
            "ipaddr": '',
            "mask": ''
            }
        range_template = {            
            "start": "",
            "end": ""
        }
        
        for i in range(1, num+1):
            temp_template = copy.deepcopy(template)
            network_list = []
            range_list = [] 

            _addr_num = random.randint(1, pool_num)  # 随机生成最多pool_num个地址  5
            _network_num = random.randint(1, _addr_num)  # 随机生成最多j个network  3

            for j in range(_network_num):  # 生成_network_num个network
                temp_network_template = copy.deepcopy(network_template)
                temp_network_template['ipaddr'] = '.'.join(str(random.randint(1,255)) for _ in range(4))
                temp_network_template['mask'] = '32'
                network_list.append(temp_network_template)
                j -= 1
            
            if _addr_num - _network_num > 0:
                for k in range(_addr_num - _network_num):  # 生成_addr_num-_network_num个range
                    temp_range_template = copy.deepcopy(range_template)                   
                    _base = '.'.join(str(random.randint(1,255)) for _ in range(4))
                    temp_range_template['start'] = f'{_base}'

                    #range生成时，end需要大于start                   
                    temp_range_template['end'] = f'{".".join(_base.split(".")[:-1])}.254'
                    range_list.append(temp_range_template)
                    k -= 1

            temp_template['val']['networks'] = network_list
            temp_template['val']['name'] = f'address{i}'
            temp_template['val']['ranges'] = range_list

            ip4_random_pools.append(temp_template)

        return ip4_random_pools


with TGFW('10.113.54.162', 'admin', 'Ngfw@123') as device:
    header = {'Authorization': f'Bearer {device.token}',
          'Content-Type': 'application/json'}
    
    #循环禁用启用可以用request方法写
    # disable_data = {
    # "id": 7,
    # "val": {
    #     "id": 7,
    #     "dst_network": "13.1.1.2/32",
    #     "enable": False,
    #     "next_hop_addr": "11.11.11.2",
    #     "weight": 0,
    #     "preference": 1,
    #     "outgoing_interface": ""
    # }}
    # enable_data = copy.deepcopy(disable_data)
    # enable_data['val']['enable'] = True
    # number = 100000

    # while number > 0:
    #     device_a.request('put', '/api/v1/route', headers=header, data=json.dumps(enable_data))
    #     time.sleep(.5)
    #     device_a.request('put', '/api/v1/route', headers=header, data=json.dumps(disable_data))
    #     time.sleep(1)
    #     number -= 1

    #若需要实现批量添加配置，则需要考虑配置生成

    ip4pools = device.generate_random_ip4pool(1, 10)
    print(ip4pools)

    # for pool in ip4pools:
    #     # print(json.dumps(pool))
    #     print(device.request('post', '/api/v1/ippool', headers=header, data=json.dumps(pool)))
    #     time.sleep(1)

