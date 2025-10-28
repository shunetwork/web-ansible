"""
审计日志 Admin 配置
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, LoginHistory, OperationStatistics


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'action_badge', 'level_badge', 'description',
        'object_repr', 'success_badge', 'ip_address', 'created_at'
    ]
    list_filter = ['action', 'level', 'success', 'created_at']
    search_fields = ['username', 'description', 'object_repr', 'ip_address']
    readonly_fields = [
        'user', 'username', 'ip_address', 'user_agent',
        'action', 'description', 'level',
        'content_type', 'object_id', 'object_repr',
        'changes', 'extra_data', 'success', 'error_message',
        'created_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user', 'username', 'ip_address', 'user_agent')
        }),
        ('操作信息', {
            'fields': ('action', 'level', 'description', 'success', 'error_message')
        }),
        ('关联对象', {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        ('详细信息', {
            'fields': ('changes', 'extra_data'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )
    
    def action_badge(self, obj):
        """操作类型标识"""
        color_map = {
            'create': 'green',
            'update': 'blue',
            'delete': 'red',
            'view': 'gray',
            'execute': 'orange',
            'login': 'purple',
            'logout': 'purple',
        }
        color = color_map.get(obj.action, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            color, obj.get_action_display()
        )
    action_badge.short_description = '操作类型'
    
    def level_badge(self, obj):
        """级别标识"""
        color_map = {
            'info': '#2196F3',
            'warning': '#FF9800',
            'error': '#F44336',
            'critical': '#9C27B0',
        }
        color = color_map.get(obj.level, 'gray')
        return format_html(
            '<span style="color: {};">●</span> {}',
            color, obj.get_level_display()
        )
    level_badge.short_description = '级别'
    
    def success_badge(self, obj):
        """成功标识"""
        if obj.success:
            return format_html('<span style="color: green;">✓</span> 成功')
        return format_html('<span style="color: red;">✗</span> 失败')
    success_badge.short_description = '结果'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # 只有超级用户可以删除审计日志
        return request.user.is_superuser


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'status_badge', 'ip_address',
        'failure_reason', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['username', 'ip_address']
    readonly_fields = [
        'user', 'username', 'status', 'ip_address',
        'user_agent', 'failure_reason', 'created_at'
    ]
    date_hierarchy = 'created_at'
    
    def status_badge(self, obj):
        """状态标识"""
        if obj.status == 'success':
            return format_html('<span style="color: green;">●</span> 成功')
        return format_html('<span style="color: red;">●</span> 失败')
    status_badge.short_description = '状态'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(OperationStatistics)
class OperationStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'active_users', 'total_operations',
        'tasks_created', 'backups_created', 'login_success'
    ]
    list_filter = ['date']
    search_fields = ['date']
    readonly_fields = [
        'date', 'active_users', 'new_users',
        'login_success', 'login_failed',
        'total_operations', 'create_operations', 'update_operations',
        'delete_operations', 'execute_operations',
        'tasks_created', 'tasks_success', 'tasks_failed',
        'backups_created', 'backups_success', 'backups_failed',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

