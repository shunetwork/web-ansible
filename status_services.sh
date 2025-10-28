#!/bin/bash
# 查看服务状态的脚本（Linux/Mac）

echo "=========================================="
echo "服务运行状态"
echo "=========================================="

PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_DIR"

# 检查 Redis
echo -n "Redis:          "
if pgrep -x "redis-server" > /dev/null; then
    echo "✓ 运行中"
else
    echo "✗ 未运行"
fi

# 检查 Celery Worker
echo -n "Celery Worker:  "
if [ -f logs/celery_worker.pid ]; then
    WORKER_PID=$(cat logs/celery_worker.pid)
    if ps -p $WORKER_PID > /dev/null 2>&1; then
        echo "✓ 运行中 (PID: $WORKER_PID)"
    else
        echo "✗ 未运行 (PID 文件存在但进程不存在)"
    fi
else
    if pgrep -f "celery.*worker.*web_ansible" > /dev/null; then
        echo "✓ 运行中 (无 PID 文件)"
    else
        echo "✗ 未运行"
    fi
fi

# 检查 Celery Beat
echo -n "Celery Beat:    "
if [ -f logs/celery_beat.pid ]; then
    BEAT_PID=$(cat logs/celery_beat.pid)
    if ps -p $BEAT_PID > /dev/null 2>&1; then
        echo "✓ 运行中 (PID: $BEAT_PID)"
    else
        echo "✗ 未运行 (PID 文件存在但进程不存在)"
    fi
else
    if pgrep -f "celery.*beat.*web_ansible" > /dev/null; then
        echo "✓ 运行中 (无 PID 文件)"
    else
        echo "✗ 未运行"
    fi
fi

# 检查 Django
echo -n "Django:         "
if [ -f logs/django.pid ]; then
    DJANGO_PID=$(cat logs/django.pid)
    if ps -p $DJANGO_PID > /dev/null 2>&1; then
        echo "✓ 运行中 (PID: $DJANGO_PID)"
    else
        echo "✗ 未运行 (PID 文件存在但进程不存在)"
    fi
else
    if pgrep -f "python.*manage.py.*runserver" > /dev/null; then
        echo "✓ 运行中 (无 PID 文件)"
    else
        echo "✗ 未运行"
    fi
fi

echo "=========================================="
echo ""
echo "访问地址:"
echo "  管理后台: http://127.0.0.1:8000/admin/"
echo "  API:     http://127.0.0.1:8000/api/"
echo ""
echo "日志文件:"
if [ -f logs/django.log ]; then
    echo "  Django:       logs/django.log (最后 5 行)"
    tail -n 5 logs/django.log | sed 's/^/    /'
fi
echo "=========================================="

