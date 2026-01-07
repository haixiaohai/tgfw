import time
from main import add_dnat
from get_token import get_token


if __name__ == '__main__':
    token = """Bearer """ + get_token()
    print(token)
    token = token.strip()
    k = 0
    for i in range(1,33):
        add_dnat(auth=token, external_ip='192.0.0.{}'.format(i),external_port=i,local_port=i,local_ip='192.168.1.1')