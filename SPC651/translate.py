import ipaddress

# with open('SPC651/v4_route.txt', 'r') as file:
#     with open('SPC651/v6_route.txt', 'w') as v6_file:
#         lines = file.readlines()
#         for line in lines:
#             prefix, netmask = line.strip().split(' ')[4:6]
#             # print(prefix, netmask)

#             #将V4地址转换成V6地址
#             v4_int = int(ipaddress.IPv4Address(prefix))
#             v4_hex = f'{v4_int:08x}'

#             _v4_hex = ':'.join(v4_hex[i:i+4] for i in range(0, len(str(v4_hex)), 4))  #
#             v6_prefix = '2000::' + _v4_hex 

#             #将V4掩码转换成V6掩码
#             netmask_len = ipaddress.IPv4Network(f'0.0.0.0/{netmask}').prefixlen

#             v6_netmask = 128 - (32 - netmask_len)
#             v6_file.write(f'ipv6 route-static vpn-instance zjh {v6_prefix} {v6_netmask} NULL0\n')



# with open('SPC651/v4_route.txt', 'r') as file:
#     with open('SPC651/v4_preifx.txt', 'w') as v4_prefix_file:
#         lines = file.readlines()
#         for line in lines:
        
#             # 提取V4前缀
#             prefix, netmask = line.strip().split(' ')[4:6]

#             netmask_int = ipaddress.IPv4Network(f'0.0.0.0/{netmask}').prefixlen

#             # 保存V4前缀
#             v4_prefix_file.write(f'{prefix}\n')


with open('SPC651/v6_route.txt', 'r') as file:
    with open('SPC651/v6_preifx.txt', 'w') as v6_prefix_file:
        lines = file.readlines()
        for line in lines:
        
            # 提取V6前缀
            prefix, netmask = line.strip().split(' ')[4:6]
            # 保存V6前缀
            v6_prefix_file.write(f'{prefix}/{netmask}\n')
        