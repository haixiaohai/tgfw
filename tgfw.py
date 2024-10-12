#连接TGFW

import requests, base64, ipaddress, json, time, copy, random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tools import *

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class TGFW:
    # 操作TGFW设备
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
                          data=data,
                          verify=False)
        
        if response.status_code == 200:
            # if 'name' in kwargs['data']['val']:
            #     return kwargs['data']['val']['name']
            return
        else:
            return response

    def generate_random_ip4addr_obj(self, num, pool_num):
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

    def generate_ip4addr_obj(self, base_ip, num, step=1):
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

    def generate_ip4addr_group_obj(self):
        pass
    
    def generate_domainName_obj(self):
        pass

    

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
    
    def generate_server_obj(self, num:int, protocol:int, pool_num:int, sport:int=10000) -> list:
        #生成自定义服务配置
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


class render:
    # 根据拓扑渲染出TGFW和辅测设备的配置，需要传入拓扑、互联网段、业务网段、

    def __init__(self):        
        pass
    
    def generate_subnetwork(self, network, number, mask=30):
        # 根据地址池生成子网段，需要判断地址池是否合法

        network = ipaddress.ip_network(network)
        network2 = network.subnets(new_prefix=mask)
        rst = []
        for i in range(number):
            try:
                rst.append(next(network2).compressed)
            except StopIteration:
                raise ValueError(f'地址池不足，需要{number}个地址，但只有{len(rst)}个可用')
        return rst


with TGFW('10.113.55.83', 'admin', 'Ngfw@123') as device:
    headers = {'Authorization': f'Bearer {device.token}',
          'Content-Type': 'application/json'}
    
    # 循环禁用启用可以用request方法写
    disable_data = {
    "id": "GE0_3",
    "val": {
        "linkType": 0,
        "name": "GE0_3",
        "type": 3,
        "enabled": False,
        "vltype": "VPP",
        "mode": "Route",
        "service": {
            "https": False,
            "ssh": False,
            "ping": False
        },
        "sip": [],
        "smac": [],
        "ipv4_address_mode_config": {
            "address_mode": 0,
            "dhcp_client_setting": {}
        },
        "ipv6_address_mode_config": {
            "address_mode": 0,
            "dhcp_client_setting": {}
        },
        "ip_addresses": []
    }
}
    # enable_data = copy.deepcopy(disable_data)
    # enable_data['val']['enable'] = True

    enable_data = {
    "id": "GE0_3",
    "val": {
        "linkType": 0,
        "name": "GE0_3",
        "type": 3,
        "enabled": True,
        "vltype": "VPP",
        "mode": "Route",
        "service": {
            "https": False,
            "ssh": False,
            "ping": False
        },
        "sip": [],
        "smac": [],
        "ipv4_address_mode_config": {
            "address_mode": 0,
            "dhcp_client_setting": {}
        },
        "ipv6_address_mode_config": {
            "address_mode": 0,
            "dhcp_client_setting": {}
        },
        "ip_addresses": []
    }
}
    
    haswitch = {
    "id": 1,
    "val": {
        "forceSwitch": True
    }
}
    number = 200

    policy1 = {
    "id": 1,
    "val": {
        "enable": True,
        "session_switch": False,
        "action": 1,
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
        "name": "1",
        "log": True,
        "src_addr": [
            {
                "addr_name": "any",
                "is_group": False
            }
        ],
        "dst_addr": [
            {
                "addr_name": "any",
                "is_group": False
            }
        ],
        "service": [
            {
                "service_name": "any",
                "is_group": False
            }
        ],
        "applist": [],
        "userlist": [],
        "app_tag_name": [],
        "sec_obj_data": [
            {
                "profile_id": 1,
                "profile_name": "qzgaj",
                "model_name": "av"
            },
            {
                "profile_id": 1001,
                "profile_name": "qzgaj",
                "model_name": "ips"
            },
            {
                "profile_id": 1,
                "profile_name": "恶意域名",
                "model_name": "urlFilter"
            },
            {
                "profile_id": 1,
                "profile_name": "qzgaj",
                "model_name": "dga"
            }
        ]
    }
}
    
    policy2 = {
    "id": 1,
    "val": {
        "enable": True,
        "session_switch": False,
        "action": 1,
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
        "name": "1",
        "log": True,
        "src_addr": [
            {
                "addr_name": "any",
                "is_group": False
            }
        ],
        "dst_addr": [
            {
                "addr_name": "any",
                "is_group": False
            }
        ],
        "service": [
            {
                "service_name": "any",
                "is_group": False
            }
        ],
        "applist": [],
        "userlist": [],
        "app_tag_name": [],
        "sec_obj_data": [
            {
                "profile_id": 1,
                "profile_name": "qzgaj",
                "model_name": "av"
            },
            {
                "profile_id": 1002,
                "profile_name": "allrule",
                "model_name": "ips"
            },
            {
                "profile_id": 1,
                "profile_name": "恶意域名",
                "model_name": "urlFilter"
            },
            {
                "profile_id": 1,
                "profile_name": "qzgaj",
                "model_name": "dga"
            }
        ]
    }
}

    while number > 0:
        # d = json.dumps(disable_data)
        # e = json.dumps(enable_data)
        device.request('put', '/api/v1/intf', headers=headers, data=json.dumps(disable_data))
        time.sleep(30)
        device.request('put', '/api/v1/intf', headers=headers, data=json.dumps(enable_data))
        time.sleep(30)
        number -= 1

    #若需要实现批量添加配置，则需要考虑配置生成

    # ip4pools = device.generate_ip4pool('3.3.3.2', 20, 256)
    # print(ip4pools, len(ip4pools))
    # addr_pool_list = []
    # server_pool_list = []
    # for pool in ip4pools:

    #     result = device.request('post', '/api/v1/servicepool', headers=headers, data=pool)
    #     if result:
    #         addr_pool_list.append(result)
    #     time.sleep(0.5)
    
    # print(addr_pool_list)


# config = render()

# print(config.generate_subnetwork('192.168.0.0/20', 100, 29))