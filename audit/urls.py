"""
审计日志 URL 配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, LoginHistoryViewSet, OperationStatisticsViewSet

router = DefaultRouter()
router.register(r'logs', AuditLogViewSet, basename='auditlog')
router.register(r'login-history', LoginHistoryViewSet, basename='loginhistory')
router.register(r'statistics', OperationStatisticsViewSet, basename='operationstatistics')

urlpatterns = router.urls

