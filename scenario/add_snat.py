import time
from main import add_snat
from get_token import get_token


if __name__ == '__main__':
    token = """Bearer """ + get_token()
    print(token)
    token = token.strip()
    k = 0
    for i in range(1,33):
        add_snat(auth=token, outintname=str(i),dstName=str(i))