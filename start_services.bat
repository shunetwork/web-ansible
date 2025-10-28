@echo off
REM 后台启动所有服务的脚本（Windows）

echo 正在启动 Cisco 网络设备自动化管理平台...

cd /d "%~dp0"

REM 创建日志目录
if not exist logs mkdir logs

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo 已激活虚拟环境
) else (
    echo 警告: 未找到虚拟环境，使用系统 Python
)

REM 1. 启动 Redis
echo.
echo 启动 Redis...
start "Redis Server" /MIN redis-server
timeout /t 2 /nobreak >nul
echo [√] Redis 已启动

REM 2. 启动 Celery Worker
echo.
echo 启动 Celery Worker...
start "Celery Worker" /MIN cmd /c "celery -A web_ansible worker -l info > logs\celery_worker.log 2>&1"
echo [√] Celery Worker 已启动

REM 3. 启动 Celery Beat
echo.
echo 启动 Celery Beat...
start "Celery Beat" /MIN cmd /c "celery -A web_ansible beat -l info > logs\celery_beat.log 2>&1"
echo [√] Celery Beat 已启动

REM 4. 启动 Django 服务器
echo.
echo 启动 Django 服务器...
start "Django Server" /MIN cmd /c "python manage.py runserver 0.0.0.0:8000 > logs\django.log 2>&1"
echo [√] Django 服务器已启动

echo.
echo ==========================================
echo 所有服务已启动！
echo ==========================================
echo Django 管理后台: http://127.0.0.1:8000/admin/
echo API 基础地址: http://127.0.0.1:8000/api/
echo.
echo 日志文件位置:
echo   - Django: logs\django.log
echo   - Celery Worker: logs\celery_worker.log
echo   - Celery Beat: logs\celery_beat.log
echo.
echo 查看服务状态: status_services.bat
echo 停止所有服务: stop_services.bat
echo ==========================================
echo.
pause

