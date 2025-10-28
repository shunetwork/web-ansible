@echo off
REM 停止所有服务的脚本（Windows）

echo 正在停止所有服务...

REM 停止 Django
echo 停止 Django 服务器...
taskkill /FI "WINDOWTITLE eq Django Server*" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo [√] Django 已停止
) else (
    echo Django 未运行或已停止
)

REM 停止 Celery Beat
echo 停止 Celery Beat...
taskkill /FI "WINDOWTITLE eq Celery Beat*" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo [√] Celery Beat 已停止
) else (
    echo Celery Beat 未运行或已停止
)

REM 停止 Celery Worker
echo 停止 Celery Worker...
taskkill /FI "WINDOWTITLE eq Celery Worker*" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo [√] Celery Worker 已停止
) else (
    echo Celery Worker 未运行或已停止
)

REM 强制清理可能残留的 Python 进程（celery 相关）
taskkill /IM celery.exe /F >nul 2>&1

REM 停止 Redis
echo 停止 Redis...
taskkill /FI "WINDOWTITLE eq Redis Server*" /F >nul 2>&1
if %errorlevel% equ 0 (
    echo [√] Redis 已停止
) else (
    echo Redis 未运行或已停止
)

echo.
echo 所有服务已停止！
pause

