'''
生成报文，修改报文内容，发送报文，分析报文
'''

from scapy.all import IP, ICMP, raw, TCP, UDP, send, sniff, wrpcap, rdpcap, RandIP
import re

# 修改报文的内容
# packets = rdpcap('baiyun1.cap')
# packets[0].show()

# packets[0][IP].src = '10.128.180.79'

# packets[0].show()

# wrpcap('baiyun1_1.pcap', packets)



# 生成报文
# dst_ip = '10.128.180.79'
# dst_port = 443
# src_port = 59438
# tcp = TCP(sport=src_port, dport=dst_port, flags='S')
# packet = IP(dst=dst_ip)/tcp

# send(packet, verbose=1)


def htd(src):
    return str(int(src,base=16))

def ipAddressConvert(src,method='htd'):
    def intStr(src,base):
        return str(int(src,base))
    if method == 'htd':
        srcList = re.findall(r'.{2}',src)
        return '.'.join(list(map(intStr,srcList,[16,16,16,16])))
    else:
        pass
    

def dot1qHandle(src):
    #识别802.1q头
    ret = {
        '802.1qHeader' : {
            'pricfi' : src[:1],
            'vlan' : src[1:4],
            'ethtype' : src[4:8]
            }
    }
    ethType = src[4:8]
    left = src[8:]

    if ethType == '0800':
        ipHeader = ipHandle(left)
        ret.update(ipHeader)
    
    if ethType == '0806':
        arpHeader = arpHandle(left)
        ret.update(arpHeader)

    return ret

def arpHandle(src):
    ret = {
        'hardwareType' : src[0:4],
        'protocolType' : src[4:8],
        'hardwareSize' : src[8:10],
        'protocolSize' : src[10:12],
        'opCode' : src[12:16],
        'arpsmac' : src[16:28],
        'arpsip' : src[28:36],
        'arpdmac' : src[36:48],
        'arpdip' : src[48:]
    }
    return ret

def ipHandle(src):
    #识别IP头部信息
    ret = {
        'ipHeader' : {
            'version' : src[:1],
            'ipHeaderLen' : src[1:2],
            'tos' : src[2:4],
            'totalLen' : src[4:8],
            'id' : src[8:12],
            'flagPlusOffset' : src[12:16],
            'tt' : src[16:18],
            'protocol' : htd(src[18:20]),
            'headerCheckSum' : src[20:24],
            'sourceIP' : ipAddressConvert(src[24:32]),
            'destinationIP' : ipAddressConvert(src[32:40])
        }
    }
    protocol = ret['ipHeader']['protocol']
    if protocol == '17':
        #是udp报文
        udpHeader = udpHandle(src[40:])
        ret.update(udpHeader)
    
    if protocol == '6':
        #是tcp报文
        tcpHeader = tcpHandle(src[40:])
        ret.update(tcpHeader)
    return ret

def udpHandle(src):
    ret = {
        'udpHeader' : {
            'dport' : int(src[:4], 16),
            'sport' : int(src[4:8], 16),
            'udpPacketLen' : src[8:12],
            'udpCheckSum' : src[12:16]
        }
    }
    return ret

def tcpHandle(src):
    ret = {
        'tcpHeader' : {
            'sport' : htd(src[:4]),
            'dport' : htd(src[4:8]),
            'seq' : src[8:16],
            'ack' : src[16:32],
            'ack' : src[16:24],
            'offsetFlags' : src[24:28],
            'window' : src[28:32],
            'checksum' : src[32:36],
            'up' : src[36:40],
        }
    }
    return ret

def packetHandle(buffer : str) -> dict:
    #只处理标准以太报文
    # print(buffer)
    cookedBuffer = re.sub(r'\s', '', buffer)
    print(cookedBuffer)
    packetConstruct = {
        'etHeader' : {
            'dmac' : cookedBuffer[0:12],
            'smac' : cookedBuffer[12:24],
            'ethType' : cookedBuffer[24:28]
            }
    }
    ethType = cookedBuffer[24:28]
    packetLeft = cookedBuffer[28:]

    if ethType == '8100':
        #是一个带vlan tag的报文，用dot1qHandle函数识别802.1q头，需要兼容单层tag和双层tag的情况
        dot1qHeader = dot1qHandle(packetLeft)
        packetConstruct.update(dot1qHeader)

    if ethType == '0800':
        #是IP头，用ipHandle函数识别IP头
        ipHeader = ipHandle(packetLeft)
        packetConstruct.update(ipHeader)

    if ethType == '0806':
        #是arp报文
        arpHeader = arpHandle(packetLeft)
        packetConstruct.update(arpHeader)

    return packetConstruct



def send_fragments(dst_ip, src_ip=None, iface=None):
    # 如果未指定源 IP，则使用随机的 IP
    if src_ip is None:
        src_ip = RandIP()

    # 构建 IP 头部
    ip = IP(dst=dst_ip, src=src_ip)
    
    # 构建分片的 payload 数据，设置不同的片段偏移（fragment offset）
    frag1 = ip / ICMP() / ('X' * 400)  # 第一片段
    frag2 = ip / ('Y' * 400)  # 第二片段，数据跟上一个片段无缝对接

    # 分片发送的首个片段（MF=1 表示后续还有片段）
    frag1[IP].flags = 'MF'
    frag1[IP].frag = 0  # 首个片段的偏移为0

    # 分片发送的第二个片段（MF=0 表示这是最后一个片段）
    frag2[IP].frag = 50  # 第二片段的偏移量为50个8字节单位

    print(f"Sending fragmented packets to {dst_ip}...")
    
    # 发送数据包
    print(frag1.summary())
    send(frag1, iface=iface)

    print(frag2.summary())
    send(frag2, iface=iface)
    
    print("Fragmented packets sent!")

# 使用示例
if __name__ == "__main__":
    # dst_ip = "10.113.53.203"  # 目标 IP 地址
    # src_ip = "10.113.6.84"  # 源 IP 地址（可以设为 None 使用随机 IP）

    # # 发送分片的 IP 数据包
    # if src_ip is None:
    #     src_ip = RandIP()

    # # 构建 IP 头部
    # ip = IP(dst=dst_ip, src=src_ip)
    # icmp = ICMP()
    
    # # 构建分片的 payload 数据，设置不同的片段偏移（fragment offset）
    # frag1 = ip / icmp / raw('X' * 400)  # 第一片段
    # frag2 = ip / raw('Y' * 400)  # 第二片段，数据跟上一个片段无缝对接

    # # 分片发送的首个片段（MF=1 表示后续还有片段）
    # frag1[IP].flags = 'MF'
    # frag1[IP].frag = 0  # 首个片段的偏移为0

    # # 分片发送的第二个片段（MF=0 表示这是最后一个片段）
    # frag2[IP].frag = 50  # 第二片段的偏移量为50个8字节单位

    # print(f"Sending fragmented packets to {dst_ip}...")
    
    # # 发送数据包
    # # print(frag1.summary())
    # # send(frag1)
    # try:
    #     wrpcap('1.pcap', frag1)
    #     wrpcap('2.pcap', frag2)
    # except Exception as e:
    #     print("Error:", e)
    
    # print("Fragmented packets sent!")


    data = '''2cab 0062 8680 c0ea c323 fe0a 0800 4500
00ca 75dc 0000 7b11 0ea7 a9fe 66a3 a9fe
ffff 008a 008a 00b6 9576 110a d246 a9fe
66a3 008a 00a0 0000 2046 4345 4a46 4445
4545 4343 4143 4143 4143 4143 4143 4143
4143 4143 4143 4141 4100 2046 4845 5046
4345 4c45 4846 4345 5046 4646 4143 4143
4143 4143 4143 4143 4142 4e00 ff53 4d42
2500 0000 0000 0000 0000 0000 0000 0000
0000 0000 0000 0000 0000 0000 1100 0006
0000 0000 0000 0000 00e8 0300 0000 0000
0000 0006 0056 0003 0001 0001 0002 0017
005c 4d41 494c 534c 4f54 5c42 524f 5753
4500 0904 da3f 0000'''

print(packetHandle(data))
