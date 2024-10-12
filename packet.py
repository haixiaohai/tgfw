from scapy.all import TCP, IP, send

# 修改报文的内容
# packets = rdpcap('baiyun1.cap')
# packets[0].show()

# packets[0][IP].src = '10.128.180.79'

# packets[0].show()

# wrpcap('baiyun1_1.pcap', packets)



# 生成报文
dst_ip = '10.128.180.79'
dst_port = 443
src_port = 59438
tcp = TCP(sport=src_port, dport=dst_port, flags='S')
packet = IP(dst=dst_ip)/tcp

send(packet, verbose=1)