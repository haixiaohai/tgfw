import argparse
from pysnmp.hlapi import *
from pysnmp import error

def get_sysname(host, community, snmp_version, retries=1):
    # 根据SNMP版本设置参数
    if snmp_version == 'v1':
        mp_model = 0
    elif snmp_version == 'v2c':
        mp_model = 1
    else:
        raise ValueError("Unsupported SNMP version")

    # 系统名称的OID
    oid = ObjectIdentity('1.3.6.1.2.1.1.5.0')

    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=mp_model),
        UdpTransportTarget((host, 161), retries=retries),
        ContextData(),
        ObjectType(oid)
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        return None, str(errorIndication)
    elif errorStatus:
        return None, f'{errorStatus.prettyPrint()} at {errorIndex}'
    else:
        for varBind in varBinds:
            return str(varBind[1]), None

def main():
    parser = argparse.ArgumentParser(description='SNMP sysName Query Tool')
    parser.add_argument('--host', required=True, help='SNMP agent address')
    parser.add_argument('--community', default='public', help='SNMP community string')
    parser.add_argument('--version', choices=['v1', 'v2c'], required=True, help='SNMP version')
    parser.add_argument('--count', type=int, default=1, help='Number of queries to perform')
    args = parser.parse_args()

    for i in range(1, args.count + 1):
        try:
            value, error = get_sysname(args.host, args.community, args.version)
            if error:
                print(f"Attempt {i}: Failed - {error}")
            else:
                print(f"Attempt {i}: Success - sysName: {value}")
        except Exception as e:
            print(f"Attempt {i}: Failed - {str(e)}")

if __name__ == '__main__':
    main()