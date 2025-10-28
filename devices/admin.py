"""
设备管理 Admin 配置
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Device, DeviceGroup, DeviceCredential
from .tasks import test_device_connection


@admin.register(DeviceGroup)
class DeviceGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'device_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def device_count(self, obj):
        """设备数量"""
        return obj.devices.count()
    device_count.short_description = '设备数量'


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'ip_address', 'device_type', 'status_badge', 
        'is_active', 'last_check', 'action_buttons'
    ]
    list_filter = ['device_type', 'status', 'is_active', 'groups']
    search_fields = ['name', 'hostname', 'ip_address', 'serial_number']
    readonly_fields = ['last_check', 'last_check_result', 'created_at', 'updated_at', 'created_by']
    filter_horizontal = ['groups']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'hostname', 'ip_address', 'device_type', 'model', 'serial_number')
        }),
        ('连接信息', {
            'fields': ('ssh_port', 'username', 'password', 'enable_password')
        }),
        ('分组和状态', {
            'fields': ('groups', 'status', 'is_active', 'location', 'description')
        }),
        ('版本信息', {
            'fields': ('os_version',),
            'classes': ('collapse',)
        }),
        ('健康检查', {
            'fields': ('last_check', 'last_check_result'),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['test_connections', 'activate_devices', 'deactivate_devices']
    
    def status_badge(self, obj):
        """状态标识"""
        color_map = {
            'online': 'green',
            'offline': 'red',
            'maintenance': 'orange',
            'unknown': 'gray',
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">●</span> {}',
            color, obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def action_buttons(self, obj):
        """操作按钮"""
        return format_html(
            '<a class="button" href="{}">测试连接</a>',
            f'/admin/devices/device/{obj.id}/test-connection/'
        )
    action_buttons.short_description = '操作'
    
    def save_model(self, request, obj, form, change):
        """保存时记录创建者"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def test_connections(self, request, queryset):
        """批量测试连接"""
        for device in queryset:
            test_device_connection.delay(device.id)
        self.message_user(request, f'已提交 {queryset.count()} 个设备的连接测试任务', messages.SUCCESS)
    test_connections.short_description = '测试选中设备的连接'
    
    def activate_devices(self, request, queryset):
        """激活设备"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {count} 个设备', messages.SUCCESS)
    activate_devices.short_description = '激活选中的设备'
    
    def deactivate_devices(self, request, queryset):
        """停用设备"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {count} 个设备', messages.SUCCESS)
    deactivate_devices.short_description = '停用选中的设备'
    
    def get_urls(self):
        """添加自定义 URL"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:device_id>/test-connection/',
                self.admin_site.admin_view(self.test_connection_view),
                name='device-test-connection',
            ),
        ]
        return custom_urls + urls
    
    def test_connection_view(self, request, device_id):
        """测试连接视图"""
        device = Device.objects.get(pk=device_id)
        test_device_connection.delay(device_id)
        self.message_user(request, f'已提交 {device.name} 的连接测试任务', messages.SUCCESS)
        return redirect('admin:devices_device_changelist')


@admin.register(DeviceCredential)
class DeviceCredentialAdmin(admin.ModelAdmin):
    list_display = ['name', 'username', 'description', 'created_at']
    search_fields = ['name', 'username', 'description']
    readonly_fields = ['created_at', 'updated_at']

