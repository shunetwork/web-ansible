"""
自动创建超级用户脚本
"""
import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_ansible.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 默认管理员信息
USERNAME = 'admin'
EMAIL = 'admin@example.com'
PASSWORD = 'admin123'

# 检查用户是否已存在
if User.objects.filter(username=USERNAME).exists():
    print(f'用户 "{USERNAME}" 已存在！')
    user = User.objects.get(username=USERNAME)
    print(f'用户名: {USERNAME}')
    print(f'邮箱: {user.email}')
else:
    # 创建超级用户
    user = User.objects.create_superuser(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD
    )
    print('[OK] 超级用户创建成功！')
    print('=' * 50)
    print(f'用户名: {USERNAME}')
    print(f'密码: {PASSWORD}')
    print(f'邮箱: {EMAIL}')
    print('=' * 50)
    print(f'\n访问管理后台: http://127.0.0.1:8000/admin/')
    print('使用上述账号密码登录即可')

