"""
配置备份 URL 配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConfigBackupViewSet, ConfigDiffViewSet, RestoreHistoryViewSet

router = DefaultRouter()
router.register(r'', ConfigBackupViewSet, basename='configbackup')
router.register(r'diffs', ConfigDiffViewSet, basename='configdiff')
router.register(r'restore-history', RestoreHistoryViewSet, basename='restorehistory')

urlpatterns = router.urls

