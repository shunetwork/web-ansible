# Cisco 网络设备自动化管理平台

基于 **Django Jet** + **SQLite** + **Ansible** 的 Cisco 网络设备集中管理与自动化运维平台。

## 功能特性

- 🖥️ **设备管理**: 集中管理 Cisco 网络设备，支持批量导入/导出
- 📝 **模板化配置**: 基于 Jinja2 的配置模板，支持变量参数化
- ⚡ **批量任务执行**: 异步执行配置下发和命令任务
- 💾 **配置备份**: 自动定时备份，支持差异对比和版本恢复
- 👥 **权限管理**: 多角色权限控制和操作审计
- 🎨 **可视化界面**: Django Jet 提供现代化管理后台

## 技术栈

- **后端框架**: Django 4.2
- **管理界面**: Django Jet
- **数据库**: SQLite
- **自动化引擎**: Ansible
- **异步任务**: Celery + Redis
- **模板引擎**: Jinja2

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 数据库初始化

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

或者使用默认管理员账号：
```bash
python reset_admin_password.py
```

**默认登录信息**：
- 用户名: `admin`
- 密码: `admin123`
- 登录地址: http://127.0.0.1:8000/admin/

> ⚠️ 生产环境请务必修改默认密码！

### 3. 启动 Redis（用于 Celery）

```bash
redis-server
```

### 4. 启动 Celery Worker

```bash
celery -A web_ansible worker -l info
```

### 5. 启动 Celery Beat（定时任务）

```bash
celery -A web_ansible beat -l info
```

### 6. 启动 Django 开发服务器

#### 前台启动（用于调试）

```bash
python manage.py runserver
```

#### 后台启动（一键启动所有服务）

**Linux/Mac:**
```bash
chmod +x start_services.sh  # 首次使用需要添加执行权限
./start_services.sh         # 启动所有服务
./status_services.sh        # 查看服务状态
./stop_services.sh          # 停止所有服务
```

**Windows:**
```batch
start_services.bat    # 启动所有服务
status_services.bat   # 查看服务状态
stop_services.bat     # 停止所有服务
```

> 📖 详细说明请参考 [后台启动服务说明.md](后台启动服务说明.md)

访问 http://127.0.0.1:8000/ 即可使用。

## 项目结构

```
web-ansible/
├── web_ansible/          # Django 项目配置
│   ├── settings.py       # 项目设置
│   ├── urls.py          # 路由配置
│   └── celery.py        # Celery 配置
├── devices/             # 设备管理应用
├── templates/           # 模板管理应用
├── tasks/               # 任务执行应用
├── backups/             # 配置备份应用
├── audit/               # 审计日志应用
├── ansible_playbooks/   # Ansible playbook 目录
├── media/               # 媒体文件（备份配置等）
└── tests/               # 测试用例

```

## 使用说明

### 设备管理

1. 在管理后台添加设备信息（IP、用户名、密码等）
2. 点击"测试连接"验证设备连通性
3. 支持批量导入 CSV 格式的设备列表

### 模板管理

1. 创建 Jinja2 配置模板
2. 定义模板变量
3. 在任务执行时选择模板并填入参数

### 任务执行

1. 选择目标设备或设备组
2. 选择配置模板或自定义命令
3. 提交任务后异步执行
4. 查看任务状态和执行日志

### 配置备份

1. 系统自动定时备份设备配置
2. 查看历史备份版本
3. 对比配置差异
4. 一键恢复到历史版本

## 测试

```bash
pytest
```

## 许可证

MIT License

