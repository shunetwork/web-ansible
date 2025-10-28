"""
重置管理员密码脚本
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
NEW_PASSWORD = 'admin123'

try:
    user = User.objects.get(username=USERNAME)
    user.set_password(NEW_PASSWORD)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    
    print('=' * 50)
    print('[OK] 管理员密码已重置！')
    print('=' * 50)
    print(f'用户名: {USERNAME}')
    print(f'新密码: {NEW_PASSWORD}')
    print(f'邮箱: {user.email}')
    print('=' * 50)
    print(f'\n访问管理后台: http://127.0.0.1:8000/admin/')
    print('使用上述账号密码登录')
    
except User.DoesNotExist:
    # 如果不存在就创建
    user = User.objects.create_superuser(
        username=USERNAME,
        email='admin@example.com',
        password=NEW_PASSWORD
    )
    print('=' * 50)
    print('[OK] 管理员账户已创建！')
    print('=' * 50)
    print(f'用户名: {USERNAME}')
    print(f'密码: {NEW_PASSWORD}')
    print(f'邮箱: {user.email}')
    print('=' * 50)
    print(f'\n访问管理后台: http://127.0.0.1:8000/admin/')
    print('使用上述账号密码登录')

