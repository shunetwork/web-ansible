"""
模板管理 URL 配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConfigTemplateViewSet, TemplateVersionViewSet, TemplateVariableViewSet

router = DefaultRouter()
router.register(r'', ConfigTemplateViewSet, basename='configtemplate')
router.register(r'versions', TemplateVersionViewSet, basename='templateversion')
router.register(r'variables', TemplateVariableViewSet, basename='templatevariable')

urlpatterns = router.urls

