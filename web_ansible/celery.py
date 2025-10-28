"""
Celery 配置文件
"""
import os
from celery import Celery
from celery.schedules import crontab

# 设置 Django settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_ansible.settings')

app = Celery('web_ansible')

# 从 Django settings 中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有 Django app 中的 tasks.py
app.autodiscover_tasks()

# 配置定时任务
app.conf.beat_schedule = {
    # 每天凌晨 2 点执行配置备份
    'backup-all-devices': {
        'task': 'backups.tasks.backup_all_devices',
        'schedule': crontab(hour=2, minute=0),
    },
    # 每小时检查设备健康状态
    'check-device-health': {
        'task': 'devices.tasks.check_all_devices_health',
        'schedule': crontab(minute=0),
    },
    # 清理过期备份（每天凌晨 3 点）
    'cleanup-old-backups': {
        'task': 'backups.tasks.cleanup_old_backups',
        'schedule': crontab(hour=3, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')

