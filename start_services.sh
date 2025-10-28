#!/bin/bash
# 后台启动所有服务的脚本（Linux/Mac）

echo "正在启动 Cisco 网络设备自动化管理平台..."

# 设置项目目录（请根据实际情况修改）
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_DIR"

# 创建日志目录
mkdir -p logs

# 检查虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "警告: 未找到虚拟环境，使用系统 Python"
fi

# 1. 启动 Redis（如果未运行）
echo "检查 Redis 服务..."
if ! pgrep -x "redis-server" > /dev/null; then
    echo "启动 Redis..."
    redis-server --daemonize yes
    echo "✓ Redis 已在后台启动"
else
    echo "✓ Redis 已在运行"
fi

# 等待 Redis 启动
sleep 2

# 2. 启动 Celery Worker
echo "启动 Celery Worker..."
celery -A web_ansible worker -l info \
    --logfile=logs/celery_worker.log \
    --pidfile=logs/celery_worker.pid \
    --detach

if [ $? -eq 0 ]; then
    echo "✓ Celery Worker 已在后台启动"
else
    echo "✗ Celery Worker 启动失败"
fi

# 3. 启动 Celery Beat
echo "启动 Celery Beat..."
celery -A web_ansible beat -l info \
    --logfile=logs/celery_beat.log \
    --pidfile=logs/celery_beat.pid \
    --detach

if [ $? -eq 0 ]; then
    echo "✓ Celery Beat 已在后台启动"
else
    echo "✗ Celery Beat 启动失败"
fi

# 4. 启动 Django 服务器
echo "启动 Django 服务器..."
nohup python manage.py runserver 0.0.0.0:8000 > logs/django.log 2>&1 &
DJANGO_PID=$!
echo $DJANGO_PID > logs/django.pid

if [ $? -eq 0 ]; then
    echo "✓ Django 服务器已在后台启动 (PID: $DJANGO_PID)"
else
    echo "✗ Django 服务器启动失败"
fi

echo ""
echo "=========================================="
echo "所有服务已启动！"
echo "=========================================="
echo "Django 管理后台: http://127.0.0.1:8000/admin/"
echo "API 基础地址: http://127.0.0.1:8000/api/"
echo ""
echo "日志文件位置:"
echo "  - Django: logs/django.log"
echo "  - Celery Worker: logs/celery_worker.log"
echo "  - Celery Beat: logs/celery_beat.log"
echo ""
echo "查看服务状态: ./status_services.sh"
echo "停止所有服务: ./stop_services.sh"
echo "=========================================="

