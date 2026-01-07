import time
import random
from main import add_servicepool
from get_token import get_token

if __name__ == '__main__':
    token = """Bearer """ + str(get_token())
    print(token)
    token = token.strip()
    for i in range(64):
        add_servicepool(auth=token, id='{}'.format(i), name='{}'.format(i), s_start=i,
                        s_end=i+1, d_start=i,
                        d_end=i+1)
