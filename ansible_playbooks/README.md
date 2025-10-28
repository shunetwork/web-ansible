# Ansible Playbooks for Cisco Network Automation

这个目录包含用于 Cisco 网络设备自动化管理的 Ansible playbooks。

## 文件结构

```
ansible_playbooks/
├── ansible.cfg              # Ansible 配置文件
├── inventory/               # Inventory 目录
│   └── hosts.ini           # 主机清单（动态生成）
├── backup_config.yml        # 备份配置 playbook
├── deploy_config.yml        # 部署配置 playbook
├── execute_commands.yml     # 执行命令 playbook
├── health_check.yml         # 健康检查 playbook
├── restore_config.yml       # 恢复配置 playbook
└── templates/               # Jinja2 模板目录
    ├── interface_config.j2  # 接口配置模板
    ├── vlan_config.j2       # VLAN 配置模板
    ├── acl_config.j2        # ACL 配置模板
    └── routing_config.j2    # 路由配置模板
```

## Playbooks 说明

### 1. backup_config.yml
备份设备的 running-config 配置。

**使用方法：**
```bash
ansible-playbook -i inventory backup_config.yml -e "backup_dir=/path/to/backup"
```

### 2. deploy_config.yml
部署配置到设备。

**使用方法：**
```bash
ansible-playbook -i inventory deploy_config.yml -e "config_lines=['interface GigabitEthernet0/1', 'description Test']"
```

### 3. execute_commands.yml
在设备上执行命令。

**使用方法：**
```bash
# 执行 show 命令
ansible-playbook -i inventory execute_commands.yml -e "command_type=show commands_list=['show version', 'show ip interface brief']"

# 执行配置命令
ansible-playbook -i inventory execute_commands.yml -e "command_type=config commands_list=['hostname NewName']"
```

### 4. health_check.yml
执行设备健康检查。

**使用方法：**
```bash
ansible-playbook -i inventory health_check.yml -e "report_dir=/path/to/reports"
```

### 5. restore_config.yml
从备份文件恢复配置。

**使用方法：**
```bash
ansible-playbook -i inventory restore_config.yml -e "restore_config_file=/path/to/backup.cfg backup_dir=/path/to/backup"
```

## 配置模板

### interface_config.j2
接口配置模板，支持以下变量：
- `interface_name`: 接口名称
- `description`: 接口描述
- `ip_address` / `subnet_mask`: IP 地址和子网掩码
- `vlan`: VLAN ID
- `trunk_allowed_vlans`: Trunk 允许的 VLAN
- `speed`: 速率
- `duplex`: 双工模式
- `shutdown`: 是否关闭接口

### vlan_config.j2
VLAN 配置模板，支持以下变量：
- `vlans`: VLAN 列表
- `svi_interfaces`: SVI 接口列表

### acl_config.j2
ACL 配置模板，支持以下变量：
- `acl_type`: ACL 类型（standard/extended）
- `acl_name`: ACL 名称
- `rules`: 规则列表
- `apply_to_interface`: 应用到的接口
- `direction`: 方向（in/out）

### routing_config.j2
路由配置模板，支持以下协议：
- OSPF
- EIGRP
- BGP
- 静态路由

## 注意事项

1. 所有 playbook 都需要正确配置的 inventory 文件
2. 确保设备的 SSH 连接正常
3. 执行配置变更前建议先备份
4. 生产环境使用前请充分测试
5. 建议使用 Ansible Vault 加密敏感信息

## 依赖

- Ansible >= 2.9
- ansible-pylibssh 或 paramiko
- Cisco IOS collection: `ansible-galaxy collection install cisco.ios`

