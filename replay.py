from scapy.all import IP, rdpcap, Ether, send, show_interfaces, conf, sendp, TCP, UDP

# 读取数据包并回访
# show_interfaces()
packets = rdpcap("C:\\Users\Zjhon\Desktop\GW测试\应用识别测试报文\\app包\\app包\逃逸或隧道加密\\todesk\ToDesk-connect-PC.pcap")


def check_interface_status(index):
    iface = conf.ifaces.dev_from_index(index)
    try:
        # 尝试创建socket
        s = conf.L2socket(iface=iface)
        s.close()
        print(f"网卡 {iface.name} 可以正常使用")
    except Exception as e:
        print(f"网卡 {iface.name} 出现问题：{str(e)}")

# check_interface_status(8)


for pkt in packets:
    pkt[IP].src = "192.168.105.101"
    pkt[IP].dst = "192.168.107.100"
    pkt[Ether].src = "00:0E:C6:3A:8E:48"
    pkt[Ether].dst = "64:57:e5:9d:28:9a"
    pkt[IP].chksum = None

    #重新计算TCP和UDP的校验和
    if pkt.haslayer(TCP):
        pkt[TCP].chksum = None

    if pkt.haslayer(UDP):
        pkt[UDP].chksum = None
    # print(pkt[IP])

    # conf.ifaces.dev_from_index的参数是网卡的索引，索引可以通过show_interfaces查看
    sendp(pkt, iface=conf.ifaces.dev_from_index(8), verbose=True)