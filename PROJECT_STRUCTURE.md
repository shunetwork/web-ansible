# 项目结构说明

本文档详细说明项目的目录结构和各个文件的作用。

## 目录树

```
web-ansible/
├── web_ansible/              # Django 项目配置目录
│   ├── __init__.py          # 项目包初始化（导入 Celery）
│   ├── settings.py          # Django 设置
│   ├── urls.py              # 项目 URL 配置
│   ├── wsgi.py              # WSGI 配置
│   ├── asgi.py              # ASGI 配置
│   └── celery.py            # Celery 配置
│
├── devices/                  # 设备管理应用
│   ├── __init__.py
│   ├── apps.py              # 应用配置
│   ├── models.py            # 数据模型（Device, DeviceGroup, DeviceCredential）
│   ├── admin.py             # Admin 配置
│   ├── views.py             # API 视图
│   ├── serializers.py       # REST 序列化器
│   ├── urls.py              # URL 配置
│   └── tasks.py             # Celery 任务
│
├── templates_mgr/            # 模板管理应用
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py            # ConfigTemplate, TemplateVersion, TemplateVariable
│   ├── admin.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
│
├── tasks/                    # 任务执行应用
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py            # Task, TaskResult, Schedule
│   ├── admin.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── tasks.py             # Celery 任务（任务执行逻辑）
│
├── backups/                  # 配置备份应用
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py            # ConfigBackup, ConfigDiff, RestoreHistory
│   ├── admin.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── tasks.py             # 备份和恢复任务
│
├── audit/                    # 审计日志应用
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py            # AuditLog, LoginHistory, OperationStatistics
│   ├── admin.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── middleware.py        # 审计中间件
│
├── ansible_playbooks/        # Ansible 自动化脚本
│   ├── ansible.cfg          # Ansible 配置
│   ├── inventory/           # 主机清单目录
│   │   └── hosts.ini
│   ├── backup_config.yml    # 备份配置
│   ├── deploy_config.yml    # 部署配置
│   ├── execute_commands.yml # 执行命令
│   ├── health_check.yml     # 健康检查
│   ├── restore_config.yml   # 恢复配置
│   ├── templates/           # Jinja2 模板
│   │   ├── interface_config.j2
│   │   ├── vlan_config.j2
│   │   ├── acl_config.j2
│   │   └── routing_config.j2
│   └── README.md
│
├── tests/                    # 测试目录
│   ├── __init__.py
│   ├── conftest.py          # pytest 配置和 fixtures
│   ├── test_devices.py      # 设备模块测试
│   ├── test_templates.py    # 模板模块测试
│   ├── test_tasks.py        # 任务模块测试
│   ├── test_backups.py      # 备份模块测试
│   ├── test_audit.py        # 审计模块测试
│   ├── test_api.py          # API 测试
│   └── README.md
│
├── media/                    # 媒体文件目录
│   └── backups/             # 配置备份存储
│
├── staticfiles/              # 静态文件收集目录
│
├── logs/                     # 日志目录
│   ├── django.log           # Django 日志
│   └── ansible.log          # Ansible 日志
│
├── manage.py                 # Django 管理脚本
├── requirements.txt          # Python 依赖
├── pytest.ini                # pytest 配置
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略文件
├── README.md                 # 项目说明
├── QUICKSTART.md             # 快速开始指南
├── PROJECT_STRUCTURE.md      # 项目结构说明（本文件）
└── 需求.txt                  # 原始需求文档
```

## 核心组件说明

### 1. Django 项目配置 (web_ansible/)

#### settings.py
包含所有 Django 配置：
- 应用列表 (INSTALLED_APPS)
- 中间件配置
- 数据库设置（SQLite）
- Celery 配置
- Django Jet 配置
- 日志配置
- 静态文件和媒体文件设置

#### urls.py
项目主 URL 配置：
- Admin 后台路由
- Django Jet 路由
- 各应用 API 路由

#### celery.py
Celery 异步任务配置：
- Celery 应用初始化
- 定时任务调度配置（beat_schedule）
- 自动发现任务

### 2. 应用模块

每个应用都遵循 Django 标准结构：

#### models.py
定义数据模型，包括：
- 字段定义
- 模型关系
- 自定义方法
- Meta 配置（排序、索引等）

#### admin.py
Django Admin 后台配置：
- 列表显示字段
- 过滤器和搜索
- 自定义操作
- 内联编辑
- 自定义视图

#### views.py
REST API 视图：
- ViewSet 定义
- 自定义 action
- 权限控制
- 数据过滤和搜索

#### serializers.py
REST 序列化器：
- 数据序列化/反序列化
- 字段定义和验证
- 关联数据处理

#### tasks.py
Celery 异步任务：
- 后台任务定义
- 定时任务
- 长时间运行的操作

### 3. 设备管理 (devices/)

**核心模型：**
- `Device`: 网络设备信息
- `DeviceGroup`: 设备分组
- `DeviceCredential`: 设备凭据管理

**主要功能：**
- 设备 CRUD 操作
- SSH 连接测试
- 批量导入/导出（CSV）
- 设备健康检查
- 设备分组管理

### 4. 模板管理 (templates_mgr/)

**核心模型：**
- `ConfigTemplate`: 配置模板（Jinja2）
- `TemplateVersion`: 模板版本历史
- `TemplateVariable`: 模板变量定义

**主要功能：**
- 模板创建和编辑
- 模板渲染预览
- 版本控制
- 变量管理

### 5. 任务执行 (tasks/)

**核心模型：**
- `Task`: 任务记录
- `TaskResult`: 任务执行结果
- `Schedule`: 定时任务

**主要功能：**
- 命令执行
- 模板下发
- 配置备份
- 健康检查
- 定时调度

### 6. 配置备份 (backups/)

**核心模型：**
- `ConfigBackup`: 配置备份记录
- `ConfigDiff`: 配置差异
- `RestoreHistory`: 恢复历史

**主要功能：**
- 自动/手动备份
- 配置对比
- 版本恢复
- 备份清理

### 7. 审计日志 (audit/)

**核心模型：**
- `AuditLog`: 操作审计日志
- `LoginHistory`: 登录历史
- `OperationStatistics`: 操作统计

**主要功能：**
- 自动记录用户操作
- 登录/登出追踪
- 操作统计分析
- 审计报表

### 8. Ansible Playbooks

**核心 Playbooks：**
- `backup_config.yml`: 备份设备配置
- `deploy_config.yml`: 部署配置
- `execute_commands.yml`: 执行命令
- `health_check.yml`: 健康检查
- `restore_config.yml`: 恢复配置

**配置模板：**
- `interface_config.j2`: 接口配置
- `vlan_config.j2`: VLAN 配置
- `acl_config.j2`: ACL 配置
- `routing_config.j2`: 路由配置

## 数据流

### 1. 配置下发流程

```
用户创建任务 -> Task 对象创建
    ↓
Celery 接收任务
    ↓
渲染配置模板
    ↓
生成 Ansible Inventory
    ↓
执行 Ansible Playbook
    ↓
更新 TaskResult
    ↓
记录审计日志
```

### 2. 配置备份流程

```
定时任务触发 / 手动触发
    ↓
Celery 执行备份任务
    ↓
SSH 连接设备
    ↓
获取 running-config
    ↓
保存到文件系统
    ↓
创建 ConfigBackup 记录
    ↓
对比上一版本（可选）
```

### 3. 用户操作审计流程

```
用户执行操作
    ↓
AuditMiddleware 拦截
    ↓
记录请求信息
    ↓
创建 AuditLog 记录
    ↓
记录操作结果
```

## 扩展指南

### 添加新的设备类型

1. 修改 `devices/models.py` 中的 `DEVICE_TYPE_CHOICES`
2. 更新 `devices/tasks.py` 中的连接逻辑
3. 添加对应的 Ansible playbook

### 添加新的任务类型

1. 修改 `tasks/models.py` 中的 `TASK_TYPE_CHOICES`
2. 在 `tasks/tasks.py` 中实现执行逻辑
3. 创建对应的 Ansible playbook
4. 更新 Admin 配置

### 自定义配置模板

1. 在 `ansible_playbooks/templates/` 添加新的 Jinja2 模板
2. 在管理后台创建对应的 ConfigTemplate
3. 定义模板变量

### 集成其他网络设备

1. 安装对应的 Ansible collection
2. 修改 Ansible playbook 支持新设备
3. 更新设备模型的 `get_ansible_vars()` 方法

## 性能优化建议

1. **数据库优化**
   - 添加合适的索引
   - 使用 select_related 和 prefetch_related

2. **Celery 优化**
   - 合理设置 worker 数量
   - 使用任务优先级
   - 配置任务超时时间

3. **缓存**
   - 使用 Redis 缓存常用数据
   - 缓存设备状态
   - 缓存模板渲染结果

4. **异步处理**
   - 所有耗时操作使用 Celery
   - 批量操作分批处理
   - 使用 WebSocket 推送任务状态

## 安全考虑

1. **密码存储**
   - 使用加密存储设备密码
   - 考虑使用 Ansible Vault

2. **API 安全**
   - 使用 Token 认证
   - 限制 API 访问频率
   - 记录所有 API 调用

3. **权限控制**
   - 实现细粒度权限
   - 敏感操作需要二次确认
   - 定期审计权限

4. **网络安全**
   - 使用 VPN 或专网
   - 限制设备访问来源
   - 启用防火墙规则

