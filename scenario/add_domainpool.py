import time

from main import add_domainpool
from get_token import get_token
from IPy import IP

if __name__ == '__main__':
    token = """Bearer """ + get_token()
    print(token)
    token = token.strip()
    for i in range(32):
        add_domainpool(auth=token,name='test-{}'.format(i),domain='www.test{}.com'.format(i))