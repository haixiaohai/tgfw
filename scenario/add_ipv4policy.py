import time
from main import add_ipv4policy,add_ippool,add_ipv4_blacklist,add_ipv4_whitelist
from get_token import get_token


if __name__ == '__main__':
    # token = """Bearer """ + str(get_token())
    token = str(get_token())
    print(token)
    token = token.strip()
    k = 0
    for i in range(500):
        add_ipv4policy(auth=token, name='{}'.format(i),src_addr='{}'.format(i))
    # for j in range(1024,2048):
    #     add_ipv4policy(auth=token, name='{}'.format(j),src_addr='{}'.format(j-1024))