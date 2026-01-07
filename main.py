from tools import generate_ipv4_list, generate_ipv6_list



ipv6_list = generate_ipv6_list('2000::1', 5000)

start = 2
with open('ipv4policy-5000.csv1.csv', mode='a+') as f:
    for i in range(5000):
        f.write('policy' + str(start) + ',' + 'address' + str(start) + '\n')
        start = start + 1


