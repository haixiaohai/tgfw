import time

from main import add_ippool_group, get_ip_list
from get_token import get_token

#  [{"ipaddr": kwargs.get('ipaddr'), "mask": ""}]

if __name__ == '__main__':
    token = """Bearer """ + str(get_token())
    print(token)
    token = token.strip()
    k = 0
    for i in range(1,65):
        add_ippool_group(auth=token, id=str(i), name='{}'.format(i),
                         ippools='{}'.format(i-1))


