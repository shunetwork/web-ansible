# 快速开始指南

本指南将帮助您快速部署和使用 Cisco 网络设备自动化管理平台。

## 系统要求

- Python 3.8+
- Redis 服务器
- SQLite（或其他数据库）
- Ansible 2.9+

## 安装步骤

### 1. 克隆项目（如果从 Git 获取）

```bash
git clone <repository-url>
cd web-ansible
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装 Ansible Collections

```bash
ansible-galaxy collection install cisco.ios
```

### 5. 配置环境变量

复制环境变量模板文件并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，修改以下配置：

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 6. 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. 创建超级用户

```bash
python manage.py createsuperuser
```

按提示输入用户名、邮箱和密码。

### 8. 收集静态文件

```bash
python manage.py collectstatic --noinput
```

## 启动服务

### 方式一：开发环境（单进程）

#### 1. 启动 Redis

```bash
# Windows (需要先安装 Redis)
redis-server

# Linux
sudo systemctl start redis

# Mac
brew services start redis
```

#### 2. 启动 Celery Worker（新终端）

```bash
celery -A web_ansible worker -l info
```

#### 3. 启动 Celery Beat（新终端）

```bash
celery -A web_ansible beat -l info
```

#### 4. 启动 Django 开发服务器（新终端）

```bash
python manage.py runserver
```

### 方式二：生产环境

生产环境建议使用 Supervisor 或 systemd 来管理进程。

#### 使用 Supervisor 示例配置

```ini
[program:django]
command=/path/to/venv/bin/gunicorn web_ansible.wsgi:application -b 0.0.0.0:8000
directory=/path/to/web-ansible
user=www-data
autostart=true
autorestart=true

[program:celery_worker]
command=/path/to/venv/bin/celery -A web_ansible worker -l info
directory=/path/to/web-ansible
user=www-data
autostart=true
autorestart=true

[program:celery_beat]
command=/path/to/venv/bin/celery -A web_ansible beat -l info
directory=/path/to/web-ansible
user=www-data
autostart=true
autorestart=true
```

## 访问系统

### 管理后台

访问：http://127.0.0.1:8000/admin/

使用之前创建的超级用户登录。

### API 接口

基础 URL：http://127.0.0.1:8000/api/

主要端点：
- `/api/devices/` - 设备管理
- `/api/templates/` - 模板管理
- `/api/tasks/` - 任务执行
- `/api/backups/` - 配置备份
- `/api/audit/logs/` - 审计日志

## 基本使用

### 1. 添加设备

在管理后台 -> 设备管理 -> 网络设备 -> 添加设备

填写以下信息：
- 设备名称
- 主机名
- IP 地址
- 设备类型
- SSH 端口
- 用户名和密码

### 2. 测试设备连接

在设备列表中，选择设备，点击"测试连接"按钮。

### 3. 创建配置模板

在管理后台 -> 模板管理 -> 配置模板 -> 添加模板

使用 Jinja2 语法编写配置模板：

```jinja2
interface {{ interface_name }}
 description {{ description }}
 ip address {{ ip_address }} {{ subnet_mask }}
 no shutdown
```

### 4. 执行配置下发任务

在管理后台 -> 任务执行 -> 任务 -> 添加任务

选择：
- 任务类型：模板下发
- 目标设备或设备组
- 配置模板
- 填写模板变量

提交后，任务将异步执行。

### 5. 备份设备配置

在管理后台 -> 配置备份，可以：
- 手动备份单个设备
- 查看备份历史
- 对比配置差异
- 恢复到历史版本

### 6. 设置定时任务

在管理后台 -> 任务执行 -> 定时任务 -> 添加定时任务

配置：
- 任务名称和类型
- 目标设备
- 执行频率（每小时/每天/每周/每月）

系统会按计划自动执行任务。

## 常见问题

### Q: Redis 连接失败

**A:** 确保 Redis 服务已启动，检查 `.env` 中的 Redis 配置是否正确。

### Q: Celery 任务不执行

**A:** 检查 Celery Worker 和 Beat 是否正常运行，查看日志输出。

### Q: 设备连接失败

**A:** 
1. 检查设备 IP 地址和端口是否正确
2. 确认用户名和密码正确
3. 检查网络连接
4. 查看审计日志中的详细错误信息

### Q: 模板渲染失败

**A:** 检查模板语法是否正确，确保所有变量都已定义。

### Q: 权限不足

**A:** 确保当前用户有足够的权限，某些操作需要管理员权限。

## 下一步

- 阅读完整文档了解更多功能
- 查看 API 文档学习如何集成
- 浏览 Ansible playbooks 了解自动化细节
- 运行测试用例确保系统正常工作

## 获取帮助

- 查看项目 README.md
- 查看测试用例了解使用方式
- 查看日志文件排查问题

## 安全建议

1. **生产环境务必更改 SECRET_KEY**
2. **禁用 DEBUG 模式**
3. **使用 HTTPS**
4. **加密敏感数据（如密码）**
5. **定期备份数据库**
6. **限制管理后台访问**
7. **定期更新依赖包**

祝您使用愉快！

