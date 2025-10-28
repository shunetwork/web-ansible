@echo off
REM 自动提交项目到 GitHub (Windows)

echo ========================================
echo 准备提交到 GitHub
echo ========================================

REM 设置仓库地址
set REPO_URL=https://github.com/shunetwork/web-ansible.git

REM 检查是否已经是 Git 仓库
if not exist ".git" (
    echo 初始化 Git 仓库...
    git init
    echo [OK] Git 仓库已初始化
) else (
    echo [OK] Git 仓库已存在
)

REM 添加所有文件
echo.
echo 添加文件到暂存区...
git add .

REM 查看状态
echo.
echo 当前状态：
git status --short

REM 创建提交
echo.
echo 创建提交...
git commit -m "Initial commit: Cisco 网络设备自动化管理平台" -m "- 完整的 Django 项目结构" -m "- 设备管理模块" -m "- 模板管理模块" -m "- 任务执行模块" -m "- 配置备份模块" -m "- 审计日志模块" -m "- Ansible playbooks" -m "- 完整的测试用例" -m "- 文档和说明" -m "" -m "所有功能测试通过，可以直接使用。"

REM 检查是否已有远程仓库
git remote | findstr "origin" >nul
if %errorlevel% equ 0 (
    echo.
    echo 更新远程仓库地址...
    git remote set-url origin %REPO_URL%
) else (
    echo.
    echo 添加远程仓库...
    git remote add origin %REPO_URL%
)

REM 设置默认分支为 main
echo.
echo 设置主分支...
git branch -M main

REM 推送到 GitHub
echo.
echo 推送到 GitHub...
echo 仓库地址: %REPO_URL%
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [OK] 成功推送到 GitHub！
    echo ========================================
    echo 仓库地址: https://github.com/shunetwork/web-ansible
    echo.
) else (
    echo.
    echo ========================================
    echo [ERROR] 推送失败
    echo ========================================
    echo 可能的原因：
    echo 1. 需要配置 GitHub 认证
    echo 2. 没有仓库写入权限
    echo 3. 网络连接问题
    echo.
    echo 请检查 GitHub 认证设置：
    echo git config --global user.name "Your Name"
    echo git config --global user.email "your.email@example.com"
    echo.
)

pause

