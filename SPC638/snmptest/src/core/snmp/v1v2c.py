from pysnmp.hlapi import *
from concurrent.futures import ThreadPoolExecutor
import yaml
import time
from src.utils.logger import debug_logger

class SNMPv1v2cTester:
    OID_TYPE_SCALAR = 'scalar'
    OID_TYPE_SCALAR_1 = 'scalar1'
    OID_TYPE_TABLE = 'table'

    def __init__(self, mib_yaml_path, host, community,version='v2c'):
        self.host = host
        self.community = community
        self.mib_yaml_path = mib_yaml_path
        self.version = 0 if version == "v1" else 1
        self.mib_mappings = self._load_mib_mappings(mib_yaml_path)
        
    def _load_mib_mappings(self, yaml_path=None):
        """加载MIB YAML配置文件"""
        yaml_path = yaml_path if yaml_path else self.mib_yaml_path
        with open(yaml_path, 'r',encoding='utf-8') as f:
            return yaml.safe_load(f)['mib_mappings']
    
    def _resolve_oid(self, mib_node, oid_type=None):
        """将MIB节点转换为OID"""
        debug_logger.debug(f'resolve_oid: {mib_node}')
        parts = mib_node.split('.')
        current = self.mib_mappings
        oid_parts = []
        oid_type = oid_type if oid_type else self.OID_TYPE_SCALAR
        
        for part in parts:
            if part in current:
                current = current[part]
                if isinstance(current, str):
                    if oid_type == self.OID_TYPE_TABLE:
                        oid_parts.append(current)
                    elif oid_type == self.OID_TYPE_SCALAR_1:
                        oid_parts.append(f'{current}.1')
                    else:
                        oid_parts.append(f'{current}.0')

            else:
                raise ValueError(f"Invalid MIB node: {mib_node}")
        
        return '.'.join(oid_parts)

    def _get_host_and_community(self, host, community):
        host = host if host else self.host
        community = community if community else self.community
        return host, community

    def get(self, mib_node, host=None, community=None,oid_type=None):
        """执行SNMP GET操作"""
        oid = self._resolve_oid(mib_node,oid_type=oid_type)
        debug_logger.debug(f"snmpv1v2 get oid: {oid}")
        host, community = self._get_host_and_community(host, community)
        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community,mpModel=self.version),
                   UdpTransportTarget((host, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )
        result = self._process_response(var_binds, error_indication, error_status, error_index)
        debug_logger.debug(f"snmpv1v2 get result: {result}")
        return result

    def get_next(self, mib_node, host=None, community=None):
        """执行SNMP GETNEXT操作"""
        oid = self._resolve_oid(mib_node)
        host, community = self._get_host_and_community(host, community)
        error_indication, error_status, error_index, var_binds = next(
            nextCmd(SnmpEngine(),
                   CommunityData(community,mpModel=self.version),
                   UdpTransportTarget((host, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )
        return self._process_response(var_binds, error_indication, error_status,error_index)

    def set(self, mib_nodes_values, host=None, community=None, oid_type=None,timeout=1.0):
        """执行SNMP SET操作"""
        oid_value_pairs = []
        host, community = self._get_host_and_community(host, community)
        debug_logger.debug(f"snmpv1v2 set mib_nodes_values: {mib_nodes_values}")
        for mib_node, value in mib_nodes_values.items():
            oid = self._resolve_oid(mib_node,oid_type=oid_type)
            oid_value_pairs.append((oid, value))

        debug_logger.debug(f"snmpv1v2 set oid_value_pairs: {oid_value_pairs}")
        error_indication, error_status, error_index, var_binds = next(
            setCmd(SnmpEngine(),
                   CommunityData(community,mpModel=self.version),
                   UdpTransportTarget((host, 161),timeout=timeout),
                   ContextData(),
                   *[ObjectType(ObjectIdentity(oid), value) for oid, value in oid_value_pairs])
        )
        result = self._process_response(var_binds, error_indication, error_status, error_index)
        debug_logger.debug(f"snmpv1v2 set result:{result}")
        return result

    def concurrent_test(self, host, community, mib_node, count, interval):
        """并发测试方法"""
        results = []
        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(count):
                futures.append(executor.submit(self.get, host, community, mib_node))
                time.sleep(interval)
                
            for future in futures:
                results.append(future.result())
        return results

    def _process_response(self, var_binds, error_indication, error_status, error_index):
        """统一处理响应结果"""
        if error_indication:
            return {'status': 'error', 'message': str(error_indication)}
        elif error_status:
            return {'status': 'error', 
                    'message': f"{error_status.prettyPrint()} at {error_index}"}
        else:
            return {
                'status': 'success',
                # 'data': [{'oid': oid.prettyPrint(), 'value': val.prettyPrint()}
                'data': [{'oid': oid.prettyPrint(), 'value': val.asOctets().decode('utf-8') if isinstance(val, OctetString) else val.prettyPrint()}
                # 'data': [{'oid': oid.prettyPrint(), 'value': val.encoding('utf-8').prettyPrint()}
                        for oid, val in var_binds]
            }