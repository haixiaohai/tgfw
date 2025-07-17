# import pandas as pd
# from sqlalchemy import create_engine

# username = 'root'
# password = 'ngfw123!%40%23'
# port = '3306'
# host = '10.113.53.29'
# database = 'true_zentao_copy'


# engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')



# df = pd.read_sql_query('SELECT * FROM zt_bug', engine)

# print(df.head())

from scapy.all import send, sniff, IP, UDP, ICMP, Raw, DNS, DNSQR, ls, DNSRR, AsyncSniffer
import random, time, threading, asyncio

def icmp_error(packet):
    # 提取报文的源IP、目的IP、源端口和目的端口
    ip_src = packet[IP].src
    ip_dst = packet[IP].dst
    udp_src = packet[UDP].sport
    udp_dst = packet[UDP].dport

    # 构造ICMP错误报文

    ret_packet = IP(src=ip_dst, dst=ip_src)/ICMP(type=3, code=3, checksum=0x1341)/ IP(src=ip_src, dst=ip_dst)/UDP(sport=udp_src, dport=udp_dst)
    send(ret_packet)
    print('success')

def create_udp_packet_and_send():
    # 生成目的IP随机，源端口和目的端口随机的UDP报文并发送

    ip_src = '10.10.10.20'
    ip_dst = '.'.join(str(random.randint(0, 255)) for _ in range(4))
    udp_src = random.randint(1025, 65535)
    udp_dst = random.randint(1025, 65535)
    packet = IP(src=ip_src, dst=ip_dst)/UDP(sport=udp_src, dport=udp_dst)
    send(packet)

def generate_dns_query_packet_and_send(condition=True, interval=0.1, src='10.113.6.83', dst='10.113.6.43'):
    # 生成dns报文并发送，DNS报文的请求域名随机变化
    
    def _create_dns_query_packet_and_send(src, dst):
        query_name = 'www.' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5)) + '.com'
        ip = IP(src=src, dst=dst)
        udp = UDP(sport=random.randint(1025, 65535), dport=53)
        dns = DNS(
                  id=random.randint(1, 65535),
                  rd=1, 
                  qd=DNSQR(qname=query_name, qtype='A', qclass='IN'))
        
        packet = ip/udp/dns
        send(packet)
    while condition:
        _create_dns_query_packet_and_send(src=src, dst=dst)
        time.sleep(interval)

def handle_dns_packet_and_response(packet):
    # 提取dns报文的请求域名，构造dns响应报文并发送
    if DNS in packet:
        if b'.com' in packet[DNS].qd.qname:
            query_name = packet[DNSQR].qname
            cname = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=7)) + '.org'
            ip = IP(src=packet[IP].dst, dst=packet[IP].src)
            udp = UDP(sport=53, dport=packet[UDP].sport)
            dns = DNS(id=packet[DNS].id, 
                    qr=1, 
                    qd=packet[DNS].qd, 
                    ancount=1,
                    an=DNSRR(rrname=query_name, type='CNAME', rdata=cname))
            response_packet = ip/udp/dns
            send(response_packet)

def handle_dns_cname_response_and_re_request(filter='src host 10.113.6.43',interface='以太网 2'):
    # 处理dns响应报文，提取cname，构造新的dns请求报文并发送

    def _request_cname(packet):
        if DNSRR in packet:
            print(packet[DNSRR].rdata)
            ip=IP(src=packet[IP].dst, dst=packet[IP].src)
            udp=UDP(sport=packet[UDP].dport, dport=packet[UDP].sport)

            dns=DNS(id=packet[DNS].id, 
                    rd=1, 
                    qd=DNSQR(qname=packet[DNSRR].rdata, 
                            qtype='A', 
                            qclass='IN'))

            request_packet=ip/udp/dns
            send(request_packet)

    sniff(prn=_request_cname, filter='src host 10.113.6.43', iface='以太网 2', store=0)


# thread1 = threading.Thread(target=generate_dns_query_packet_and_send, args=(True, 2, '10.113.6.83', '10.113.6.43'))
# thread2 = threading.Thread(target=handle_dns_cname_response_and_re_request, args=('src host 10.113.6.43', '以太网 2'))

# thread1.start()
# thread2.start()

# sniff(prn=handle_dns_packet_and_response, filter='src host 10.113.6.83 and port 53')


async def async_generate_dns_query_packet_and_send(condition=True, interval=0.1, src='10.113.6.83', dst='10.113.6.43'):
    # 生成dns报文并发送，DNS报文的请求域名随机变化
    
    def _create_dns_query_packet_and_send(src, dst):
        query_name = 'www.' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5)) + '.com'
        ip = IP(src=src, dst=dst)
        udp = UDP(sport=random.randint(1025, 65535), dport=53)
        dns = DNS(
                  id=random.randint(1, 65535),
                  rd=1, 
                  qd=DNSQR(qname=query_name, qtype='A', qclass='IN'))
        
        packet = ip/udp/dns
        send(packet)
    while condition:
        _create_dns_query_packet_and_send(src=src, dst=dst)
        await asyncio.sleep(interval)

async def async_handle_dns_cname_response_and_re_request(filter='src host 10.113.6.43',interface='以太网 2'):
    # 处理dns响应报文，提取cname，构造新的dns请求报文并发送

    def _request_cname(packet):
        if DNSRR in packet:
            print(packet[DNSRR].rdata)
            ip=IP(src=packet[IP].dst, dst=packet[IP].src)
            udp=UDP(sport=packet[UDP].dport, dport=packet[UDP].sport)

            dns=DNS(id=packet[DNS].id, 
                    rd=1, 
                    qd=DNSQR(qname=packet[DNSRR].rdata, 
                            qtype='A', 
                            qclass='IN'))

            request_packet=ip/udp/dns
            send(request_packet)

    sniffer = AsyncSniffer(prn=_request_cname, filter='src host 10.113.6.43', iface='以太网 2', store=0)

    sniffer.start()
    await asyncio.sleep(3)
    sniffer.stop()

async def main():
    task1 = asyncio.create_task(async_generate_dns_query_packet_and_send())
    task2 = asyncio.create_task(async_handle_dns_cname_response_and_re_request())
    await asyncio.gather(task1, task2)

asyncio.run(main())