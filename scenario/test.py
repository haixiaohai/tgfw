import time
import re
import base64
import json
import requests
from IPy import IP


def get_ip_list(begin_ip, count, netmask):
    ipv4_add = []
    ipv6_add = []
    ip_list = ''  # 用来存放生成的IP地址
    begin_ip = IP(begin_ip)
    ip_list += str(begin_ip)  # 将第一个地址放入ip_列表中
    if begin_ip.version() == 4:
        for i in range(count):
            ip = IP(begin_ip)
            new_ip = IP(ip.ip + 2 ** (32 - netmask))
            begin_ip = str(new_ip)
            # print(begin_ip)
            ipv4_add.append(begin_ip)
        return ipv4_add
    else:
        for i in range(count):
            ipv6 = IP(begin_ip)
            new_ipv6 = IP(ipv6.ip + 2 ** (128 - netmask))
            begin_ip = str(new_ipv6)
            # print(begin_ip)
            ipv6_add.append(begin_ip)
        return ipv6_add

def GenerateIPList(mode:str, A:int, B:int,C:int, D:int) -> list:
    #根据模式生成IP列表
    return '.'.join([str(A), str(B), str(C), str(D)])

def TranIPForm(input):
    #输入是10进制，则转换成点分十进制；输入是点分十进制，则转换成十进制
    if isinstance(input, int):
        if input < 2**32:

            pass
        else:
            raise ValueError('IP地址不可以大于2的32次方')
    
    if isinstance(input, str):
        #需判断输入的字符串是不是IP地址格式
        return None

def nat64Address(prefix,v4Addr):
    # return v6Addr
    # v4地址使用上面函数转换成10进制，然后再转换成16进制即可。
    v4Addr_list = v4Addr.split('.')
    v6Addr_list = []
    for item in v4Addr_list:
        v6Addr_list.append(format(int(item), 'X').zfill(2))
    
    v6Addr = ''.join(v6Addr_list)

    prefix_list=prefix.split(':/')

    list1 = prefix_list[0].split(':')
    list2 = []
    for item in list1:
        list2.append(item.zfill(4))

    return ':'.join(re.findall(r'.{4}', (''.join(list2).ljust(24, '0') + v6Addr)))


def get_token(ip, username, passwd):
    '''
    没有获取到token需要返回错误消息，判断返回的token是否合规，如果存在错误消息返回None
    '''

    url = "https://" + ip + "/api/v1/auth"

    headers = {'Content-Type': 'application/json'}

    data = {
        "id": "admin",
        "val": {
            "username": username,
            "passwd": base64.b64encode(passwd.encode('ascii')).decode('ascii'),
            # "passwd" : "Tmdmd0AxMjM=",
            "action": "login",
            "autht": 0,
            "code": ""
        }
    }

    response = json.loads(requests.put(url=url, headers=headers, data=data, verify=False).text)

    if "errMsg" in response:
        return response['errMsg']
        # return
    return "Bearer " + response['token']

# print(get_token('10.113.54.161','admin','Ngfw@123'))


# 将获取到的token存放在dict中
# tokens = {}
# ip_list = ['10.113.53.204', '10.113.53.206', '10.113.54.161', '10.113.53.201']
# for ip in ip_list: 
#     tokens[ip] = get_token(ip,username='admin',passwd='Ngfw@123')

# print(tokens)


#设备新增配置

def put(url, data, token):
    requests.put(url=url, data=data, headers={'Content-Type': 'application/json', 'Authorization': token}, verify=False)
    return


data = {
    
    "id": "GE0_18",
    "val": {
        "linkType": 0,
        "name": "GE0_18",
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
            "address_mode": 0
        },
        "ipv6_address_mode_config": {
            "dhcp_client_setting": {},
            "address_mode": 0
        },
        "ip_addresses": [
            "11.1.1.1/24"
        ],
        "level": 100,
        "mtus": [
            1500,
            0,
            0,
            0
        ]
    }
}

token = get_token('10.113.54.161','admin','Ngfw@123')

if token:
    print(token)