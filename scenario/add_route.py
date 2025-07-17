import time

from main import add_ipv4_route
from main import get_ip_prefix
from get_token import get_token
from IPy import IP

ip_prefix = get_ip_prefix(begin_ip='172.168.0.0', count=500, netmask=24)
ipv6_prefix = get_ip_prefix(begin_ip='FC04::', count=500, netmask=96)
print(ip_prefix)
if __name__ == '__main__':
    token = """Bearer """ + get_token()
    print(token)
    token = token.strip()
    for i in range(0,128):
        time.sleep(1)
        add_ipv4_route(auth=token,dst_network='{}'.format(ip_prefix[i]),next_hop_addr='172.16.1.254')
        add_ipv4_route(auth=token, dst_network='{}'.format(ipv6_prefix[i]), next_hop_addr='2001:172:16::1')