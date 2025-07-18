import socket
import struct
import random
import time
import threading
import logging
from typing import List, Dict, Tuple, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ICMPv6Type:
    DESTINATION_UNREACHABLE = 1
    PACKET_TOO_BIG = 2
    TIME_EXCEEDED = 3
    PARAMETER_PROBLEM = 4
    ECHO_REQUEST = 128
    ECHO_REPLY = 129
    ROUTER_SOLICITATION = 133
    ROUTER_ADVERTISEMENT = 134
    NEIGHBOR_SOLICITATION = 135
    NEIGHBOR_ADVERTISEMENT = 136
    REDIRECT_MESSAGE = 137
    MLD_LISTENER_QUERY = 130
    MLD_LISTENER_REPORT = 131
    MLD_LISTENER_DONE = 132

class ICMPv6Fuzzer:
    def __init__(self, target_ip: str, interface: str = None, timeout: int = 2):
        self.target_ip = target_ip
        self.interface = interface
        self.timeout = timeout
        self.socket = None
        self.stop_event = threading.Event()
        self.results = []
        self.setup_socket()
        
    def setup_socket(self) -> None:
        """创建原始套接字用于发送和接收ICMPv6包"""
        try:
            # 创建ICMPv6原始套接字
            self.socket = socket.socket(
                socket.AF_INET6, 
                socket.SOCK_RAW, 
                socket.IPPROTO_ICMPV6
            )
            self.socket.settimeout(self.timeout)
            
            # 如果指定了接口，则设置套接字选项
            if self.interface:
                self.socket.setsockopt(
                    socket.IPPROTO_IPV6, 
                    socket.IPV6_IFINDEX, 
                    socket.if_nametoindex(self.interface)
                )
                
            logger.info(f"套接字已创建，目标IP: {self.target_ip}")
        except Exception as e:
            logger.error(f"创建套接字失败: {e}")
            raise
    
    def generate_fuzzed_packet(self, icmp_type: int, icmp_code: int = 0) -> bytes:
        """生成模糊测试数据包"""
        # 基础头部字段
        checksum = 0
        identifier = random.randint(0, 65535)
        sequence = random.randint(0, 65535)
        
        # 基本ICMPv6头部
        icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, identifier, sequence)
        
        # 生成随机负载（16-1024字节）
        payload_length = random.randint(16, 1024)
        payload = bytes([random.randint(0, 255) for _ in range(payload_length)])
        
        # 计算校验和
        checksum = self.calculate_checksum(icmp_header + payload)
        
        # 重新打包头部，包含正确的校验和
        icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, identifier, sequence)
        
        # 根据不同的ICMPv6类型，可能需要修改数据包结构
        if icmp_type == ICMPv6Type.ECHO_REQUEST:
            # 对于ECHO请求，我们可以模糊处理更多字段
            return icmp_header + payload
        elif icmp_type == ICMPv6Type.NEIGHBOR_SOLICITATION:
            # 邻居请求需要目标地址
            target_address = socket.inet_pton(socket.AF_INET6, self.target_ip)
            return icmp_header + target_address + payload[:-16]  # 确保总长度正确
        else:
            # 其他类型的ICMPv6包
            return icmp_header + payload
    
    def calculate_checksum(self, data: bytes) -> int:
        """计算ICMPv6校验和"""
        s = 0
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                a = data[i]
                b = data[i + 1]
                s += (a + (b << 8))
            else:
                s += data[i]
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        return ~s & 0xffff
    
    def send_packet(self, packet: bytes) -> None:
        """发送数据包到目标IP"""
        try:
            self.socket.sendto(packet, (self.target_ip, 0))
        except Exception as e:
            logger.warning(f"发送数据包失败: {e}")
    
    def receive_response(self) -> Optional[Tuple[bytes, str]]:
        """接收并返回响应"""
        try:
            data, addr = self.socket.recvfrom(65535)
            return data, addr[0]
        except socket.timeout:
            return None
        except Exception as e:
            logger.warning(f"接收响应失败: {e}")
            return None
    
    def analyze_response(self, request: bytes, response: bytes) -> Dict:
        """分析响应并检测潜在问题"""
        result = {
            "request_type": request[0],
            "response_type": response[0] if response else None,
            "potential_issue": False,
            "description": ""
        }
        
        # 分析响应类型
        if not response:
            result["potential_issue"] = True
            result["description"] = "无响应，可能存在问题"
        elif response[0] == ICMPv6Type.PARAMETER_PROBLEM:
            result["potential_issue"] = True
            result["description"] = "目标返回参数问题消息"
        elif response[0] == ICMPv6Type.DESTINATION_UNREACHABLE:
            result["potential_issue"] = True
            result["description"] = "目标不可达"
        
        return result
    
    def fuzz_icmp_type(self, icmp_type: int, iterations: int = 1000) -> None:
        """对特定类型的ICMPv6消息进行模糊测试"""
        logger.info(f"开始对ICMPv6类型 {icmp_type} 进行模糊测试，迭代 {iterations} 次")
        
        for i in range(iterations):
            if self.stop_event.is_set():
                break
                
            # 生成模糊测试数据包
            packet = self.generate_fuzzed_packet(icmp_type)
            
            # 记录发送时间
            send_time = time.time()
            
            # 发送数据包
            self.send_packet(packet)
            
            # 接收响应
            response = self.receive_response()
            
            # 计算响应时间
            response_time = time.time() - send_time if response else None
            
            # 分析响应
            analysis = self.analyze_response(packet, response[0] if response else None)
            
            # 记录结果
            result = {
                "iteration": i,
                "icmp_type": icmp_type,
                "timestamp": time.time(),
                "response_time": response_time,
                "response": analysis
            }
            
            self.results.append(result)
            
            # 每100次迭代记录一次进度
            if i % 100 == 0:
                logger.info(f"进度: {i}/{iterations}")
                
            # 检测到问题时记录详细信息
            if analysis["potential_issue"]:
                logger.warning(f"可能存在问题 - 迭代 {i}: {analysis['description']}")
    
    def start(self, icmp_types: List[int] = None, iterations_per_type: int = 1000) -> None:
        """启动模糊测试"""
        if icmp_types is None:
            # 默认测试常见的ICMPv6类型
            icmp_types = [
                ICMPv6Type.ECHO_REQUEST,
                ICMPv6Type.NEIGHBOR_SOLICITATION,
                ICMPv6Type.ROUTER_SOLICITATION
            ]
            
        logger.info(f"开始ICMPv6模糊测试，目标IP: {self.target_ip}")
        
        # 为每种ICMPv6类型创建一个线程
        threads = []
        for icmp_type in icmp_types:
            thread = threading.Thread(
                target=self.fuzz_icmp_type,
                args=(icmp_type, iterations_per_type)
            )
            threads.append(thread)
            thread.start()
            
        # 等待所有线程完成
        for thread in threads:
            thread.join()
            
        logger.info(f"模糊测试完成，执行了 {len(icmp_types)} 种类型，每种类型 {iterations_per_type} 次迭代")
    
    def stop(self) -> None:
        """停止模糊测试"""
        self.stop_event.set()
        if self.socket:
            self.socket.close()
            self.socket = None
        logger.info("模糊测试已停止")
    
    def get_results(self) -> List[Dict]:
        """获取测试结果"""
        return self.results
    
    def generate_report(self, output_file: str = "icmpv6_fuzzing_report.txt") -> None:
        """生成测试报告"""
        with open(output_file, "w") as f:
            f.write(f"ICMPv6模糊测试报告 - 目标IP: {self.target_ip}\n")
            f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总测试次数: {len(self.results)}\n\n")
            
            # 统计潜在问题
            potential_issues = [r for r in self.results if r["response"]["potential_issue"]]
            
            f.write(f"潜在问题数量: {len(potential_issues)}\n\n")
            
            # 按ICMP类型分组的问题
            issues_by_type = {}
            for issue in potential_issues:
                icmp_type = issue["icmp_type"]
                if icmp_type not in issues_by_type:
                    issues_by_type[icmp_type] = []
                issues_by_type[icmp_type].append(issue)
            
            # 写入按类型分类的问题
            for icmp_type, issues in issues_by_type.items():
                f.write(f"ICMPv6类型 {icmp_type} 的问题 ({len(issues)}):\n")
                for issue in issues:
                    f.write(f"  - 迭代 {issue['iteration']}: {issue['response']['description']}\n")
                f.write("\n")
            
            f.write("=" * 50 + "\n")
            f.write("详细结果:\n")
            for result in self.results:
                f.write(f"迭代 {result['iteration']}, 类型 {result['icmp_type']}, "
                        f"响应时间: {result['response_time'] if result['response_time'] else '无响应'}\n")
                f.write(f"  结果: {result['response']['description']}\n")
                f.write("-" * 30 + "\n")
        
        logger.info(f"测试报告已生成: {output_file}")

# 示例使用
if __name__ == "__main__":
    # 目标IPv6地址
    target_ip = "2001:db8::1"
    
    # 创建模糊测试器实例
    fuzzer = ICMPv6Fuzzer(target_ip)
    
    try:
        # 启动模糊测试，测试3种ICMPv6类型，每种类型1000次迭代
        fuzzer.start(
            icmp_types=[
                ICMPv6Type.ECHO_REQUEST,
                ICMPv6Type.NEIGHBOR_SOLICITATION,
                ICMPv6Type.ROUTER_SOLICITATION
            ],
            iterations_per_type=1000
        )
        
        # 生成测试报告
        fuzzer.generate_report()
        
    except KeyboardInterrupt:
        # 捕获Ctrl+C并优雅地停止测试
        fuzzer.stop()
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        fuzzer.stop()    