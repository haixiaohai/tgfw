import codecs
import random
import sys
import time

from src.core.snmp.v1v2c import *
from pysnmp.hlapi import ObjectType, ObjectIdentity, OctetString

# oid_type = SNMPv1v2cTester.OID_TYPE_TABLE   # table形式set，不会在oid后面添加.0
# oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR    # scalar标量形式set，会在oid后面添加.0
# oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR_1    # scalar标量形式set，会在oid后面添加.1
oid_typs= [SNMPv1v2cTester.OID_TYPE_TABLE, SNMPv1v2cTester.OID_TYPE_SCALAR, SNMPv1v2cTester.OID_TYPE_SCALAR_1]


def test_snmpv1v2_get(tester):
    node = 'swVersionUpdateTable.swUpdateFilePath'
    print(tester.get(node))


def test_snmpv1v2_set(host,community,version):
    nodes = {
        'mib_2.system.sysName': "test12",
        # 'mib_2.system.sysLocation': "chongqing33"
    }
    mib_yaml_path='./mib/rfc1213.yaml'
    tester = SNMPv1v2cTester(mib_yaml_path=mib_yaml_path, host=host, community=community, version=version)
    tester.set(nodes, oid_type=SNMPv1v2cTester.OID_TYPE_SCALAR)
    # tester.set(nodes, oid_type=SNMPv1v2cTester.OID_TYPE_TABLE)
    for key in nodes.keys():
        print(tester.get(key))

def test_snmpv2_tgfw_1213_separate(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/rfc1213.yaml', host=host, community=community,
                             version=version)
    # 重启
    sysName = {'mib_2.system.sysName': OctetString('TGFW')}
    sysContact = {'mib_2.system.sysContact': OctetString('TGFW3')}
    sysLocation = {'mib_2.system.sysLocation': OctetString('成都2',encoding='utf-8')}
    # sysLocation = {'mib_2.system.sysLocation': OctetString('chongqing')}

    # oid_type = SNMPv1v2cTester.OID_TYPE_TABLE   # table形式set，不会在oid后面添加.0
    # oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR  # scalar标量形式set，会在oid后面添加.0
    oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR_1    # scalar标量形式set，会在oid后面添加.1

    test_obj = sysContact
    key = list(test_obj.keys())[0]
    value = test_obj.get(key)
    print(f"set:{key}, value:{value}. \n response is : {tester.set(test_obj, oid_type=oid_type, timeout=2.0)}")
    for key in test_obj.keys():
        for ot in oid_typs:
            rs = tester.get(key, oid_type=ot)
            print(f"get {key}: {rs}")
    print('-------------------------------')

def test_snmpv2_tgfw_1213_separate_batch(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/rfc1213.yaml', host=host, community=community,
                             version=version)
    # 重启
    sysName = [{'mib_2.system.sysName': OctetString('TGFW')},
               {'mib_2.system.sysName': OctetString('TGFW0')},
               {'mib_2.system.sysName': OctetString('TGFW1')}]
    sysContact = [{'mib_2.system.sysContact': OctetString('TGFW')},
                  {'mib_2.system.sysContact': OctetString('TGFW0')},
                  {'mib_2.system.sysContact': OctetString('TGFW1')}]
    sysLocation = [{'mib_2.system.sysLocation': OctetString('1成都1'.encode('utf-8'))},
                   {'mib_2.system.sysLocation': OctetString('chengdu')},
                   {'mib_2.system.sysLocation': OctetString('1重庆1'.encode('utf-8'))}]

    for _, st in zip(sysContact, oid_typs):
        # print(f"set {_.keys()}: {tester.set(_, oid_type=st)}")
        for key in _.keys():
            for ot in oid_typs:
                print(f"get {key}: {tester.get(key, oid_type=ot)}")
        print('-------------------------------')

def test_snmpv2_tgfw_set_dev_batch(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    # 重启
    devReset = {'devConfigTable.devReset': OctetString('100')}
    devShutdown = {'devConfigTable.devShutdown': OctetString('1')}
    devSettime = [{'devConfigTable.devSettime': OctetString('2025-05-27 09:00:00')},
                  {'devConfigTable.devSettime': OctetString('2026-05-27 00:00:00')},
                  {'devConfigTable.devSettime': OctetString('2027-05-27 24:00:00')}]

    # oid_type = SNMPv1v2cTester.OID_TYPE_TABLE   # table形式set，不会在oid后面添加.0
    # oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR    # scalar标量形式set，会在oid后面添加.0
    oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR_1    # scalar标量形式set，会在oid后面添加.0

    for _,st in zip(devSettime,oid_typs):
        print(f"set {_.keys()},value {list(_.values())[0][-1]}. \n response is : {tester.set(_, oid_type=st)}")
        for key in _.keys():
            for ot in oid_typs:
                print(f"get {key}: {tester.get(key, oid_type=ot)}")
        print('-------------------------------')

def test_snmpv2_tgfw_set_dev(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    # 重启
    devReset = {'devConfigTable.devReset': OctetString('100')}
    devShutdown = {'devConfigTable.devShutdown': OctetString('0')}
    devSettime = {'devConfigTable.devSettime': OctetString('2025-06-01 09:00:00')}

    # oid_type = SNMPv1v2cTester.OID_TYPE_TABLE   # table形式set，不会在oid后面添加.0
    oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR    # scalar标量形式set，会在oid后面添加.0
    # oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR_1    # scalar标量形式set，会在oid后面添加.1

    test_obj = devSettime

    print(f"set {test_obj.keys()},value {test_obj.values()}. \n response is : {tester.set(test_obj, oid_type=oid_type, timeout=6.0)}")
    for key in test_obj.keys():
        for ot in oid_typs:
            print(f"get {key}: {tester.get(key, oid_type=ot)}")
    print('-------------------------------')

def test_snmpv2_tgfw_set_dev_invalid(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    # 重启
    devReset = {'devConfigTable.devReset': Integer32(100)}
    devShutdown = {'devConfigTable.devShutdown': Integer32('1')}
    devSettime = {'devConfigTable.devSettime': Integer32('65535')}

    # oid_type = SNMPv1v2cTester.OID_TYPE_TABLE   # table形式set，不会在oid后面添加.0
    oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR    # scalar标量形式set，会在oid后面添加.0
    # oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR_1    # scalar标量形式set，会在oid后面添加.1

    test_obj = devShutdown

    print(f"set {test_obj.keys()},value {test_obj.values()}. \n response is : {tester.set(test_obj, oid_type=oid_type, timeout=6.0)}")
    for key in test_obj.keys():
        for ot in oid_typs:
            print(f"get {key}: {tester.get(key, oid_type=ot)}")
    print('-------------------------------')

def test_snmpv2_tgfw_update_separate(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    # 重启
    swFtpAddress = {'swVersionUpdateTable.swFtpAddress': OctetString('a'*255)}
    swFtpPort = {'swVersionUpdateTable.swFtpPort': Integer32(random.randint(1,65535))}
    swFtpUsername = {'swVersionUpdateTable.swFtpUsername': OctetString('A'*255)}
    swFtpPassword = {'swVersionUpdateTable.swFtpPassword': OctetString('x'*255)}
    swUpdateFileMD5 = {'swVersionUpdateTable.swUpdateFileMD5': OctetString('a'*32270)}
    swUpdateFilePath = {'swVersionUpdateTable.swUpdateFilePath': OctetString('f'*255)}
    swProgress = {'swVersionUpdateTable.swProgress': Integer32(1)}
    swUpdateResult = {'swVersionUpdateTable.swUpdateResult': OctetString('success')}
    swUpdateStatus = {'swVersionUpdateTable.swUpdateStatus': OctetString('1')}
    swBSName = {'swVersionUpdateTable.swBSName': OctetString('f'*255)}
    swModuleName = {'swVersionUpdateTable.swModuleName': OctetString('systemupgrade')}
    swUpdateType = {'swVersionUpdateTable.swUpdateType': OctetString('FPGA')}
    swVersion = {'swVersionUpdateTable.swVersion': OctetString('a'*64)}

    # oid_type = SNMPv1v2cTester.OID_TYPE_TABLE   # table形式set，不会在oid后面添加.0
    oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR  # scalar标量形式set，会在oid后面添加.0
    # oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR_1    # scalar标量形式set，会在oid后面添加.1

    test_obj = swUpdateFileMD5

    print(f"set {test_obj.keys()},value {test_obj.values()}. \n response is : {tester.set(test_obj, oid_type=oid_type, timeout=6.0)}")
    for key in test_obj.keys():
        for ot in oid_typs:
            print(f"get {key}: {tester.get(key, oid_type=ot)}")
    print('-------------------------------')

def test_snmpv2_tgfw_update_separate_valid_batch(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    # 重启
    swFtpAddress = [{'swVersionUpdateTable.swFtpAddress': OctetString('a'*255)},{'swVersionUpdateTable.swFtpAddress': OctetString('123')},{'swVersionUpdateTable.swFtpAddress': OctetString('101.113.53.255')}]
    swFtpPort = [{'swVersionUpdateTable.swFtpPort': Integer32(random.randint(1,65535))},{'swVersionUpdateTable.swFtpPort': Integer32(0)},{'swVersionUpdateTable.swFtpPort': Integer32(65536)}]
    swFtpUsername = [{'swVersionUpdateTable.swFtpUsername': OctetString('A'*255)},{'swVersionUpdateTable.swFtpUsername': OctetString('123')},{'swVersionUpdateTable.swFtpUsername': OctetString('pwtg@./3')}]
    swFtpPassword = [{'swVersionUpdateTable.swFtpPassword': OctetString('x'*255)},{'swVersionUpdateTable.swFtpPassword': OctetString('123')},{'swVersionUpdateTable.swFtpPassword': OctetString('pwtg@./3')}]
    swUpdateFileMD5 = [{'swVersionUpdateTable.swUpdateFileMD5': OctetString('a'*33)},{'swVersionUpdateTable.swUpdateFileMD5': OctetString('123456')},{'swVersionUpdateTable.swUpdateFileMD5': OctetString('de449d9b9eaf4904b338adffc2d1f0d49')}]
    swUpdateFilePath = [{'swVersionUpdateTable.swUpdateFilePath': OctetString('f'*255)},
                        {'swVersionUpdateTable.swUpdateFilePath': OctetString('32')},
                        {'swVersionUpdateTable.swUpdateFilePath': OctetString('ftp://10.113.53.28/ngfw/images/V6R01C00SPC638B001/TGFW-V6R01C00SPC638B003-arm-upgrade-release-20250429165302.dat')}]
    swProgress = [{'swVersionUpdateTable.swProgress': Integer32(1)},{'swVersionUpdateTable.swProgress': Integer32(1024)},{'swVersionUpdateTable.swProgress': Integer32(65535)}]
    swUpdateResult = [{'swVersionUpdateTable.swUpdateResult': OctetString('success')},{'swVersionUpdateTable.swUpdateResult': OctetString('updating')},{'swVersionUpdateTable.swUpdateResult': OctetString('failed')}]
    swUpdateStatus = [{'swVersionUpdateTable.swUpdateStatus': OctetString('1')},{'swVersionUpdateTable.swUpdateStatus': OctetString('2')},{'swVersionUpdateTable.swUpdateStatus': OctetString('3')}]
    swBSName = [{'swVersionUpdateTable.swBSName': OctetString('f'*255)},{'swVersionUpdateTable.swBSName': OctetString('1')},{'swVersionUpdateTable.swBSName': OctetString('SNMP')}]
    swModuleName = [{'swVersionUpdateTable.swModuleName': OctetString('systemupgrade')},{'swVersionUpdateTable.swModuleName': OctetString('appupgrade')},{'swVersionUpdateTable.swModuleName': OctetString('urlupgrade')}]
    swUpdateType = [{'swVersionUpdateTable.swUpdateType': OctetString('FPGA')},{'swVersionUpdateTable.swUpdateType': OctetString('CPU')},{'swVersionUpdateTable.swUpdateType': OctetString('内核'.encode('utf-8'))}]
    swVersion = [{'swVersionUpdateTable.swVersion': OctetString('a'*64)},{'swVersionUpdateTable.swVersion': OctetString('123')},{'swVersionUpdateTable.swVersion': OctetString('V6R01C00SPC638B003')}]

    for _,st in zip(swVersion,oid_typs):
        print(f"set {_.keys()}: {tester.set(_, oid_type=st)}")
        for key in _.keys():
            for ot in oid_typs:
                print(f"get {key}: {tester.get(key,oid_type=ot)}")
        print('-------------------------------')

def test_snmpv2_tgfw_update_separate_invalid_batch(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    # 重启
    swFtpAddress = [{'swVersionUpdateTable.swFtpAddress': OctetString('127.0.0.1',encoding='utf-8')},{'swVersionUpdateTable.swFtpAddress': OctetString('1.256.0.0')},{'swVersionUpdateTable.swFtpAddress': OctetString('224.255.255.253')}]
    swFtpPort = [{'swVersionUpdateTable.swFtpPort': OctetString('1'*10072)},{'swVersionUpdateTable.swFtpPort': Integer32(0)},{'swVersionUpdateTable.swFtpPort': Integer32(65536)}]
    swFtpUsername = [{'swVersionUpdateTable.swFtpUsername': OctetString('A'*256)},{'swVersionUpdateTable.swFtpUsername': Integer32('123')},{'swVersionUpdateTable.swFtpUsername': OctetString('pwtg@./3')}]
    swFtpPassword = [{'swVersionUpdateTable.swFtpPassword': OctetString('x'*255)},{'swVersionUpdateTable.swFtpPassword': Integer32('123')},{'swVersionUpdateTable.swFtpPassword': OctetString('pwtg@./3')}]
    swUpdateFileMD5 = [{'swVersionUpdateTable.swUpdateFileMD5': OctetString('a'*32270)},{'swVersionUpdateTable.swUpdateFileMD5': Integer32('123456')},{'swVersionUpdateTable.swUpdateFileMD5': OctetString('')}]
    swUpdateFilePath = [{'swVersionUpdateTable.swUpdateFilePath': OctetString('f'*255)},
                        {'swVersionUpdateTable.swUpdateFilePath': Integer32('32')},
                        {'swVersionUpdateTable.swUpdateFilePath': OctetString('ftp://10.113.53.28/ngfw/images/V6R01C00SPC638B001/TGFW-V6R01C00SPC638B003-arm-upgrade-release-20250429165302.dat')}]
    swProgress = [{'swVersionUpdateTable.swProgress': Integer32(1)},{'swVersionUpdateTable.swProgress': Integer32(1024)},{'swVersionUpdateTable.swProgress': Integer32(65535)}]
    swUpdateResult = [{'swVersionUpdateTable.swUpdateResult': OctetString('success')},{'swVersionUpdateTable.swUpdateResult': OctetString('updating')},{'swVersionUpdateTable.swUpdateResult': OctetString('failed')}]
    swUpdateStatus = [{'swVersionUpdateTable.swUpdateStatus': OctetString('1')},{'swVersionUpdateTable.swUpdateStatus': OctetString('2')},{'swVersionUpdateTable.swUpdateStatus': OctetString('3')}]
    swBSName = [{'swVersionUpdateTable.swBSName': OctetString('f'*256)},{'swVersionUpdateTable.swBSName': Integer32('1')},{'swVersionUpdateTable.swBSName': OctetString('SNMP')}]
    swModuleName = [{'swVersionUpdateTable.swModuleName': OctetString('f'*255)},{'swVersionUpdateTable.swModuleName': Integer32('123')},{'swVersionUpdateTable.swModuleName': OctetString('urlupgrade')}]
    swUpdateType = [{'swVersionUpdateTable.swUpdateType': OctetString('FPGA')},{'swVersionUpdateTable.swUpdateType': OctetString('CPU')},{'swVersionUpdateTable.swUpdateType': OctetString('内核1'.encode('utf-8'))}]
    swVersion = [{'swVersionUpdateTable.swVersion': OctetString('b'*65)},{'swVersionUpdateTable.swVersion': Integer32('123')},{'swVersionUpdateTable.swVersion': OctetString('')}]

    for _,st in zip(swFtpAddress,oid_typs):
        key = list(_.keys())[0]
        value = _.get(key)
        # value = value if not isinstance(value,OctetString) else value.prettyPrint()
        print(f"set key:{key},\n"
              f"set value:{value},\n"
              # f"type:{type(value)}"
              f" response:{tester.set(_, oid_type=st)}")
        for key in _.keys():
            for ot in oid_typs:
                print(f"get {key}: {tester.get(key,oid_type=ot)}")
        print('-------------------------------')

def test_snmpv2_tgfw_update(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    swFtpAddress = {'swVersionUpdateTable.swFtpAddress': OctetString('10.113.53.105')}
    swFtpPort = {'swVersionUpdateTable.swFtpPort': Integer32(22)}
    swFtpUsername = {'swVersionUpdateTable.swFtpUsername': OctetString('root')}
    swFtpPassword = {'swVersionUpdateTable.swFtpPassword': OctetString('ngfw123!@#')}
    swUpdateFileMD5 = {'swVersionUpdateTable.swUpdateFileMD5': OctetString('02e303707b0a83f645e3a88ed412eeab')}
    swUpdateFilePath = {'swVersionUpdateTable.swUpdateFilePath': OctetString('/userdata/package/202504/DAS-TGFW-AV-20250417.dat')}
    swBSName = {'swVersionUpdateTable.swBSName': OctetString('software')}
    swModuleName = {'swVersionUpdateTable.swModuleName': OctetString('avupgrade')}  # systemupgrade, ipsupgrade, appupgrade, urlupgrade, avupgrade, tiupgrade
    swUpdateType = {'swVersionUpdateTable.swUpdateType': OctetString('CPU')}
    swVersion = {'swVersionUpdateTable.swVersion': OctetString('V6R01C00SPC638B003')}

    paras = {}
    for _ in [swFtpAddress, swFtpPort, swFtpUsername, swFtpPassword, swUpdateFileMD5, swUpdateFilePath, swBSName, swModuleName, swUpdateType, swVersion]:
        paras.update(_)

    # oid_type = SNMPv1v2cTester.OID_TYPE_TABLE  # table形式set，不会在oid后面添加.0或者.1
    oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR    # scalar标量形式set，会在oid后面添加.0
    # oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR_1    # scalar标量形式set，会在oid后面添加.1

    print(f"set {paras.keys()}: {tester.set(paras, oid_type=oid_type)}")

    # get_keys = ['swVersionUpdateTable.swUpdateResult','swVersionUpdateTable.swUpdateStatus','swVersionUpdateTable.swProgress']
    # # for _g in get_keys:
    # #     # for ot in oid_typs:
    # #     #     print(f"get {_g}: {tester.get(_g,oid_type=ot)}")
    # log_progress = {'swVersionUpdateTable.swUpdateResult':"",'swVersionUpdateTable.swUpdateStatus':"",'swVersionUpdateTable.swProgress':""}
    # for i in range(1,60000):
    #     update = False
    #     for _g in get_keys:
    #         log=f"get {_g}: {tester.get(_g, oid_type=oid_type)}"
    #         if log != log_progress.get(_g):
    #             log_progress[_g] = log
    #             update = True
    #         # print(f"get {_g}: {tester.get(_g, oid_type=oid_type)}")
    #     delay = 3
    #     time.sleep(delay)
    #     if update:
    #         print(f"经过了{delay * i} 秒")
    #         for k in log_progress.keys():
    #             print(log_progress.get(k))
    #         print("##############")
    print('-------------------------------')


def test_snmpv2_tgfw_log_separate(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    # 重启
    logFtpAddress = [{'logManagementTable.logFtpAddress': OctetString('101.113.53.236')},{'logManagementTable.logFtpAddress': OctetString('101.113.53.0')},{'logManagementTable.logFtpAddress': OctetString('101.113.53.255')}]
    logFtpPort = [{'logManagementTable.logFtpPort': Integer32(1)},{'logManagementTable.logFtpPort': Integer32(1024)},{'logManagementTable.logFtpPort': Integer32(65535)}]
    logFtpUsername = [{'logManagementTable.logFtpUsername': OctetString('a?b')},{'logManagementTable.logFtpUsername': OctetString('a@')},{'logManagementTable.logFtpUsername': OctetString('ab/')}]
    logFtpPassword = [{'logManagementTable.logFtpPassword': OctetString('a'*255)},{'logManagementTable.logFtpPassword': OctetString('123')},{'logManagementTable.logFtpPassword': OctetString('pwtfgwtester3?')}]
    logStartDate = [{'logManagementTable.logStartDate': OctetString('2025-05-15+0000')},{'logManagementTable.logStartDate': OctetString('2099-01-01+1200')},{'logManagementTable.logStartDate': OctetString('2001-12-31')}]
    logEndDate = [{'logManagementTable.logEndDate': OctetString('1970-01-01+0000')},{'logManagementTable.logEndDate': OctetString('9999-12-31+1200')},{'logManagementTable.logEndDate': OctetString('2025-05-15+0800')}]
    logTransferStatus = [{'logManagementTable.logTransferStatus': OctetString('transfer')},{'logManagementTable.logTransferStatus': OctetString('failed')},{'logManagementTable.logTransferStatus': OctetString('success')}]
    logFilePath = [{'logManagementTable.logFilePath': OctetString('logfile_'+'a'*1009+'.tar.gz')},{'logManagementTable.logFilePath': OctetString('logfile_'+'a1'*10+'.tar.gz')},{'logManagementTable.logFilePath': OctetString('logfile_2015-05-01_2015-05-04.tar.gz')}]
    logFileMD5 = [{'logManagementTable.logFileMD5': OctetString('de449d9b9eaf4904b338adffc2d1f0d41')},{'logManagementTable.logFileMD5': OctetString('de449d9b9eaf4904b338adffc2d1f0d42')},{'logManagementTable.logFileMD5': OctetString('de449d9b9eaf4904b338adffc2d1f0d43')}]
    logFileProgress = [{'logManagementTable.logFileProgress': OctetString('1')},{'logManagementTable.logFileProgress': OctetString('2')},{'logManagementTable.logFileProgress': OctetString('3')}]

    for _,st in zip(logFtpUsername,oid_typs):
        print(f"set {_.keys()}: {tester.set(_, oid_type=st)}")
        for key in _.keys():
            for ot in oid_typs:
                print(f"get {key}: {tester.get(key,oid_type=ot)}")
        print('-------------------------------')

def test_snmpv2_tgfw_log_separate_invalid_batch(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    # 重启
    logFtpAddress = [{'swVersionUpdateTable.swFtpAddress': OctetString('0.0.0.0',encoding='utf-8')},{'swVersionUpdateTable.swFtpAddress': OctetString('127.0.0.1')},{'swVersionUpdateTable.swFtpAddress': OctetString('224.255.255.25')}]
    logFtpPort = [{'logManagementTable.logFtpPort': Integer32(1)},{'logManagementTable.logFtpPort': Integer32(1024)},{'logManagementTable.logFtpPort': Integer32(65535)}]
    logFtpUsername = [{'logManagementTable.logFtpUsername': OctetString('a'*255)},{'logManagementTable.logFtpUsername': Integer32('1024')},{'logManagementTable.logFtpUsername': OctetString('tfgwtester3?')}]
    logFtpPassword = [{'logManagementTable.logFtpPassword': OctetString('a'*255)},{'logManagementTable.logFtpPassword': Integer32('123')},{'logManagementTable.logFtpPassword': OctetString('pwtfgwtester3?')}]
    logStartDate = [{'logManagementTable.logStartDate': OctetString('a'*256)},{'logManagementTable.logStartDate': Integer32('32')},{'logManagementTable.logStartDate': OctetString('2023-05-15+1200')}]
    logEndDate = [{'logManagementTable.logEndDate': OctetString('a'*256)},{'logManagementTable.logEndDate': Integer32('32')},{'logManagementTable.logEndDate': OctetString('2025-05-15+0800')}]
    logTransferStatus = [{'logManagementTable.logTransferStatus': OctetString('transfer')},{'logManagementTable.logTransferStatus': OctetString('failed')},{'logManagementTable.logTransferStatus': OctetString('success')}]
    logFilePath = [{'logManagementTable.logFilePath': OctetString('logfile_'+'a'*1010+'.tar.gz')},{'logManagementTable.logFilePath': Integer32('32')},{'logManagementTable.logFilePath': OctetString('logfile_2015-05-01_2015-05-04.tar.gz')}]
    logFileMD5 = [{'logManagementTable.logFileMD5': OctetString('de449d9b9eaf4904b338adffc2d1f0d41')},{'logManagementTable.logFileMD5': OctetString('de449d9b9eaf4904b338adffc2d1f0d42')},{'logManagementTable.logFileMD5': OctetString('de449d9b9eaf4904b338adffc2d1f0d43')}]
    logFileProgress = [{'logManagementTable.logFileProgress': OctetString('1')},{'logManagementTable.logFileProgress': OctetString('2')},{'logManagementTable.logFileProgress': OctetString('3')}]

    for _, st in zip(logFtpAddress, oid_typs):
        key = list(_.keys())[0]
        value = _.get(key)
        print(f"set key:{key},\n"
              f"set value:{value},\n"
              f" response:{tester.set(_, oid_type=st)}")
        for key in _.keys():
            for ot in oid_typs:
                print(f"get {key}: {tester.get(key, oid_type=ot)}")
        print('-------------------------------')

def test_snmpv2_tgfw_log_upload(host, community, version):
    tester = SNMPv1v2cTester(mib_yaml_path='./mib/zhognxinliangzi.yaml', host=host, community=community, version=version)
    # 写入值
    logFtpAddress = {'logManagementTable.logFtpAddress': OctetString('10.113.53.200')}
    logFtpPort = {'logManagementTable.logFtpPort': Integer32(22)}
    logFtpUsername = {'logManagementTable.logFtpUsername': OctetString('root')}
    logFtpPassword = {'logManagementTable.logFtpPassword': OctetString('ngfw123!@#')}
    logStartDate = {'logManagementTable.logStartDate': OctetString('2025-05-01+0000')}
    logEndDate = {'logManagementTable.logEndDate': OctetString('2025-05-27+0000')}
    logFilePath = {'logManagementTable.logFilePath': OctetString('/userdata/'+'logfile_'+'20250501-20250516'+'.tar.gz')}

    # 查询值
    logTransferStatus = [{'logManagementTable.logTransferStatus': OctetString('transfer')},{'logManagementTable.logTransferStatus': OctetString('failed')},{'logManagementTable.logTransferStatus': OctetString('success')}]
    logFileMD5 = {'logManagementTable.logFileMD5': OctetString('de449d9b9eaf4904b338adffc2d1f0d41')}
    logFileProgress = {'logManagementTable.logFileProgress': OctetString('1')}

    get_keys=['logManagementTable.logTransferStatus','logManagementTable.logFileMD5','logManagementTable.logFileProgress']

    paras = {}
    for _ in [logFtpAddress,logFtpPort,logFtpUsername,logFtpPassword,logStartDate,logEndDate,logFilePath]:
        paras.update(_)

    # oid_type = SNMPv1v2cTester.OID_TYPE_TABLE  # table形式set，不会在oid后面添加.0或者.1
    oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR    # scalar标量形式set，会在oid后面添加.0
    # oid_type = SNMPv1v2cTester.OID_TYPE_SCALAR_1    # scalar标量形式set，会在oid后面添加.1

    print(f"set {paras.keys()}: {tester.set(paras, oid_type=oid_type)}")
    for i in range(1, 60):
        for _g in get_keys:
            print(f"get {_g}: {tester.get(_g, oid_type=oid_type)}")
        time.sleep(0.5)
        print('      ####################')
    print('-------------------------------')



if __name__ == '__main__':
    # sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    # host = '10.113.53.201'
    host = '10.113.53.203'
    # community = 'P@ssw0rd+T3st'
    community = '1qaz!QAZ'
    snmp_version = 'v2c'
    # mib_yaml_path = './mib/zhognxinliangzi.yaml'
    # mib_yaml_path = './mib/rfc1213.yaml'
    # snmp_tester = SNMPv1v2cTester(mib_yaml_path=mib_yaml_path, host=host, community=community, version=snmp_version)


    # 1、 测试get
    # test_snmpv1v2_get(snmp_tester)

    # 2、 测试set
    # test_snmpv1v2_set(host=host, community=community, version=snmp_version)

    # 3、测试tgfw dev节点
    # test_snmpv2_tgfw_set_dev(host=host, community=community, version=snmp_version)
    # test_snmpv2_tgfw_set_dev_invalid(host=host, community=community, version=snmp_version)

    # 3、测试tgfw 升级节点
    # test_snmpv2_tgfw_update_separate_valid_batch(host=host, community=community, version=snmp_version)
    # test_snmpv2_tgfw_update_separate_invalid_batch(host=host, community=community, version=snmp_version)
    # test_snmpv2_tgfw_update_separate(host=host, community=community, version=snmp_version)
    test_snmpv2_tgfw_update(host=host, community=community, version=snmp_version)

    # 3、测试tgfw log节点
    # test_snmpv2_tgfw_log_separate(host=host, community=community, version=snmp_version)
    # test_snmpv2_tgfw_log_upload(host=host, community=community, version=snmp_version)
    # test_snmpv2_tgfw_log_separate_invalid_batch(host=host, community=community, version=snmp_version)

    # 4、 测试1213
    # test_snmpv2_tgfw_1213_separate(host=host, community=community, version=snmp_version)
