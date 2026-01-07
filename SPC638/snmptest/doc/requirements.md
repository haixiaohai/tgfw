# SNMP测试工具需求文档

## 1. 项目概述
开发跨平台的SNMP协议测试工具，支持SNMPv1/v2c/v3协议版本，提供基础协议操作和调试功能。

## 2. 功能需求

### 2.1 协议支持
- [x] SNMPv1/v2c 测试功能
  - 支持GET/SET/GETNEXT操作
  - 在GET和GETNEXT操作支持以字符串的形式传入请求的mib节点，在snmp请求时从mib管理的yaml文档中获取对应的oid
  - 在set操作时支持指定以列表的形式传入请求的mib节点，在snmp请求时从mib管理的yaml文档中获取对应的oid
  - 提供并发测试方法，可以制定数量和间隔发起snmp测试

- [ ] SNMPv3 测试功能
  - 支持三种安全级别：
    - noAuthNoPriv
    - authNoPriv
    - authPriv
  - 认证协议支持：MD5/SHA/SHA256
  - 加密协议支持：DES/AES128/AES192/AES256

### 2.2 核心功能
- [ ] MIB智能管理
  - 采用YAML格式定义MIB映射关系
  - 配置示例：
    ```yaml
    mib_mappings:
      system:
        oid: 1.3.6.1.2.1.1
        description: System Information
        children:
          sysDescr: 1.3.6.1.2.1.1.1.0
          sysUpTime: 1.3.6.1.2.1.1.3.0
      interfaces:
        oid: 1.3.6.1.2.1.2.2
    ```
  - 支持以下自动化功能：
    - 命令行输入时通过`Tab键`自动补全YAML定义的key值
    - 执行测试时自动将key值转换为完整OID
    - 支持多层级YAML定义嵌套解析

## 3. 非功能需求
- **跨平台支持**：Windows 10+ / Linux (Ubuntu 18.04+)
- **性能要求**：单实例支持同时管理50个SNMP会话
- **日志记录**：详细记录协议交互过程，支持导出为PCAP格式
- **配置管理**：支持测试配置的保存/加载（JSON格式）

## 4. 用户界面要求
- 命令行交互模式（基础功能）
- 响应式Web界面（可选扩展功能）
- 实时结果显示区域
- 历史测试记录查看

## 5. 安全要求
- SNMPv3用户密钥加密存储
- 敏感操作审计日志
- 输入参数合法性校验

## 6. 项目目录结构
├── src/                    # 源代码目录
│   ├── core/              # 核心功能实现
│   │   ├── snmp/         # SNMP协议实现
│   │   │   ├── v1.py    # SNMPv1实现
│   │   │   ├── v2c.py   # SNMPv2c实现
│   │   │   └── v3.py    # SNMPv3实现
├── config/                # 配置文件目录
│   ├── mibs/             # MIB YAML配置
│   │   ├── system.yaml  # 系统MIB配置
│   │   └── custom/      # 自定义MIB配置
│   └── templates/        # 配置模板
├── tests/                 # 测试目录
│   ├── unit/            # 单元测试
│   └── integration/     # 集成测试
├── logs/                  # 日志目录
│   └── audit/           # 审计日志
├── doc/                   # 文档目录
│   └── requirements.md  # 需求文档
└── requirements.txt       # 项目依赖
