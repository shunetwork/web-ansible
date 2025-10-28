"""
设备管理 URL 配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, DeviceGroupViewSet, DeviceCredentialViewSet

router = DefaultRouter()
router.register(r'', DeviceViewSet, basename='device')
router.register(r'groups', DeviceGroupViewSet, basename='devicegroup')
router.register(r'credentials', DeviceCredentialViewSet, basename='devicecredential')

urlpatterns = router.urls

