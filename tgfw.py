#连接TGFW

import requests, base64, ipaddress, copy, random, re, pytesseract, time
from requests.packages.urllib3.exceptions import InsecureRequestWarning # type: ignore
from tools import * # type: ignore
from PIL import Image
from io import BytesIO
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import os

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

class TGFW:
    # 操作TGFW设备
    def __init__(self, ip, username, password, port=443):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.token = None

    @staticmethod
    def static_always_inline() -> int:
        # Implementation of the static method
        return 64

    def construct_url(self, uri):
        return f'https://{self.ip}:{self.port}{uri}'
    
    def request(self, method:str, uri:str, **kwargs) -> tuple:
        # get/post/put/delete
        # 为了配合场景测试，如果是POST请求，需要把对象的名称返回
        method = getattr(requests, method.lower())
        header = kwargs['headers'] if 'headers' in kwargs else {"Content-Type": "application/json"}  
        data = kwargs['data'] if 'data' in kwargs else {}
        
        #如果传进来了header和data，，需要判断header和da的类型
        if isinstance(data, dict) and isinstance(header, dict):
            response = method(self.construct_url(uri), headers=header, json=data, verify=False)
        else:
            raise TypeError("header和data必须为字典类型")        
        return response  # 不同的请求返回的内容不同，引用时自行判断

    def generate_random_ip4addr_obj(self, num, pool_num) -> list:
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
        '''
        获取设备的token
        '''

        # 获取公钥，第一步先从HTML中解析到公钥文件名，然后再get公钥内容
        r = self.request('get', '', headers={'Content-Type': 'text/html'})
        if r.status_code != 200:
            raise Exception('连接设备失败，手动检查')
        public_key_filename = re.findall(r'ras_public_key.\d+.js', r.text)[0]
        js_text = self.request('get', '/js/'+public_key_filename, headers={'Content-Type': 'application/javascript'}).text
        lines = re.findall(r"'(.*?)'", js_text, re.DOTALL) 
        public_key_pem = '\n'.join([line.replace('\\n', '').strip() for line in lines])  #公钥

        # 加载公钥
        from cryptography.hazmat.backends import default_backend
        public_key = serialization.load_pem_public_key(public_key_pem.encode(), backend=default_backend())
        encrypted_password = public_key.encrypt(self.password.encode('utf-8'),padding.PKCS1v15())
        encrypted_password_b64 = base64.b64encode(encrypted_password).decode('utf-8')
        # print(encrypted_password_b64)

        # 获取验证码  uri = /api/v1/getAuthConfig
        captcha_data = {
        "id": "verify",
        "val": {}
        }
        captcha_response = self.request('put', '/api/v1/getAuthConfig', data=captcha_data)
        if captcha_response.status_code != 200:
            raise Exception('获取验证码失败')
            exit(1)

        captche_img = captcha_response.json()['data']
        verify_id = captcha_response.json()['vertifyid']

        # 解析验证码
        captcha_img_base64 = captche_img.split(",")[1]
        img_bytes = base64.b64decode(captcha_img_base64)
        img = Image.open(BytesIO(img_bytes))
        text = pytesseract.image_to_string(img)   

        # 登录获取token
        data = {
            "id": self.username,
            "val": {
            "username": self.username,
            "passwd": encrypted_password_b64,
            "action": "login",
            "autht": 0,
            "code": "",
            "vertifycode": text.replace(' ', '').strip(),
            "vertifyid": verify_id
            }
        }
        response = self.request('put', '/api/v1/auth', data=data)
        if response.status_code == 200:         
            return response.json()['token']
        
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


with TGFW('10.113.55.147', 'admin', 'Ngfw@123') as device:

    #需要判断有没有正常获取到token
    if not device.token:
        raise Exception('获取token失败，请检查设备连接和登录信息')
    
    headers = {'Authorization': f'Bearer {device.token}',
               'Content-Type': 'application/json',
               'charset': 'utf-8'
                }
    
    # 循环禁用启用可以用request方法写
    number = 50
    down_interface =  {
    "id": "GE0_5.202",
    "val": {
        "vltype": "VPP",
        "linkType": 0,
        "name": "GE0_5.202",
        "desc": "",
        "type": 1,
        "mode": "Route",
        "enabled": False,
        "level": 100,
        "ipv4_gateway": "",
        "ipv4_reverse_path": False,
        "ipv6_reverse_path": False,
        "ipv6_gateway": "",
        "mtus": [
            1500,
            0,
            0,
            0
        ],
        "sub": {
            "parent_name": "GE0_5",
            "sub_id": 202
        },
        "ipv4_address_mode_config": {
            "address_mode": 0
        },
        "ipv6_address_mode_config": {
            "dhcp_client_setting": {},
            "address_mode": 0
        },
        "ip_addresses": [
            "10.202.1.252/24"
        ],
        "service": {
            "https": False,
            "ssh": False,
            "ping": False
        },
        "sip": [],
        "smac": []
    }
}
    up_interface = {
    "id": "GE0_5.202",
    "val": {
        "vltype": "VPP",
        "linkType": 0,
        "name": "GE0_5.202",
        "desc": "",
        "type": 1,
        "mode": "Route",
        "enabled": True,
        "level": 100,
        "ipv4_gateway": "",
        "ipv4_reverse_path": False,
        "ipv6_reverse_path": False,
        "ipv6_gateway": "",
        "mtus": [
            1500,
            0,
            0,
            0
        ],
        "sub": {
            "parent_name": "GE0_5",
            "sub_id": 202
        },
        "ipv4_address_mode_config": {
            "address_mode": 0
        },
        "ipv6_address_mode_config": {
            "dhcp_client_setting": {},
            "address_mode": 0
        },
        "ip_addresses": [
            "10.202.1.252/24"
        ],
        "service": {
            "https": False,
            "ssh": False,
            "ping": False
        },
        "sip": [],
        "smac": []
    }
}

    while number > 0:
        # print(device.token)
        r1 = device.request('put', '/api/v1/intf', headers=headers, data=down_interface)
        if r1.status_code == 200:
            time.sleep(120)
        else:
            print(r1)
            break  
        r2 = device.request('put', '/api/v1/intf', headers=headers, data=up_interface)
        if r2.status_code == 200:
            time.sleep(120)
        else:
            print(r2)
            break
        number -= 1
        print(number)
# for i in range(1, 5):

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