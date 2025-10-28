#!/bin/bash
# 停止所有服务的脚本（Linux/Mac）

echo "正在停止所有服务..."

PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_DIR"

# 1. 停止 Django
if [ -f logs/django.pid ]; then
    DJANGO_PID=$(cat logs/django.pid)
    if ps -p $DJANGO_PID > /dev/null 2>&1; then
        echo "停止 Django 服务器 (PID: $DJANGO_PID)..."
        kill $DJANGO_PID
        rm logs/django.pid
        echo "✓ Django 已停止"
    else
        echo "Django 进程不存在"
        rm logs/django.pid
    fi
else
    echo "未找到 Django PID 文件"
fi

# 2. 停止 Celery Beat
if [ -f logs/celery_beat.pid ]; then
    echo "停止 Celery Beat..."
    celery -A web_ansible control shutdown
    rm logs/celery_beat.pid 2>/dev/null
    echo "✓ Celery Beat 已停止"
else
    echo "未找到 Celery Beat PID 文件"
fi

# 3. 停止 Celery Worker
if [ -f logs/celery_worker.pid ]; then
    WORKER_PID=$(cat logs/celery_worker.pid)
    if ps -p $WORKER_PID > /dev/null 2>&1; then
        echo "停止 Celery Worker (PID: $WORKER_PID)..."
        kill $WORKER_PID
        rm logs/celery_worker.pid
        echo "✓ Celery Worker 已停止"
    else
        echo "Celery Worker 进程不存在"
        rm logs/celery_worker.pid
    fi
else
    echo "未找到 Celery Worker PID 文件"
fi

# 强制清理可能残留的 Celery 进程
pkill -f "celery.*web_ansible" 2>/dev/null

echo ""
echo "所有服务已停止！"

