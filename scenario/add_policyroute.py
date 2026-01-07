import time
from main import add_policyroute
from main import get_ip_prefix,get_ip_list
from get_token import get_token
from IPy import IP
from random import sample

sip_list = []
dip_list = []
sip = IP('192.168.0.0/22')
dip = IP('172.16.0.0/22')
for i in dip:
    i = str(i)
    dip_list.append(i)
for j in sip:
    j = str(j)
    sip_list.append(j)
d_ipadd = sample(dip_list, 1001)
s_ipadd = sample(sip_list, 1001)

if __name__ == '__main__':
    token = """Bearer """ + get_token()
    print(token)
    token = token.strip()
    k = 0
    for i in range(128):
        add_policyroute(auth=token,id=i,source_network=str(i+1),dst_network=str(i+2),weight=i+1)