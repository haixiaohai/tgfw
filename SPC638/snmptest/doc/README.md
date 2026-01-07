# 1、安装环境 pip install -r requriements.txt。
建议使用虚拟环境执行,python版本需要时用3.11
可以使用conda创建虚拟环境
conda create -n snmp_test python=3.11 -c conda-forge
conda activate snmp_test
cd <snmp_test目录>
pip install -r requriements.tx

# 2、 准备mib文件
   建mib文件以yaml格式写入mib目录下
   mib文件在测试工具中以文件路径和yaml节点路径的格式调用，详情参考test_snmpv1v2.py和test_snmpv3.py

# 3、snmp测试
## 3.1 snmpv1v2测试
1. snmpv1v2测试防范在test_snmpv1v2.py文件中   
2. 根据需求实现测试方法，参考文档中已实现的get和set方法
3. 将需要执行的测试防范写入到最下面的if __name__ == '__main__':中执行，不执行的测试方法需要注释掉。

## 3.2 snmpv3测试
1. snmpv1v2测试防范在test_snmpv3.py文件中   
2. 根据需求实现测试方法，参考文档中已实现的get和set方法
3. 将需要执行的测试防范写入到最下面的if __name__ == '__main__':中执行，不执行的测试方法需要注释掉。
注意：多次snmp测试可能导致snmp服务端的会话数量耗尽，因此在频繁调用snmp方法时仅在初次调用时间create_engine=True，之后均置为False，避免会话耗尽