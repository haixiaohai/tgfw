from src.core.snmp.v3 import SNMPv3Tester
from pysnmp.hlapi import ObjectType, ObjectIdentity, OctetString, Integer32
import dill
import os
from pysnmp.hlapi import SnmpEngine
from typing import BinaryIO
oid_typs= [SNMPv3Tester.OID_TYPE_TABLE, SNMPv3Tester.OID_TYPE_SCALAR, SNMPv3Tester.OID_TYPE_SCALAR_1]

def save_engine(engine, path='snmp_engine.pkl'):
    with open(path, 'wb') as f:
        dill.dump(engine, f)

def load_engine(create_engine, path='snmp_engine.pkl'):
    if create_engine:
        engine = SnmpEngine()
        save_engine(engine)
    else:
        with open(path, 'rb') as f:
            engine = dill.load(f)
    return engine


def test_snmpv3_get(tester):
    # node = 'swVersionUpdateTable.swUpdateFilePath'
    node = 'mib_2.system.sysName'
    print(tester.get(node))


def test_snmpv3_set(tester):
    nodes = {
        'mib_2.system.sysName': "test1238",
        'mib_2.system.sysLocation': "chongqing33"
    }
    tester.set(nodes, oid_type=SNMPv3Tester.OID_TYPE_SCALAR)
    # tester.set(nodes, oid_type=SNMPv3Tester.OID_TYPE_TABLE)
    for key in nodes.keys():
        print(tester.get(key))

def test_snmpv3_dev_tgfw(host, username, create_engine, auth_key,priv_key,auth_protocol,priv_protocol):


    engine = load_engine(create_engine)
    tester = SNMPv3Tester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, username=username, engine=engine,
                          auth_key=auth_key, priv_key=priv_key,
                          auth_protocol=auth_protocol, priv_protocol=priv_protocol)
    # 重启
    nodes_reboot = {'devConfigTable.devReset': OctetString('1')}
    nodes_shutdown = {'devConfigTable.devShutdown': OctetString('1')}
    nodes_time = {'devConfigTable.devSettime': OctetString('2025-5-9 14:42:00')}

    # oid_type = SNMPv3Tester.OID_TYPE_TABLE   # table形式set，不会在oid后面添加.0
    oid_type = SNMPv3Tester.OID_TYPE_SCALAR    # scalar标量形式set，会在oid后面添加.0

    tester.set(nodes_time, oid_type=oid_type)
    for key in nodes_time.keys():
        print(tester.get(key))



def test_snmpv3_tgfw_update(host, username, create_engine, auth_key,priv_key,auth_protocol,priv_protocol):

    engine = load_engine(create_engine)
    tester = SNMPv3Tester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, username=username, engine=engine,
                          auth_key=auth_key, priv_key=priv_key,
                          auth_protocol=auth_protocol, priv_protocol=priv_protocol)
    # 重启
    swFtpAddress = {'swVersionUpdateTable.swFtpAddress': OctetString('101.113.53.233')}
    swFtpPort = {'swVersionUpdateTable.swFtpPort': Integer32(65534)}
    swFtpUsername = {'swVersionUpdateTable.swFtpUsername': OctetString('tgfwxxx')}
    swUpdateFileMD5 = {'swVersionUpdateTable.swUpdateFileMD5': OctetString('de449d9b9eaf4904b338adffc2d1f0d5')}
    swUpdateFilePath = {'swVersionUpdateTable.swUpdateFilePath': OctetString(
        'ftp://10.113.53.28/ngfw/images/V6R01C00SPC638B001/TGFW-V6R01C00SPC638B002-arm-upgrade-release-20250429165302.dat')}
    swBSName = {'swVersionUpdateTable.swBSName': OctetString('CPU')}
    swModuleName = {'swVersionUpdateTable.swModuleName': OctetString('算法实现FPGA'.encode('utf-8'))}
    swUpdateType = {'swVersionUpdateTable.swUpdateType': OctetString('4')}
    swVersion = {'swVersionUpdateTable.swVersion': OctetString('V1R6C00333')}

    # oid_type = SNMPv3Tester.OID_TYPE_TABLE   # table形式set，不会在oid后面添加.0
    oid_type = SNMPv3Tester.OID_TYPE_SCALAR    # scalar标量形式set，会在oid后面添加.0

    for _ in [swFtpAddress,swFtpPort,swFtpUsername,swUpdateFileMD5,swUpdateFilePath,swBSName,swModuleName,swUpdateType,swVersion]:
        tester.set(_, oid_type=oid_type)
        for key in _.keys():
            print(tester.get(key))



def test_snmpv3_tgfw_1213_separate(host, username, create_engine, auth_key,priv_key,auth_protocol,priv_protocol):
    engine = load_engine(create_engine)
    tester = SNMPv3Tester(mib_yaml_path='./mib/rfc1213.yaml', host=host, username=username, engine=engine,
                          auth_key=auth_key, priv_key=priv_key,
                          auth_protocol=auth_protocol, priv_protocol=priv_protocol)
    # 重启
    sysName = {'mib_2.system.sysName': OctetString('TGFW')}
    sysContact = {'mib_2.system.sysContact': OctetString('123')}
    sysLocation = {'mib_2.system.sysLocation': OctetString('重庆'.encode('utf-8'))}

    # oid_type = SNMPv3Tester.OID_TYPE_TABLE   # table形式set，不会在oid后面添加.0
    oid_type = SNMPv3Tester.OID_TYPE_SCALAR    # scalar标量形式set，会在oid后面添加.0
    # oid_type = SNMPv3Tester.OID_TYPE_SCALAR_1    # scalar标量形式set，会在oid后面添加.1

    test_obj = sysContact

    print(f"set {test_obj.keys()},value {test_obj.values()}. \n response is : {tester.set(test_obj, oid_type=oid_type, timeout=1.0)}")
    for key in test_obj.keys():
        for ot in oid_typs:
            print(f"get {key}: {tester.get(key, oid_type=ot)}")
    print('-------------------------------')

def test_snmpv2_tgfw_1213_separate_batch(host, username, create_engine, auth_key,priv_key,auth_protocol,priv_protocol):
    engine = load_engine(create_engine)
    tester = SNMPv3Tester(mib_yaml_path='./mib/rfc1213.yaml', host=host, username=username, engine=engine,
                          auth_key=auth_key, priv_key=priv_key,
                          auth_protocol=auth_protocol, priv_protocol=priv_protocol)
    # 重启
    sysName = [{'mib_2.system.sysName': OctetString('TGFW')},
               {'mib_2.system.sysName': OctetString('TGFW0')},
               {'mib_2.system.sysName': OctetString('TGFW1')}]
    sysContact = [{'mib_2.system.sysContact': OctetString('123')},
               {'mib_2.system.sysContact': OctetString('456')},
               {'mib_2.system.sysContact': OctetString('789')}]
    sysLocation = [{'mib_2.system.sysLocation': OctetString('成都'.encode('utf-8'))},
               {'mib_2.system.sysLocation': OctetString('chengdu')},
               {'mib_2.system.sysLocation': OctetString('chongqing')}]

    for _, st in zip(sysLocation, oid_typs):
        print(f"set {_.keys()}: {tester.set(_, oid_type=st)}")
        for key in _.keys():
            for ot in oid_typs:
                print(f"get {key}: {tester.get(key, oid_type=ot)}")
        print('-------------------------------')


if __name__ == '__main__':
    host = '10.113.53.203'
    username = 'tgfw-snmp1'
    auth_key = 'Ngfw@1231'
    priv_key = 'Ngfw123!@#1'
    auth_protocol='SHA'
    priv_protocol = 'DES'

    # # # mib_yaml_path = './mib/zhognxinliangzi.yaml'
    # mib_yaml_path = './mib/rfc1213.yaml'
    # snmp_tester = SNMPv3Tester(mib_yaml_path=mib_yaml_path, host=host, username=username,
    #                            auth_key=auth_key, priv_key=priv_key,
    #                            auth_protocol=auth_protocol, priv_protocol=priv_protocol)
    # # 1、 测试get
    # # test_snmpv3_get(snmp_tester)
    #
    # # 2、 测试set
    # test_snmpv3_set(snmp_tester)

    # 3、测试tgfw的devconfig
    # test_snmpv3_dev_tgfw(host=host, username=username, create_engine=False, auth_key=auth_key, priv_key=priv_key, auth_protocol=auth_protocol, priv_protocol=priv_protocol)

    # 4、测试升级参数
    # test_snmpv3_tgfw_update(host=host, username=username, create_engine=False, auth_key=auth_key, priv_key=priv_key, auth_protocol=auth_protocol, priv_protocol=priv_protocol)

    # 5、测试1213参数
    test_snmpv3_tgfw_1213_separate(host=host, username=username, create_engine=True, auth_key=auth_key, priv_key=priv_key, auth_protocol=auth_protocol, priv_protocol=priv_protocol)
    # test_snmpv3_tgfw_1213_separate(host='10.113.53.203', username=username, create_engine=True, auth_key=auth_key, priv_key=priv_key, auth_protocol=auth_protocol, priv_protocol=priv_protocol)