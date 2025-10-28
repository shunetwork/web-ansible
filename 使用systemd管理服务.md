# 使用 systemd 管理服务（Linux）

在 Linux 系统上，可以使用 systemd 来管理所有服务。

## 1. 创建 systemd 服务文件

### Django 服务

创建文件 `/etc/systemd/system/web-ansible-django.service`:

```ini
[Unit]
Description=Web Ansible Django Application
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/web-ansible
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn web_ansible.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Celery Worker 服务

创建文件 `/etc/systemd/system/web-ansible-celery-worker.service`:

```ini
[Unit]
Description=Web Ansible Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/web-ansible
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A web_ansible worker -l info --detach --pidfile=/var/run/celery_worker.pid --logfile=/path/to/web-ansible/logs/celery_worker.log
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Celery Beat 服务

创建文件 `/etc/systemd/system/web-ansible-celery-beat.service`:

```ini
[Unit]
Description=Web Ansible Celery Beat
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/web-ansible
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A web_ansible beat -l info --detach --pidfile=/var/run/celery_beat.pid --logfile=/path/to/web-ansible/logs/celery_beat.log
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 2. 重载 systemd 配置

```bash
sudo systemctl daemon-reload
```

## 3. 启用服务（开机自启）

```bash
sudo systemctl enable web-ansible-django
sudo systemctl enable web-ansible-celery-worker
sudo systemctl enable web-ansible-celery-beat
```

## 4. 启动服务

```bash
# 启动所有服务
sudo systemctl start web-ansible-django
sudo systemctl start web-ansible-celery-worker
sudo systemctl start web-ansible-celery-beat

# 或者使用脚本一次性启动
sudo systemctl start web-ansible-*
```

## 5. 常用命令

### 查看状态

```bash
# 查看单个服务状态
sudo systemctl status web-ansible-django

# 查看所有服务状态
sudo systemctl status web-ansible-*
```

### 停止服务

```bash
sudo systemctl stop web-ansible-django
sudo systemctl stop web-ansible-celery-worker
sudo systemctl stop web-ansible-celery-beat

# 或者
sudo systemctl stop web-ansible-*
```

### 重启服务

```bash
sudo systemctl restart web-ansible-django
sudo systemctl restart web-ansible-celery-worker
sudo systemctl restart web-ansible-celery-beat
```

### 查看日志

```bash
# 查看服务日志
sudo journalctl -u web-ansible-django -f

# 查看应用日志
tail -f /path/to/web-ansible/logs/django.log
tail -f /path/to/web-ansible/logs/celery_worker.log
tail -f /path/to/web-ansible/logs/celery_beat.log
```

### 禁用服务（关闭开机自启）

```bash
sudo systemctl disable web-ansible-django
sudo systemctl disable web-ansible-celery-worker
sudo systemctl disable web-ansible-celery-beat
```

## 6. 管理脚本

可以创建一个简单的管理脚本 `manage_services.sh`:

```bash
#!/bin/bash

case "$1" in
    start)
        sudo systemctl start web-ansible-django
        sudo systemctl start web-ansible-celery-worker
        sudo systemctl start web-ansible-celery-beat
        echo "所有服务已启动"
        ;;
    stop)
        sudo systemctl stop web-ansible-django
        sudo systemctl stop web-ansible-celery-worker
        sudo systemctl stop web-ansible-celery-beat
        echo "所有服务已停止"
        ;;
    restart)
        sudo systemctl restart web-ansible-django
        sudo systemctl restart web-ansible-celery-worker
        sudo systemctl restart web-ansible-celery-beat
        echo "所有服务已重启"
        ;;
    status)
        sudo systemctl status web-ansible-django
        sudo systemctl status web-ansible-celery-worker
        sudo systemctl status web-ansible-celery-beat
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
```

使用方法:

```bash
chmod +x manage_services.sh
./manage_services.sh start    # 启动
./manage_services.sh stop     # 停止
./manage_services.sh restart  # 重启
./manage_services.sh status   # 状态
```

## 注意事项

1. **修改路径**: 将上述配置文件中的 `/path/to/` 替换为实际路径
2. **修改用户**: 将 `www-data` 替换为实际运行用户
3. **创建日志目录**: 确保日志目录存在且有写权限
4. **Redis 服务**: 确保 Redis 已启动（`sudo systemctl start redis`）
5. **权限设置**: 确保服务用户对项目目录有读写权限

## 优点

- ✅ 开机自启动
- ✅ 自动重启（崩溃后）
- ✅ 统一的服务管理
- ✅ 日志集中管理
- ✅ 进程监控
- ✅ 资源限制

