import csv
import requests
import json
import time
import urllib3
from typing import List, Dict, Any, Optional

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def query_ip_geoip(ip: str) -> Optional[Dict[str, Any]]:
    """
    查询单个IP的地理位置信息
    
    Args:
        ip: 待查询的IP地址
        
    Returns:
        包含地理位置信息的字典，如果查询失败则返回None
    """
    base_url = "https://10.113.53.201/api/v1/geoip/query"
    try:
        headers = {"AuthorizationToken": "Ag$xljdVLPxIKjiiWz$KqWdIN@cqfE@qBx$zXVWcYkulqSJkARmOeic!XjSwLPo#HzKXOvWbODyZaEht!GUrPIn#F$gHvaQHceRdnBjLAYBYHAfAHelGDsLn$@!AtCsk"}  # 请替换为实际Token
        response = requests.get(f"{base_url}?ip={ip}", headers=headers, verify=False)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        if "vals" in data and len(data["vals"]) > 0:
            return data["vals"][0]
        return None
    except requests.exceptions.RequestException as e:
        print(f"查询IP {ip} 时出错: {e}")
        return None
    except json.JSONDecodeError:
        print(f"解析IP {ip} 的响应时出错，非JSON格式")
        return None

def generate_all_ips():
    """
    生成所有可能的IPv4地址
    
    Returns:
        包含所有IPv4地址的列表
    """
    # 使用生成器表达式，节省内存
    for a in range(256):
        for b in range(1,56):
            for c in range(40,256):
                for d in range(223,256):
                    yield f"{a}.{b}.{c}.{d}"

def write_to_csv(data: Dict, output_file: str) -> None:
    """
    将查询结果写入CSV文件
    
    Args:
        data: 查询结果列表
        output_file: 输出CSV文件路径
    """
    if not data:
        print("没有数据可写入")
        return
    
    fieldnames = ["ip", "country", "province", "city"]
    try:
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow({
                    "ip": item.get("ip", ""),
                    "country": item.get("country", ""),
                    "province": item.get("province", ""),
                    "city": item.get("city", "")
                })
        print(f"数据已成功写入 {output_file}")
    except Exception as e:
        print(f"写入CSV文件时出错: {e}")

def main():
    # 配置信息
    output_file = "ip_geoip_result.csv"    
    delay = float(0.001)
    
    # 生成所有IP地址
    ips = generate_all_ips()
       
    # 查询IP信息
    results = []
    processed_count = 0
    save_interval = 1000  # 每查询1000个IP保存一次结果
    
    for i, ip in enumerate(ips, 1):
        result = query_ip_geoip(ip)
        if result:
            # 只提取需要的字段
            filtered = {
                "ip": result.get("ip", ""),
                "country": result.get("country", ""),
                "province": result.get("province", ""),
                "city": result.get("city", "")
            }
            results.append(filtered)

        processed_count += 1
        if processed_count % save_interval == 0:
            print(f"已处理 {processed_count} 个IP，临时保存结果...")
            write_to_csv(results, output_file)

    
    # 写入最终结果
    write_to_csv(results, output_file)

if __name__ == "__main__":
    main()