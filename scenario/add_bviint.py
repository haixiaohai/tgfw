import time

from get_token import get_token
from main import add_bviint
from main import get_ip_prefix
import json

if __name__ == '__main__':
    token = """Bearer """ + str(get_token())
    print(token)
    token = token.strip()
    for i in range(1, 32):
        add_bviint(auth=token, id='{}'.format(i), name='{}'.format(i), b_name='{}'.format(i),ins=i,ipadd='172.16.{}.1/24'.format(i))
        print(i)
