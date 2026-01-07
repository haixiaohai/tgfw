import time
from main import add_iplink,get_ip_list
from get_token import get_token
ipv4_addr = get_ip_list(begin_ip='101.0.0.1', count=16, netmask=32)

if __name__ == '__main__':
    token = """Bearer """ + get_token()
    print(token)
    token = token.strip()
    k = 0
    for i in range(1,17):
        add_iplink(auth=token, name="test-{}".format(i),dest=ipv4_addr[i-1])