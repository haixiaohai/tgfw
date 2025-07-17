from get_token import get_token
from main import add_ipv4_blacklist, add_ipv4_whitelist, add_ipv6_blacklist, add_ipv6_whitelist, get_ip_list
from IPy import IP
from random import sample
import json

sip_list = []
dip_list = []
sip = IP('192.168.3.0/24')
dip = IP('172.16.5.0/24')
ipv6_dip = get_ip_list(begin_ip='FC00::', count=1001, netmask=128)
ipv6_sip = get_ip_list(begin_ip='FC01::', count=1001, netmask=128)
# print(ipv6_sip)
for i in dip:
    i = str(i)
    dip_list.append(i)
for j in sip:
    j = str(j)
    sip_list.append(j)
d_ipadd = sample(dip_list, 200)
s_ipadd = sample(sip_list, 200)
print(str(s_ipadd[1]))
print(s_ipadd)
print(len(s_ipadd))
if __name__ == '__main__':
    token = """Bearer """ + str(get_token())
    print(token)
    token = token.strip()
    for i in range(1,200):
        add_ipv4_blacklist(auth=token, id='{}'.format(i), s_addr='{}'.format(str(s_ipadd[i])),
                           d_addr='{}'.format(str(d_ipadd[i])))
    #     add_ipv6_blacklist(auth=token, id='{}'.format(i+1), s_addr='{}'.format(str(ipv6_sip[i])),
    #                        d_addr='{}'.format(str(ipv6_dip[i])))
    # for j in range(1, 129):
    #     add_ipv4_whitelist(auth=token, id='{}'.format(j), name='{}'.format(j), s_addrs=['{}'.format(d_ipadd[j+512])],
    #                        d_addrs=['{}'.format(s_ipadd[j+512])])
        # add_ipv6_whitelist(auth=token, id='{}'.format(j+64), name='{}'.format(j+64),
        #                    s_addrs=['{}'.format(ipv6_dip[j+512])],
        #                    d_addrs=['{}'.format(ipv6_sip[j+512])])

