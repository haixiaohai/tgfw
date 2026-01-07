import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file, level=logging.INFO):
    """配置并返回一个日志记录器"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 设置日志处理器
    handler = RotatingFileHandler(
        log_file, maxBytes=1024*1024, backupCount=5
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# 审计日志实例
audit_logger = setup_logger(
    'audit', 
    'd:/01_ai/test/snmptest/logs/audit/snmp_audit.log'
)

# 操作日志实例
operation_logger = setup_logger(
    'operation',
    'd:/01_ai/test/snmptest/logs/snmp_operations.log'
)

# 操作日志实例
debug_logger = setup_logger(
    'debug',
    'd:/01_ai/test/snmptest/logs/snmp_debug.log',
    level=logging.DEBUG
)