from pysnmp.hlapi import *
from concurrent.futures import ThreadPoolExecutor
import yaml
import time
# from src.core.snmp.v1v2c import SNMPv1v2cTester
from src.utils.logger import debug_logger


class SNMPv3Tester:
    OID_TYPE_SCALAR = 'scalar'
    OID_TYPE_SCALAR_1 = 'scalar'
    OID_TYPE_TABLE = 'table'

    def __init__(self, mib_yaml_path, host, username, engine=None,auth_key=None, priv_key=None, auth_protocol='SHA',
                 priv_protocol='DES'):
        self.host = host
        self.username = username
        self.auth_key = auth_key
        self.priv_key = priv_key
        self.mib_yaml_path = mib_yaml_path
        self.mib_mappings = self._load_mib_mappings(mib_yaml_path)
        self.engine = engine if engine else SnmpEngine()
        
        # 设置安全级别
        if auth_key and priv_key:
            self.security_level = 'authPriv'
        elif auth_key:
            self.security_level = 'authNoPriv'
        else:
            self.security_level = 'noAuthNoPriv'

        self.auth_protocol = auth_protocol
        self.priv_protocol = priv_protocol
            
        # 协议映射
        self.auth_protocol_map = {
            'MD5': usmHMACMD5AuthProtocol,
            'SHA': usmHMACSHAAuthProtocol
            # 'SHA256': usmHMAC128SHA256AuthProtocol
        }
        
        self.priv_protocol_map = {
            'DES': usmDESPrivProtocol,
            'AES128': usmAesCfb128Protocol,
            'AES192': usmAesCfb192Protocol,
            'AES256': usmAesCfb256Protocol
        }
    
    def _load_mib_mappings(self, yaml_path=None):
        """加载MIB YAML配置文件"""
        yaml_path = yaml_path if yaml_path else self.mib_yaml_path
        with open(yaml_path, 'r', encoding='utf-8') as f:
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

    def _get_usm_user_data(self):
        """获取USM用户安全参数"""
        if self.security_level == 'noAuthNoPriv':
            return UsmUserData(self.username)
        elif self.security_level == 'authNoPriv':
            return UsmUserData(
                self.username,
                authKey=self.auth_key,
                authProtocol=self.auth_protocol_map.get(self.auth_protocol)
            )
        else:
            return UsmUserData(
                self.username,
                authKey=self.auth_key,
                privKey=self.priv_key,
                authProtocol=self.auth_protocol_map.get(self.auth_protocol),
                privProtocol=self.priv_protocol_map.get(self.priv_protocol)
            )

    def get(self, mib_node, host=None, oid_type=None):
        """执行SNMPv3 GET操作"""
        oid = self._resolve_oid(mib_node,oid_type=oid_type)
        host = host if host else self.host
        usm_user = self._get_usm_user_data()

        debug_logger.debug(f"snmpv3 get oid: {oid}")
        debug_logger.debug(f"snmpv3 get usm_user: {usm_user}")
        error_indication, error_status, error_index, var_binds = next(
            getCmd(self.engine,
                   usm_user,
                   UdpTransportTarget((host, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )
        result = self._process_response(var_binds, error_indication, error_status, error_index)
        debug_logger.debug(f"snmpv3 get result: {result}")
        return result

    def get_next(self, mib_node, host=None):
        """执行SNMPv3 GETNEXT操作"""
        oid = self._resolve_oid(mib_node)
        host = host if host else self.host
        usm_user = self._get_usm_user_data()
        
        error_indication, error_status, error_index, var_binds = next(
            nextCmd(self.engine,
                   usm_user,
                   UdpTransportTarget((host, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )
        return self._process_response(var_binds, error_indication, error_status, error_index)

    def set(self, mib_nodes_values, host=None, oid_type= None,timeout=1.0):
        """执行SNMPv3 SET操作"""
        oid_value_pairs = []
        host = host if host else self.host
        usm_user = self._get_usm_user_data()
        
        for mib_node, value in mib_nodes_values.items():
            oid = self._resolve_oid(mib_node,oid_type=oid_type)
            oid_value_pairs.append((oid, value))

        debug_logger.debug(f"snmpv3 set usm_user:{usm_user}")
        debug_logger.debug(f"snmpv3 set oid:{oid_value_pairs}")
        error_indication, error_status, error_index, var_binds = next(
            setCmd(self.engine,
                   usm_user,
                   UdpTransportTarget((host, 161),timeout=timeout),
                   ContextData(),
                   *[ObjectType(ObjectIdentity(oid), value) for oid, value in oid_value_pairs])
        )
        result =  self._process_response(var_binds, error_indication, error_status, error_index)
        debug_logger.debug(f"snmpv3 set result:{result}")
        return result

    def concurrent_test(self, mib_node, count, interval, host=None):
        """并发测试方法"""
        results = []
        host = host if host else self.host
        
        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(count):
                futures.append(executor.submit(self.get, mib_node, host))
                time.sleep(interval)
                
            for future in futures:
                results.append(future.result())
        return results

    def set_mib_path(self, mib_path):
        self.mib_yaml_path = mib_path
        self._load_mib_mappings()

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
                'data': [{'oid': oid.prettyPrint(), 'value': val.asOctets().decode('utf-8')}
                        for oid, val in var_binds]
            }