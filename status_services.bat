@echo off
REM 查看服务状态的脚本（Windows）

echo ==========================================
echo 服务运行状态
echo ==========================================

REM 检查 Redis
echo Redis:          
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo                 [√] 运行中
) else (
    echo                 [×] 未运行
)

REM 检查 Celery Worker
echo Celery Worker:  
tasklist /FI "WINDOWTITLE eq Celery Worker*" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo                 [√] 运行中
) else (
    echo                 [×] 未运行
)

REM 检查 Celery Beat
echo Celery Beat:    
tasklist /FI "WINDOWTITLE eq Celery Beat*" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo                 [√] 运行中
) else (
    echo                 [×] 未运行
)

REM 检查 Django
echo Django:         
tasklist /FI "WINDOWTITLE eq Django Server*" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo                 [√] 运行中
) else (
    echo                 [×] 未运行
)

echo ==========================================
echo.
echo 访问地址:
echo   管理后台: http://127.0.0.1:8000/admin/
echo   API:     http://127.0.0.1:8000/api/
echo.
echo 日志文件:
echo   - Django:       logs\django.log
echo   - Celery Worker: logs\celery_worker.log
echo   - Celery Beat:   logs\celery_beat.log
echo ==========================================
echo.
pause

