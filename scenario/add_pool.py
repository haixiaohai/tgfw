import time

from main import add_ippool, get_ip_list
from get_token import get_token

#  [{"ipaddr": kwargs.get('ipaddr'), "mask": ""}]

ipv4_addr = get_ip_list(begin_ip='192.168.1.1', count=51000, netmask=32)
print(ipv4_addr)
if __name__ == '__main__':
    # token = """Bearer """ + str(get_token())
    token = str(get_token())
    # token = str(get_token())
    print(token)
    token = token.strip()
    k = 0
    for i in range(0, 500):
        add_ippool(auth=token, name='{}'.format(i),
                   ipaddr='{}'.format(ipv4_addr[k+1]),
                   ipaddr1='{}'.format(ipv4_addr[k+2]),
                   ipaddr2='{}'.format(ipv4_addr[k+3]),
                   ipaddr3='{}'.format(ipv4_addr[k+4]),
                   ipaddr4='{}'.format(ipv4_addr[k+5]),
                   ipaddr5='{}'.format(ipv4_addr[k+6]),
                   ipaddr6='{}'.format(ipv4_addr[k+7]),
                   ipaddr7='{}'.format(ipv4_addr[k+8]),
                   ipaddr8='{}'.format(ipv4_addr[k+9]),
                   ipaddr9='{}'.format(ipv4_addr[k+10]),
                   # ipaddr10='{}'.format(ipv4_addr[k+11]),
                   # ipaddr11='{}'.format(ipv4_addr[k+12]),
                   # ipaddr12='{}'.format(ipv4_addr[k+13]),
                   # ipaddr13='{}'.format(ipv4_addr[k+14]),
                   # ipaddr14='{}'.format(ipv4_addr[k+15]),
                   # ipaddr15='{}'.format(ipv4_addr[k+16]),
                   # ipaddr16='{}'.format(ipv4_addr[k+17])
                   )
        k =+ 18
