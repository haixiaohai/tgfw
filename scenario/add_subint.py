import time

from get_token import get_token
from main import add_subint
from main import get_ip_prefix
import json
if __name__ == '__main__':
    token = """Bearer """ + str(get_token())
    print(token)
    token = token.strip()
    for i in range(1, 17):
        time.sleep(1)
        add_subint(auth=token, id='{}'.format(i), name='{}'.format(i), sub_id=i,
                   ip_addresses=['101.0.{}.253/24'.format(i - 1)])
