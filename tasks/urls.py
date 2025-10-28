"""
任务执行 URL 配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskResultViewSet, ScheduleViewSet

router = DefaultRouter()
router.register(r'', TaskViewSet, basename='task')
router.register(r'results', TaskResultViewSet, basename='taskresult')
router.register(r'schedules', ScheduleViewSet, basename='schedule')

urlpatterns = router.urls

