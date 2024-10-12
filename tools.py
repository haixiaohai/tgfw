'''
常用工具集
'''

import re

def trans_ip_form(input_ip):
    '''
    十进制转换成点分十进制或点分十进制转换成十进制

    '''

    if isinstance(input_ip, int):
        if input_ip < 2 ** 32:
            # bin_input = format(input, 'b').zfill(32)    # 把十进制转成二进程并补全至32位
            # bin_input_list = [bin_input[i:i+8] for i in range(0, 32, 8)]   # 二进制数组

            dec_input_list = []
            for j in [24, 16, 8]:
                input_tuple = divmod(input_ip, 2 ** j)
                dec_input_list.append(str(input_tuple[0]))
                input_ip = input_tuple[1]
            dec_input_list.append(str(input_tuple[1]))
            return '.'.join(dec_input_list)
        else:
            raise ValueError('输入的数字不能大于IP地址范围')
    if isinstance(input_ip, str):
        # 判断字符串是不是IP地址格式
        if re.fullmatch(r'(\d{1,3}\.){3}\d{1,3}', input_ip):
            input_list = input_ip.split('.')
            return int(input_list[0]) * 2 ** 24 + \
                   int(input_list[1]) * 2 ** 16 + \
                   int(input_list[2]) * 256 + \
                   int(input_list[3])
        else:
            raise ValueError('IPv4地址格式不正确')


def generate_ipv4_list(base_ip, num, step=1):
    '''
    生成IPv4地址列表
    '''

    ret_list = []
    for i in range(num):
        dec_base_ip = trans_ip_form(base_ip)  # 转换成十进制
        ret_list.append(trans_ip_form(dec_base_ip + i * step))

    return ret_list


def nat64addr(prefix, v4addr):
    '''
    把v6前缀和v4地址组合成nat64的业务目的地址
    '''

    v4tov6addr = format(trans_ip_form(v4addr), 'x')
    pref, netmask = prefix.split('::/')
    pref_list = pref.split(':')

    # 如果输入的前中有省略的0需要补齐
    for index, item in enumerate(pref_list):
        if len(item) < 4:
            pref_list[index] = item.rjust(4, '0')

    v6addr = (''.join(pref_list).ljust(int(netmask) // 4, '0') + v4tov6addr).ljust(32, '0')

    v6addr_list = [v6addr[m:m + 4] for m in range(0, 32, 4)]

    return ':'.join(v6addr_list)


def nptv6_addr_trans():
    '''
    nptv6地址转换
    '''

    
    return


def hex_to_ascii(hex_string):
    # 16进制字符串转ASCII字符串

    # 去掉空格，确保字节串连续
    hex_string = hex_string.replace(" ", "")
    
    # 将十六进制字符串转换为字节
    bytes_object = bytes.fromhex(hex_string)
    
    # 将字节转换为 ASCII 字符串，无法显示的字符用替代符号表示
    ascii_string = bytes_object.decode("ascii", errors="replace")
    
    return ascii_string