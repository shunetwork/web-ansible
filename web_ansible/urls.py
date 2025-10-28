"""
URL configuration for web_ansible project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/devices/', include('devices.urls')),
    path('api/templates/', include('templates_mgr.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/backups/', include('backups.urls')),
    path('api/audit/', include('audit.urls')),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 自定义 admin 站点标题
admin.site.site_header = 'Cisco 网络设备自动化管理平台'
admin.site.site_title = 'Cisco 自动化管理'
admin.site.index_title = '欢迎使用 Cisco 网络设备自动化管理平台'

