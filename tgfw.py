#连接TGFW

import requests
import base64
import json, time, copy, random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tools import *

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
        #若成功下发，返回操作成功的对象name，若失败，返回的status_code和message
        method = getattr(requests, method.lower())
        header = kwargs['headers'] if 'headers' in kwargs else '{"Content-Type": "application/json"}'      
        data = kwargs['data'] if 'data' in kwargs else None
        response = method(self.construct_url(url),  
                          headers=header,
                          data=json.dumps(data),
                          verify=False)
        
        if response.status_code == 200:
            if 'name' in kwargs['data']['val']:
                return kwargs['data']['val']['name']
            return
        else:
            return response

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
            
            if _addr_num - _network_num > 0:
                for k in range(_addr_num - _network_num):  # 生成_addr_num-_network_num个range
                    temp_range_template = copy.deepcopy(range_template)                   
                    _base = '.'.join(str(random.randint(1,255)) for _ in range(4))
                    temp_range_template['start'] = f'{_base}'

                    #range生成时，end需要大于start                   
                    temp_range_template['end'] = f'{".".join(_base.split(".")[:-1])}.254'
                    range_list.append(temp_range_template)

            temp_template['val']['networks'] = network_list
            temp_template['val']['name'] = f'address{i}'
            temp_template['val']['ranges'] = range_list

            ip4_random_pools.append(temp_template)
        return ip4_random_pools

    def generate_ip4pool(self, base_ip, num, step=1):
        #基于base_ip生成num个ip地址对象，默认递增步进是1
        template = {
            "val": {
            "name": '',
            "type": 4,
            "ranges": [],
            "networks": [{
            "ipaddr": '',
            "mask": '32'
            }]
            }}        
        ip4pools = []
        ips = generate_ipv4_list(base_ip, num, step)
        for i in range(num):
            temp_template = copy.deepcopy(template)
            temp_template['val']['name'] = f'address{i+1}'
            temp_template['val']['networks'][0]['ipaddr'] = ips[i]
            ip4pools.append(temp_template)
        return ip4pools

    def generate_ip4policy(self, num:int, addr_pools:list, service_pools:list):
        #生成ip4安全策略对象
        template = {
        "val": {
            "enable": True,
            "session_switch": False,
            "action": 1,   # tag
            "session_time": 0,
            "policy_group": "全部",
            "desc": "",
            "szone": "any",
            "dzone": "any",
            "src_mac": [
            {
                "addr_name": "any"
            }
            ],
            "src_dns": [
            {
                "dns_name": "any"
            }
            ],
            "dst_mac": [
            {
                "addr_name": "any"
            }
            ],
            "dst_dns": [
            {
                "dns_name": "any"
            }
            ],
            "src_geo": [],
            "dst_geo": [],
            "name": "111",   # tag
            "log": True,   
            "src_addr": [],
            "dst_addr": [],
            "service": [],
            "applist": [],
            "userlist": [],
            "app_tag_name": [],
            "sec_obj_data": []
        }
        }
        addr_pool_template = {
                "addr_name": "",  # tag
                "is_group": False
            }
        server_pool_template = {
                "service_name": "any",
                "is_group": False
            }
        

        policy_pools = []
        
        for i in range(num):
            temp_template = copy.deepcopy(template)
            temp_template['action'] = random.randint(0, 1)
            temp_template['name'] = f'secpolicy{i+1}'
            temp_template['val']['src_addr'][0]['addr_name'] = random.choice(addr_pools)['id']

            policy_pools.append(temp_template)

        return policy_pools
    
    def generate_serverpool(self, num:int, protocol:int, pool_num:int, sport:int=10000) -> list:
        template = {
        "id": "serverpool1",
        "val": {
            "name": "serverpool1",  # tag
            "desc": "",
            "type": "CUSTOM",
            "ranges": []
        }}
        l4_serverpool_template = {
                "proto": 6,    # tag
                "s_start": 0,
                "s_end": 65535,
                "d_start": 0,  # tag
                "d_end": 10001 # tag
            }
        server_pool = []
        for i in range(num):           
            temp_template = copy.deepcopy(template)
            l4_serverpool_template_list = []

            _pool_num = random.randint(1, pool_num)   # 每个pool里面的条目 
            for j in range(_pool_num):
                sport += 1
                if sport < 65535:
                    temp_l4_serverpool_template = copy.deepcopy(l4_serverpool_template)
                    temp_l4_serverpool_template['d_start'] = sport 
                    temp_l4_serverpool_template['d_end'] = sport
                    temp_l4_serverpool_template['proto'] = protocol
                    l4_serverpool_template_list.append(temp_l4_serverpool_template)
            
            temp_template['val']['name'] = f'serverpool{i+1}'
            temp_template['val']['ranges'] = l4_serverpool_template_list
            server_pool.append(temp_template)
       
        return server_pool

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

with TGFW('10.113.54.162', 'admin', 'Ngfw@123') as device:
    headers = {'Authorization': f'Bearer {device.token}',
          'Content-Type': 'application/json'}
    
    # 循环禁用启用可以用request方法写
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

    ip4pools = device.generate_ip4pool('3.3.3.2', 20, 256)
    print(ip4pools, len(ip4pools))
    # addr_pool_list = []
    # server_pool_list = []
    # for pool in ip4pools:

    #     result = device.request('post', '/api/v1/servicepool', headers=headers, data=pool)
    #     if result:
    #         addr_pool_list.append(result)
    #     time.sleep(0.5)
    
    # print(addr_pool_list)
