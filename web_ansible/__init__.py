# 这将确保 Celery 应用始终在 Django 启动时导入
# 但在没有 celery 时可以跳过
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery 未安装，跳过
    pass

