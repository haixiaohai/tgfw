import json
import time
from IPy import IP
from get_token import get_ipadd
import requests
import json, random

ip_add = get_ipadd()


def add_subint(**kwargs):
    url = 'https://' + ip_add + '/api/v1/intf'
    datas = {"id": 'TE0_11.' + kwargs.get('id'),
             "val": {"name": 'TE0_11.' + kwargs.get('name'), "desc": "", "type": 1, "mode": "Route", "enabled": True,
                     "level": 100,
                     "ipv4_gateway": "", "ipv4_reverse_path": False, "ipv6_reverse_path": False, "ipv6_gateway": "",
                     "sub": {"parent_name": "TE0_11", "sub_id": kwargs.get('sub_id')},
                     "ipv4_address_mode_config": {"address_mode": 0},
                     "ipv6_address_mode_config": {"dhcp_client_setting": {}, "address_mode": 0},
                     "ip_addresses": kwargs.get('ip_addresses'),
                     "service": {"https": False, "ssh": False, "ping": False},
                     "sip": [], "smac": []}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_ipv4_route(**kwargs):
    url = 'https://' + ip_add + '/api/v1/route'
    datas = {
        "val": {"dst_network": kwargs.get('dst_network'), "enable": True, "next_hop_addr": kwargs.get('next_hop_addr')}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_domainpool(**kwargs):
    url = 'https://' + ip_add + '/api/v1/domainpool'
    datas = {"val":{"name":kwargs.get('name'),"domainaddrs":[{"domain":kwargs.get('domain')}]}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_ippool(**kwargs):
    url = 'https://' + ip_add + '/api/v1/ippool'
    datas = {"val": {"name": kwargs.get('name'), "type": 4, "ranges": [],
                     "networks": [{"ipaddr": kwargs.get('ipaddr'), "mask": "32"},
                                  {"ipaddr": kwargs.get('ipaddr1'), "mask": "32"},
                                  {"ipaddr": kwargs.get('ipaddr2'), "mask": "32"},
                                  {"ipaddr": kwargs.get('ipaddr3'), "mask": "32"},
                                  {"ipaddr": kwargs.get('ipaddr4'), "mask": "32"},
                                  {"ipaddr": kwargs.get('ipaddr5'), "mask": "32"},
                                  {"ipaddr": kwargs.get('ipaddr6'), "mask": "32"},
                                  {"ipaddr": kwargs.get('ipaddr7'), "mask": "32"},
                                  {"ipaddr": kwargs.get('ipaddr8'), "mask": "32"},
                                  {"ipaddr": kwargs.get('ipaddr9'), "mask": "32"},
                                  # {"ipaddr": kwargs.get('ipaddr10'), "mask": "32"},
                                  # {"ipaddr": kwargs.get('ipaddr11'), "mask": "32"},
                                  # {"ipaddr": kwargs.get('ipaddr12'), "mask": "32"},
                                  # {"ipaddr": kwargs.get('ipaddr13'), "mask": "32"},
                                  # {"ipaddr": kwargs.get('ipaddr14'), "mask": "32"},
                                  # {"ipaddr": kwargs.get('ipaddr15'), "mask": "32"},
                                  # {"ipaddr": kwargs.get('ipaddr16'), "mask": "32"}
                                  ]}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r.status_code, r.text)


def add_ippool_group(**kwargs):
    url = 'https://' + ip_add + '/api/v1/ippool/group'
    datas = {"id": kwargs.get('id'),
             "val": {"name": kwargs.get('name'), "desc": "", "ippools": [kwargs.get("ippools")]}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_servicepool(**kwargs):
    type = [1, 6, 17, 58]
    url = 'https://' + ip_add + '/api/v1/servicepool'
    datas = {"id": kwargs.get('id'), "val": {"name": kwargs.get('name'), "desc": "", "type": "CUSTOM", "ranges": [
        {"proto": random.choice(type), "s_start": kwargs.get('s_start'), "s_end": kwargs.get('s_end'),
         "d_start": kwargs.get('d_start'), "d_end": kwargs.get('d_end')}]}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r.text)


def add_snat(**kwargs):
    url = 'https://' + ip_add + '/api/v1/natsnat'
    datas = {"val": {"noTransPort": False, "enabled": True, "outInterfaceName": "TE4_2",
                     "zoneName": "any",
                     "srcName": "any", "srcName_is_group": False, "dstName": kwargs.get('dstName'),
                     "dstName_is_group": False,
                     "natType": "nat44", "serviceName": "any", "serviceName_is_group": False, "useInterface": True,
                     "transType": 0, "transParm": ""}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_iplink(**kwargs):
    url = 'https://' + ip_add + '/api/v1/iplink'
    datas = {"val":{"name":kwargs.get('name'),
                    "port":0,
                    "destination":kwargs.get('dest'),
                    "detectType":0,
                    "interface":"any",
                    "interval":1,
                    "retry":3}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_dnat(**kwargs):
    url = 'https://' + ip_add + '/api/v1/natdnat'
    datas = {"val": {"enabled": True, "natType": "nat44", "st_mappings": [
        {"external_interface": "TE4_1", "external_ip": kwargs.get('external_ip'), "protocol": 0,
         "external_port": kwargs.get('external_port'), "twice_nat": 0,
         "twice_nat_trans_type": 0, "twice_nat_trans_parm": "", "session_affinity": 0, "sip_hash": False, "local_ips": [
            {"vrf_id": 0, "local_ip": kwargs.get('local_ip'), "local_port": kwargs.get('local_port'),
             "probability": 100, "health_check": "",
             "health_check_is_group": False}]}]}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_ipv4_blacklist(**kwargs):
    url = 'https://' + ip_add + '/api/v1/blacklist'
    datas = {"id": kwargs.get('id'),
             "val": {"enable": True, "lifespan": 0, "is_ip6": False, "s_addr": kwargs.get('s_addr'),
                     "d_addr": kwargs.get('d_addr'),
                     "is_choose_service": False}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_ipv6_blacklist(**kwargs):
    url = 'https://' + ip_add + '/api/v1/blacklist'
    datas = {"id": kwargs.get('id'),
             "val": {"enable": True, "lifespan": 0, "is_ip6": True, "s_addr": kwargs.get('s_addr'),
                     "d_addr": kwargs.get('d_addr'),
                     "is_choose_service": False}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def mdy_ip_blacklist1(**kwargs):
    url = 'https://' + ip_add + '/api/v1/blacklist'
    datas = {"id": 11535, "val": {"enable": True, "lifespan": 0, "is_ip6": False, "s_addr": "192.168.0.249",
                                  "d_addr": "172.16.1.152", "is_choose_service": False}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.put(url=url, json=datas, headers=headers, verify=False)
    print(r)


def mdy_ip_blacklist2(**kwargs):
    url = 'https://' + ip_add + '/api/v1/blacklist'
    datas = {"id": 11535, "val": {"enable": True, "lifespan": 0, "is_ip6": False, "s_addr": "192.168.111.249",
                                  "d_addr": "172.16.121.152/30", "is_choose_service": False}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.put(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_ipv4_whitelist(**kwargs):
    url = 'https://' + ip_add + '/api/v1/whitelist'
    datas = {"id": kwargs.get('id'),
             "val": {"enable": True, "name": kwargs.get('name'), "desc": "", "s_addrs": kwargs.get('s_addrs'),
                     "d_addrs": kwargs.get('d_addrs'),
                     "is_ip6": False, "is_choose_service": False}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def mdy_ip_whitelist1(**kwargs):
    url = 'https://' + ip_add + '/api/v1/whitelist'
    datas = {"id": 2001, "val": {"enable": True, "name": "test", "desc": "", "s_addrs": ["172.16.255.254"],
                                 "d_addrs": ["192.168.255.254"], "is_ip6": False, "is_choose_service": False}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.put(url=url, json=datas, headers=headers, verify=False)
    print(r)


def mdy_ip_whitelist2(**kwargs):
    url = 'https://' + ip_add + '/api/v1/whitelist'
    datas = {"id": 2001, "val": {"enable": True, "name": "test", "desc": "", "s_addrs": ["172.16.250.254"],
                                 "d_addrs": ["192.168.250.254/30"], "is_ip6": False, "is_choose_service": False}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.put(url=url, json=datas, headers=headers, verify=False)
    print(r.text)


def mdy_intgroup(**kwargs):
    url = 'https://' + ip_add + '/api/v1/intf/pair'
    datas = {"id":kwargs.get('id'),"val":{"name":kwargs.get('name'),"remark":"","receive_interface":kwargs.get('rint'),"transmit_interface":kwargs.get('tint'),"status_sync":kwargs.get('status'),"allowed_vlan":kwargs.get('vlan')}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.put(url=url, json=datas, headers=headers, verify=False)
    print(r.text)

def add_ipv6_whitelist(**kwargs):
    url = 'https://' + ip_add + '/api/v1/whitelist'
    datas = {"id": kwargs.get('id'),
             "val": {"enable": True, "name": kwargs.get('name'), "desc": "", "s_addrs": kwargs.get('s_addrs'),
                     "d_addrs": kwargs.get('d_addrs'), "is_ip6": True, "is_choose_service": False}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_policyroute(**kwargs):
    url = 'https://' + ip_add + '/api/v1/policyroute'
    datas = {"id": kwargs.get('id'),
             "val": {"type": "ipv4", "in_interface": "GE0_1", "source_network": kwargs.get('source_network'),
                     "source_network_is_group": False, "dst_network": kwargs.get('dst_network'),
                     "dst_network_is_group": False,
                     "service": "any", "service_is_group": False, "applist": [], "app_tag_name": [],
                     "forwarding_paths": [
                         {"next_hop_ip": "200.0.0.3", "outgoing_interface": "", "weight": kwargs.get('weight')}],
                     "time_obj": "", "action": 1}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def add_ipv4policy(**kwargs):
    url = 'https://' + ip_add + '/api/v1/ip4policy/fwaclconf'
    datas = {
        "val": {"enable": True, "session_switch": False, "action": 1, "session_time": 1, "desc": "", "szone": "any",
                "dzone": "any", "src_mac": [{"addr_name": "any"}], "src_dns": [{"dns_name": "any"}],
                "dst_mac": [{"addr_name": "any"}], "dst_dns": [{"dns_name": "any"}], "src_geo": [], "dst_geo": [],
                "name": kwargs.get('name'), "log": False,
                "src_addr": [{"addr_name": kwargs.get('src_addr'), "is_group": False}],
                "dst_addr": [{"addr_name": "any", "is_group": False}],
                "service": [{"service_name": "any", "is_group": False}], "applist": [], "userlist": [],
                "app_tag_name": [], "sec_obj_data": []}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def del_blacklist(**kwargs):
    url_1 = 'https://' + ip_add + '/api/v1/blacklist?'
    url_2 = 'id=' + kwargs.get('id')
    url_3 = '&is_ip6=' + kwargs.get('False')
    url = url_1 + url_2 + url_3
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.delete(url=url, headers=headers, verify=False)
    print(r)


def del_whitelist(**kwargs):
    url_1 = 'https://' + ip_add + '/api/v1/whitelist?'
    url_2 = 'id=' + kwargs.get('id')
    url_3 = '&is_ip6=' + kwargs.get('false')
    url = url_1 + url_2 + url_3
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.delete(url=url, headers=headers, verify=False)
    print(r)


def del_route(**kwargs):
    url = 'https://' + ip_add + '/api/v1/route?id=' + kwargs.get('id')
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.delete(url=url, headers=headers, verify=False)
    print(r)


def del_subint(**kwargs):
    url = 'https://' + ip_add + '/api/v1/intf?id=bond10.' + kwargs.get('id')
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.delete(url=url, headers=headers, verify=False)
    print(r)


def del_ippool(**kwargs):
    url = 'https://' + ip_add + '/api/v1/ippool?id=' + kwargs.get('id')
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.delete(url=url, headers=headers, verify=False)
    print(r)


def add_isproute(**kwargs):
    url = 'https://' + ip_add + '/api/v1/isproute'
    datas = {"val": {"name": kwargs.get('name'), "is_ip6": False, "next_hop_addr": "172.172.172.1", "preference": 1}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def del_isproute(**kwargs):
    url = 'https://' + ip_add + '/api/v1/isproute?id=' + kwargs.get('id')
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.delete(url=url, headers=headers, verify=False)
    print(r)


def add_roleauth(**kwargs):
    url = 'https://' + ip_add + '/api/v1/sslvpn/roleauth'
    datas = {"id": 0, "val": {"service": "extend", "name": "2", "action": 0, "authType": 2, "resources": ["日审"],
                              "isChooseService": False, "servicepools": [], "servicepoolgroups": [],
                              "users": ["tyh@default"]}}
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.post(url=url, json=datas, headers=headers, verify=False)
    print(r)


def del_roleauth(**kwargs):
    url = 'https://' + ip_add + '/api/v1/sslvpn/roleauth?id=' + kwargs.get('id')
    headers = {
        'Authorization': kwargs.get('auth')
    }
    r = requests.delete(url=url, headers=headers, verify=False)
    print(r)


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


def get_ip_prefix(begin_ip, count, netmask):
    ipv4_add = []
    ipv6_add = []
    ip_list = ''  # 用来存放生成的IP地址
    begin_ip = IP(begin_ip)
    ip_list += str(begin_ip)  # 将第一个地址放入ip_列表中
    if begin_ip.version() == 4:
        for i in range(count):
            ip = IP(begin_ip)
            new_ip = IP(ip.ip + 2 ** (32 - netmask))
            begin_ip = str(new_ip) + '/24'
            # print(begin_ip)
            ipv4_add.append(begin_ip)
        return ipv4_add
    else:
        for i in range(count):
            ipv6 = IP(begin_ip)
            new_ipv6 = IP(ipv6.ip + 2 ** (128 - netmask))
            begin_ip = str(new_ipv6) + '/96'
            # print(begin_ip)
            ipv6_add.append(begin_ip)
        return ipv6_add
