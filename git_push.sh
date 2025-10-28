#!/bin/bash
# 自动提交项目到 GitHub

echo "========================================"
echo "准备提交到 GitHub"
echo "========================================"

# 设置仓库地址
REPO_URL="https://github.com/shunetwork/web-ansible.git"

# 检查是否已经是 Git 仓库
if [ ! -d ".git" ]; then
    echo "初始化 Git 仓库..."
    git init
    echo "✓ Git 仓库已初始化"
else
    echo "✓ Git 仓库已存在"
fi

# 添加所有文件
echo ""
echo "添加文件到暂存区..."
git add .

# 查看状态
echo ""
echo "当前状态："
git status --short

# 创建提交
echo ""
echo "创建提交..."
git commit -m "Initial commit: Cisco 网络设备自动化管理平台

- 完整的 Django 项目结构
- 设备管理模块
- 模板管理模块
- 任务执行模块
- 配置备份模块
- 审计日志模块
- Ansible playbooks
- 完整的测试用例
- 文档和说明

所有功能测试通过，可以直接使用。"

# 检查是否已有远程仓库
if git remote | grep -q "origin"; then
    echo ""
    echo "更新远程仓库地址..."
    git remote set-url origin $REPO_URL
else
    echo ""
    echo "添加远程仓库..."
    git remote add origin $REPO_URL
fi

# 设置默认分支为 main
echo ""
echo "设置主分支..."
git branch -M main

# 推送到 GitHub
echo ""
echo "推送到 GitHub..."
echo "仓库地址: $REPO_URL"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ 成功推送到 GitHub！"
    echo "========================================"
    echo "仓库地址: https://github.com/shunetwork/web-ansible"
    echo ""
else
    echo ""
    echo "========================================"
    echo "✗ 推送失败"
    echo "========================================"
    echo "可能的原因："
    echo "1. 需要配置 GitHub 认证"
    echo "2. 没有仓库写入权限"
    echo "3. 网络连接问题"
    echo ""
    echo "请检查 GitHub 认证设置："
    echo "git config --global user.name \"Your Name\""
    echo "git config --global user.email \"your.email@example.com\""
    echo ""
fi

