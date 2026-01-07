# 测试功能
import ipaddress

network = ipaddress.ip_network('192.168.1.0/24')


def a():
    return

class B:
    def __init__(self):
        pass


# print(network.supernet(new_prefix=22))

subnets = network.subnets(new_prefix=30)
c = next(subnets)
print(dir(c), c.compressed)



import base64

def is_base64(s):
    try:
        # 尝试解码
        base64.b64decode(s)
        return True
    except base64.binascii.Error:
        # 如果解码失败，则不是Base64编码
        return False

# 测试字符串
test_str = "XBWLRMGP"  # 这是"hello world"的Base64编码

print(is_base64(test_str), base64.b64encode(test_str))  # 输出: True

test_str = "hello world"  # 这不是Base64编码

print(is_base64(test_str), base64.b64decode(test_str))  # 输出: False
