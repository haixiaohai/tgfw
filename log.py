# @Time    : 2024/12/24 15:38
# @Author  : qiuyu / 邱宇
# @Email   : black.qiu@dbappsecurity.com.cn
# @File    : tcp_syslog
import socket
from datetime import datetime
from string import Template
import sys
import random
import time
import threading
# import psycopg2
# from psycopg2 import sql
# from faker import Faker
 
# fake = Faker("zh_CN")
 
# 配置目标地址和端口
host = "192.168.1.5"  # 目标 IP 地址
port = 514         # 目标端口号
packet_count = 0
lock = threading.Lock()
stop_event = threading.Event()  # 用于通知线程停止
# 数据库配置
DB_CONFIG = {
    "dbname": "ngfw",
    "user": "sysdba",
    "password": "NUzIwKDfuB9@",
    "host": host,
    "port": "5866",       # 默认PostgreSQL端口
}
TABLE_NAME = "operation_logs"  # 需要检测的表名
row_count = 0
 
# random_ratio = {1: 3, 2: 3, 3: 4, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 1, 11: 1, 12: 1}
# random_ratio_list = [value*[key] for key, value in random_ratio.items()]
# print(random_ratio_list)
 
 
def generate_random_ipv4():
    """
    生成一个随机的IPv4地址
 
    返回:
        str: 格式为'xxx.xxx.xxx.xxx'的随机IP地址字符串
    """
    # 生成四个0-255之间的随机整数
    octets = [str(random.randint(0, 255)) for _ in range(4)]
    # 用点号连接四个数字
    return '.'.join(octets)
 
 
def generate_random_ip_port() -> str:
    """
    生成一个随机IP地址和端口号。
 
    Returns:
        tuple: 包含随机IP地址 (str) 和端口号 (int) 的元组。
    """
    # 随机生成IP地址
    ip = generate_random_ipv4()
    # 随机生成端口号（0-65535, 常用范围是1024-65535）
    port = random.randint(21, 65535)
    out = f'{ip}:{port}'
    return out
 
 
def generate_GBK2312():
    head = random.randint(0xb0, 0xf7)
    body = random.randint(0xa1, 0xfe)
    val = f'{head:x} {body:x}'
    str = bytes.fromhex(val).decode('gb2312')
    return str
 
 
class Priority:
    CRITICAL = 1  # 严重
    HIGH_RISK = 2 # 高危
    MEDIUM_RISK = 3 # 中危
    LOW_RISK = 4 # 低危
    INFORMATION = 5  # 信息
 
 
class SysLogPriority:
    DEBUG = 135
    INFO = 134
    WARNING = 132
    ERROR = 139
    FATAL = 138  # 致命错误
    CRITICAL = 136  # 严重错误
 
class Action:
    RECORD = 1  # 记录日志
    RELEASE = 2  # 放行
    ALARM = 3 # 告警
    DISCARD = 4 # 丢弃
    BLOCK = 5 # 阻断
    RESET = 6 # 重置
 
class Server:
    DHCP = 'dhcp'
    DNS = 'dns'
    FTP = 'ftp'
    HTTP = 'http'
    HTTPS = 'https'
    IMAP = 'imap'
    IMAPS = 'imaps'
    LDAP = 'ldap'
    POP3 = 'pop3'
    POP3S = 'pop3s'
    RDP = 'rdp'
    GRE = 'gre'
    ICMP = 'icmp'
    OSPF = 'ospf'
    RIP = 'rip'
    SNMP = 'snmp'
    SSH = 'ssh'
 
 
class UpgradeLogType:
    SYSTEM_LOG = 'system_upgrade'  # 系统升级日志
    FEATURE_LOG = 'feature_upgrade'  # 特征库升级
    PATCH_LOG = 'patch_upgrade'  # 补丁升级
 
 
class OperatorLogUserRole:
    SUPER = 'super'  # 超级管理员
    AUDIT = 'audit'  # 审计管理员
    OP = 'op'  # 系统管理员
    SEC = 'sec'  # 安全保密管理员
    AUDITOR = 'auditor'  # 安全审计员
 
class WebProtectProtectType:
    RULE = 'waf'  # 规则防护
    WEB_FILTER = 'filter'  # Web过滤
 
def get_row_count(cursor, table_name, merge=False):
    """
    获取日志的数量
    :param cursor:
    :param table_name:
    :param merge: 是否查归并日志的攻击次数，True则查询单个日志的攻击次数，False则查整个表的日志条目数
    :return:
    """
    return 0
    # if merge:
    #     sql_cmd = "SELECT count FROM {table} LIMIT 1"
    # else:
    #     sql_cmd = "SELECT COUNT(*) FROM {table}"
    # query = sql.SQL(sql_cmd).format(
    #     table=sql.Identifier(table_name)
    # )
    # cursor.execute(query)
    # return cursor.fetchone()[0]
 
 
# 入侵防御
IPS_TEMPLATE = Template(
    """<25>$date localhost snort: [1:4983701:10] [msg:"$msg"] [Classification: sql注入] [Priority: $priority] [proto:TCP] [ipport:$src -> $dst][Comm: gid=1,sid=$sid,policy_id=1,ips_id=1,priority=$priority,action=$action,is_ipv6=0,pkt_type=4, outer_vid=65535, inner_vid=65535, vsys_id=0] [Ext: {"classtype": "sql-injection","pcap_filename":""}]""")
IPS_DEFAULTS_CONF = {'date': datetime.now().strftime("%b %d %H:%M:%S"),
                     'src': '20.250.24.6:40568',
                     'dst': '192.168.8.6:443',
                     'priority': Priority.HIGH_RISK,
                     'action': Action.ALARM,
                     'sid': 4983701,
                     'msg': 'sql注入尝试'
                     }
 
AV_TEMPLATE = Template(
    """<25>$date localhost snort: [903:1:1] [msg:"(AVSCAN) AV ALERT"] [Priority: $priority] [proto:TCP] [ipport:$src -> $dst][Comm: gid=903,sid=1,policy_id=1,ips_id=0,priority=$priority,action=$action,is_ipv6=0,pkt_type=4, outer_vid=65535, inner_vid=65535, vsys_id=0] [Ext: {"filename":"$filename","filesize":5206529000,"vir_malware_name":"病毒名字随便一个","avaction":2,"app_protocol":"这是什么应用类型","protocol":6, "from":"av"}]""")
AV_DEFAULTS_CONF = {'date': datetime.now().strftime("%b %d %H:%M:%S"),
                     'src': '172.16.1.2:58724',
                     'dst': '66.58.6.2:80',
                     'priority': Priority.MEDIUM_RISK,
                     'action': Action.ALARM,
                     'from': 'av',
                     'filename': 'file.jpg'
                     }
 
CONTENT_FILTER_TEMPLATE = Template(
    """<25>$date localhost snort: [902:13:1] [msg:"(contentfilter) http 网页内容过滤"] [Priority: $priority] [proto:TCP] [ipport:$src -> $dst][Comm: gid=902,sid=13,policy_id=1,ips_id=0,priority=$priority,action=$action,is_ipv6=0,pkt_type=4, outer_vid=65535, inner_vid=65535, vsys_id=0] [Ext: {"contentfilter_type": "网页过滤(HTTP)","keyword": "病毒"}]""")
CONTENT_FILTER_CONF = {'date': datetime.now().strftime("%b %d %H:%M:%S"),
                     'src': '172.16.1.2:58724',
                     'dst': '66.58.6.2:80',
                     'priority': Priority.MEDIUM_RISK,
                     'action': Action.ALARM,
                     }
 
URL_FILTER_TEMPLATE = Template(
    """<25>$date localhost snort: [904:6:1] [msg:"(urlfilter) URL过滤预定义分类"] [Priority: $priority] [proto:TCP] [ipport:$src -> $dst][Comm: gid=904,sid=6,policy_id=1,ips_id=0,priority=$priority,action=$action,is_ipv6=0,pkt_type=4, outer_vid=65535, inner_vid=65535, vsys_id=0] [Ext: {"urlfilter_cfg": "url过滤配置aa","urlfilter_type": "毒品", "URL": "marijuanaseedbanks.com"}]""")
URL_FILTER_CONF = {'date': datetime.now().strftime("%b %d %H:%M:%S"),
                     'src': '172.16.1.2:58724',
                     'dst': '66.58.6.2:80',
                     'priority': Priority.MEDIUM_RISK,
                     'action': Action.ALARM,
                     }
 
 
APP_FILTER_TEMPLATE = Template(
    """<25>$date localhost snort: [913:1:1] [msg:"(appobjfilter) 应用过滤"] [Priority: $priority] [proto:TCP] [ipport:$src -> $dst][Comm: gid=913,sid=1,policy_id=1,ips_id=0,priority=$priority,action=$action,is_ipv6=0,pkt_type=4, outer_vid=65535, inner_vid=65535, vsys_id=0] [Ext: {"appobjfilter": "应用过滤配置","appname": "HTTP", "log": "5", "appid": "676"}]""")
APP_FILTER_CONF  = {'date': datetime.now().strftime("%b %d %H:%M:%S"),
                     'src': '172.16.1.2:58724',
                     'dst': '66.58.6.2:80',
                     'priority': Priority.MEDIUM_RISK,
                     'action': Action.ALARM,
                     }
 
FILE_FILTER_TEMPLATE = Template(
    """<25>$date localhost snort: [906:1:1] [msg:"(FileFiter) File Fiter ALERT"] [Priority: $priority] [proto:TCP] [ipport:$src -> $dst][Comm: gid=906,sid=1,policy_id=1,ips_id=0,priority=$priority,action=$action,is_ipv6=0,pkt_type=4, outer_vid=65535, inner_vid=65535, vsys_id=0] [Ext: {"filename":"viriustest.pdf","filetype":"ZIP","app_protocol":"http"}]""")
FILE_FILTER_CONF  = {'date': datetime.now().strftime("%b %d %H:%M:%S"),
                     'src': '172.16.1.2:58724',
                     'dst': '66.58.6.2:80',
                     'priority': Priority.MEDIUM_RISK,
                     'action': Action.ALARM,
                     }
 
WEB_PROTECT_TEMPLATE = Template(
    """<25>$date localhost snort: [1000000:4983701:1] [msg:"SQL 注入漏洞"] [Classification: Web Application Attack] [Priority: $priority] [proto:TCP] [ipport:$src -> $dst][Comm: gid=1000000,sid=4983701,policy_id=1,ips_id=2,priority=$priority,action=$action,is_ipv6=0,pkt_type=4, outer_vid=65535, inner_vid=65535, vsys_id=0] [Ext: {"webfilter_cfg":"WAF","hit_rule":"4983701","pcap_filename":"web_10906304529757105428.pcap","http_filename":"web_10906304529757105428.txt","protect_type":"$protect_type"}]""")
WEB_PROTECT_CONF  = {'date': datetime.now().strftime("%b %d %H:%M:%S"),
                     'src': '172.16.1.2:58724',
                     'dst': '66.58.6.2:80',
                     'priority': Priority.CRITICAL,
                     'action': Action.ALARM,
                     'protect_type': WebProtectProtectType.RULE
                     }
 
# 防暴力破解
BRUTE_FORCE_TEMPLATE = Template(
    """<25>$date localhost snort: [908:1:1] [msg:"(explosion_proof) 防爆力破解"] [Priority: $priority] [proto:TCP] [ipport:$src -> $dst][Comm: gid=908,sid=1,policy_id=$policy_id,ips_id=0,priority=$priority,action=$action,is_ipv6=0,pkt_type=4, outer_vid=65535, inner_vid=65535, vsys_id=0] [Ext: {"explsion_proof_cfg": "$cfg_name", "service": "$service", "blacktime": $blacktime}]""")
BRUTE_FORCE_DEFAULTS_CONF = {'date': datetime.now().strftime("%b %d %H:%M:%S"),
                             'src': '20.250.24.6:40568',
                             'dst': '192.168.8.6:443',
                             'priority': Priority.MEDIUM_RISK,
                             'action': Action.DISCARD,
                             'service': Server.HTTP,
                             'cfg_name': '防暴力破解规则',
                             'blacktime': 6,
                             'policy_id': 233}
# 弱密码防护
WEAK_PASSWORD_TEMPLATE = Template(
    """<25>$date localhost snort: [909:1:1] [msg:"(weakpwcheck) 弱密码防护"] [Priority: $priority] [proto:TCP] [ipport:$src -> $dst][Comm: gid=909,sid=1,policy_id=1,ips_id=0,priority=$priority,action=$action,is_ipv6=0,pkt_type=4, outer_vid=65535, inner_vid=65535, vsys_id=0] [Ext: {"weakpwcheck": "$cfg_name", "service": "$service", "user": "user1@testtgfw.com", "type": "密码长度小于等于6且仅包含字母和数字"}] """
)
WEAK_PASSWORD_DEFAULTS_CONF = {'date': datetime.now().strftime("%b %d %H:%M:%S"),
                             'src': '172.16.1.2:61042',
                             'dst': '66.58.6.2:110',
                             'service': Server.HTTP.upper(),
                             'priority': Priority.MEDIUM_RISK,
                             'action': Action.ALARM,
                             'cfg_name': '弱密码配置文件'}
 
# 系统日志
SYSLOG_TEMPLATE = Template("""<$priority>1 $date+08:00 DAS-OS tgfw_system 1086213 - - $msg""")
SYSLOG_DEFAULTS_CONF = {'date': datetime.now().isoformat(),
                        'priority': SysLogPriority.INFO,
                        'msg': '系统启动 成功'}
 
 
UPGRADE_TEMPLATE = Template("""<$priority>1 $date+08:00 DAS-OS tgfw_upgrade 2978 - - [$log_type]$msg""")
UPGRADE_DEFAULTS_CONF = {'date': datetime.now().isoformat(),
                         'priority': SysLogPriority.INFO,
                         'log_type': UpgradeLogType.SYSTEM_LOG,
                         'msg': '测试升级日志'}
 
OPERATOR_TEMPLATE = Template("""<$priority>1 $date+08:00 localhost tgfw_operation 1836 - - {"ip":"$ip","message":"$msg","user":"$user","userchar":"super","vsys":0}""")
OPERATOR_DEFAULTS_CONF = {'date': datetime.now().isoformat(),
                          'priority': SysLogPriority.INFO,
                          'msg': '测试操作日志',
                          'ip': '10.113.6.148',
                          'user': 'admin',
                          'role': OperatorLogUserRole.SUPER}
 
def send_packets(target_package=1000):
    """
    :param target_package: 在一个周期内，目标发送多少个报文
    :return:
    """
    global packet_count
    # 创建 UDP 套接字
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        while not stop_event.is_set():  # 循环发送数据
            with lock:
                if packet_count == target_package == 1:
                    stop_event.set()
                elif packet_count >= target_package:
                    continue
                else:
                    log_type_pick = random.randint(11,12)
                    # log_type_pick = 2
                    if log_type_pick == 1:
                        text_format = WEAK_PASSWORD_TEMPLATE.substitute(WEAK_PASSWORD_DEFAULTS_CONF,
                                                                        date=datetime.now().strftime("%b %d %H:%M:%S"),
                                                                        src=generate_random_ip_port(),
                                                                        dst=generate_random_ip_port(),
                                                                        service=Server.HTTPS.upper(),
                                                                        priority=Priority.HIGH_RISK,
                                                                        cfg_name='系统启动成功')
                    elif log_type_pick == 2:
                        text_format = IPS_TEMPLATE.substitute(IPS_DEFAULTS_CONF,
                                                              date=datetime.now().strftime("%b %d %H:%M:%S"),
                                                              priority=Priority.CRITICAL,
                                                              src=generate_random_ip_port(),
                                                              dst=generate_random_ip_port(),
                                                              sid=9288,
                                                              msg='入侵防御日志生成咯',
                                                              )
                    elif log_type_pick == 3:
                        text_format = AV_TEMPLATE.substitute(AV_DEFAULTS_CONF,
                                                             date=datetime.now().strftime("%b %d %H:%M:%S"),
                                                             src=generate_random_ip_port(),
                                                             dst=generate_random_ip_port(),
                                                             )
 
                    elif log_type_pick == 4:
                        text_format = CONTENT_FILTER_TEMPLATE.substitute(CONTENT_FILTER_CONF,
                                                                         date=datetime.now().strftime("%b %d %H:%M:%S"),
                                                                         src=generate_random_ip_port(),
                                                                         dst=generate_random_ip_port())
                    elif log_type_pick == 5:
                        text_format = APP_FILTER_TEMPLATE.substitute(APP_FILTER_CONF,
                                                                     date=datetime.now().strftime("%b %d %H:%M:%S"),
                                                                     src=generate_random_ip_port(),
                                                                     dst=generate_random_ip_port(),
                                                                     priority=Priority.CRITICAL)
                    elif log_type_pick == 6:
                        text_format = URL_FILTER_TEMPLATE.substitute(URL_FILTER_CONF,
                                                                     date=datetime.now().strftime("%b %d %H:%M:%S"),
                                                                     src=generate_random_ip_port(),
                                                                     dst=generate_random_ip_port())
 
                    elif log_type_pick == 7:
                        text_format = FILE_FILTER_TEMPLATE.substitute(FILE_FILTER_CONF,
                                                                      date=datetime.now().strftime("%b %d %H:%M:%S"),
                                                                      src=generate_random_ip_port(),
                                                                      dst=generate_random_ip_port())
 
                    elif log_type_pick == 8:
                        text_format = WEB_PROTECT_TEMPLATE.substitute(WEB_PROTECT_CONF,
                                                                      date=datetime.now().strftime("%b %d %H:%M:%S"),
                                                                      src=generate_random_ip_port(),
                                                                      dst=generate_random_ip_port())
 
                    elif log_type_pick == 9:
                        text_format = BRUTE_FORCE_TEMPLATE.substitute(BRUTE_FORCE_DEFAULTS_CONF,
                                                                      date=datetime.now().strftime("%b %d %H:%M:%S"),
                                                                      src=generate_random_ip_port(),
                                                                      dst=generate_random_ip_port(),
                                                                      service='postgresql',
                                                                      cfg_name="防暴力破解规则名字很长很长很长很长很长很长很长很长很长很长很长",
                                                                      priority=Priority.INFORMATION)
 
                    elif log_type_pick == 10:
                        text_format = SYSLOG_TEMPLATE.substitute(SYSLOG_DEFAULTS_CONF,
                                                                 priority=random.choice((SysLogPriority.ERROR,)),
                                                                 date=datetime.now().isoformat(),
                                                                 msg='啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊')
                    elif log_type_pick == 11:
                        text_format = UPGRADE_TEMPLATE.substitute(UPGRADE_DEFAULTS_CONF,
                                                                  date=datetime.now().isoformat(),
                                                                  priority=SysLogPriority.INFO,
                                                                  log_type=UpgradeLogType.SYSTEM_LOG,
                                                                  msg='系统启动 成功')
                    elif log_type_pick == 12:
                        text_format = OPERATOR_TEMPLATE.substitute(OPERATOR_DEFAULTS_CONF,
                                                                   date=datetime.now().isoformat(),
                                                                   priority=SysLogPriority.INFO,
                                                                   ip=generate_random_ipv4(),
                                                                   user='admin',
                                                                   msg='API添加黑名单 成功')
                    client_socket.sendto(text_format.encode(), (host, port))
                    packet_count += 1
                    sys.stdout.write(f"\rSent {packet_count} packets to {host}:{port}")
                    sys.stdout.flush()
            # client_socket.sendto("ACT=0 ID=1001-28049012 IP6=0 IN=Admin OUT= MAC=64:57:e5:12:97:86:90:f7:b2:1e:b3:14:08:00 SRC=10.113.6.148 DST=10.113.55.42 LEN=52 TOS=0x00 PREC=0x00 TTL=126 ID=1999 DF PROTO=TCP SPT=64959 DPT=20016 WINDOW=64240 RES=0x00 SYN URGP=0".encode(), (host, port))
 
            # if sent_count >= 1:
            #     break
            # time.sleep(0.001)  # 可根据需要调整发送间隔
 
 
def controller(cycle_time=1, total_cycle=-1):
    """
 
    :param cycle_time: 1个统计周期的时间，单位秒
    :param total_cycle: 目标经过多少个周期后停止
    :return:
    """
    global packet_count
    global row_count
    diff_count_list = []
    if total_cycle == -1:
        while True:
            time.sleep(cycle_time)
            with lock:
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"   {date} 最近 {cycle_time} 秒发送的报文数: {packet_count}", end='')
                packet_count = 0
                current_count = get_row_count(cursor, TABLE_NAME)
                diff_count = current_count - row_count
                print(f" {TABLE_NAME}表中总数据量为：{current_count:05}，和上一次相差：{diff_count:+05}")
                row_count = current_count
    else:
        run_count = 0
        while not stop_event.is_set():
            time.sleep(cycle_time)
            with lock:
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"   {date} 最近 {cycle_time} 秒发送的报文数: {packet_count}", end='')
                packet_count = 0
                current_count = get_row_count(cursor, TABLE_NAME)
                diff_count = current_count - row_count
                print(f" {TABLE_NAME}表中总数据量为：{current_count:05}，和上一次相差：{diff_count:+05}")
                row_count = current_count
                diff_count_list.append(diff_count)
            run_count += 1
            if run_count >= total_cycle:
                print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 循环达到目标周期 {total_cycle}s，停止发送')
                print(f"每一次检测的偏差：{diff_count_list}")
                print(f"sum:{sum(diff_count_list)}，sum(去除负数):{sum(x for x in diff_count_list if x > 0)}")
                stop_event.set()  # 通知所有线程停止
                return
 
 
# 创建并启动线程
if __name__ == "__main__":
    # 单个周期内期望本工具发送多少个报文（可能会因为性能问题达不到）
    target_package = 100
    # 单个周期的时间是多久（单位：秒）
    cycle_time = 1
    # 经过多少个周期后停止，当传入为 -1 的时候则无限循环
    total_cycle = -1
 
    # connection = psycopg2.connect(**DB_CONFIG)
    # cursor = connection.cursor()
    cursor = None
 
    controller_thread = threading.Thread(target=controller, daemon=True, kwargs={"cycle_time": cycle_time, "total_cycle": total_cycle})
    if total_cycle == 1 and target_package == 1:
        send_packets(1)
        sys.exit()
    else:
        send_thread = threading.Thread(target=send_packets, daemon=True, kwargs={"target_package": target_package})
        send_thread.start()
    controller_thread.start()
 
    # 主线程保持运行
    try:
        while True:
            time.sleep(1)
            if not send_thread.is_alive() or not controller_thread.is_alive():
                while True:
                    current_count = get_row_count(cursor, TABLE_NAME)
                    diff_count = current_count - row_count
                    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {TABLE_NAME}表中总数据量为：{current_count:05}，和上一次相差：{diff_count:+05}')
                    row_count = current_count
                    if diff_count == 0:
                        time.sleep(1.5)
                        current_count = get_row_count(cursor, TABLE_NAME)
                        diff_count = current_count - row_count
                        if diff_count == 0:
                            break
                        else:
                            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {TABLE_NAME}表中总数据量为：{current_count:05}，和上一次相差：{diff_count:+05}')
                            row_count = current_count
                    else:
                        time.sleep(0.5)
                break
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        pass