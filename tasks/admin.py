"""
任务执行 Admin 配置
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Task, TaskResult, Schedule


class TaskResultInline(admin.TabularInline):
    """任务结果内联"""
    model = TaskResult
    extra = 0
    fields = ['device', 'status', 'output_preview', 'started_at', 'completed_at']
    readonly_fields = ['device', 'status', 'output_preview', 'started_at', 'completed_at']
    can_delete = False
    max_num = 10
    
    def output_preview(self, obj):
        """输出预览"""
        if obj.output:
            preview = obj.output[:100]
            if len(obj.output) > 100:
                preview += '...'
            return preview
        return '-'
    output_preview.short_description = '输出预览'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'task_type', 'status_badge', 'progress_bar',
        'success_count', 'failed_count', 'duration_display', 'created_at'
    ]
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = [
        'status', 'progress', 'celery_task_id', 'success_count', 'failed_count', 'total_count',
        'created_at', 'started_at', 'completed_at', 'created_by', 'duration_display'
    ]
    filter_horizontal = ['target_devices', 'target_groups']
    inlines = [TaskResultInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'task_type', 'description')
        }),
        ('目标设备', {
            'fields': ('target_devices', 'target_groups')
        }),
        ('任务内容', {
            'fields': ('template', 'template_vars', 'commands')
        }),
        ('执行状态', {
            'fields': (
                'status', 'progress', 'celery_task_id',
                'success_count', 'failed_count', 'total_count'
            )
        }),
        ('时间信息', {
            'fields': ('created_by', 'created_at', 'started_at', 'completed_at', 'duration_display'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['cancel_tasks']
    
    def status_badge(self, obj):
        """状态标识"""
        color_map = {
            'pending': 'gray',
            'running': 'blue',
            'success': 'green',
            'failed': 'red',
            'partial': 'orange',
            'cancelled': 'darkgray',
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">●</span> {}',
            color, obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def progress_bar(self, obj):
        """进度条"""
        return format_html(
            '<div style="width: 100px; height: 20px; background: #f0f0f0; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background: #4CAF50; line-height: 20px; text-align: center; color: white; font-size: 12px;">{}\u0025</div>'
            '</div>',
            obj.progress, obj.progress
        )
    progress_bar.short_description = '进度'
    
    def duration_display(self, obj):
        """时长显示"""
        duration = obj.duration
        if duration > 0:
            minutes, seconds = divmod(int(duration), 60)
            if minutes > 0:
                return f"{minutes} 分 {seconds} 秒"
            return f"{seconds} 秒"
        return '-'
    duration_display.short_description = '执行时长'
    
    def save_model(self, request, obj, form, change):
        """保存时记录创建者"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def cancel_tasks(self, request, queryset):
        """取消任务"""
        count = 0
        for task in queryset:
            if task.status in ['pending', 'running']:
                task.update_status('cancelled')
                count += 1
        self.message_user(request, f'成功取消 {count} 个任务', messages.SUCCESS)
    cancel_tasks.short_description = '取消选中的任务'


@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ['task', 'device', 'status_badge', 'duration_display', 'created_at']
    list_filter = ['status', 'task__task_type', 'created_at']
    search_fields = ['task__name', 'device__name', 'output', 'error']
    readonly_fields = ['task', 'device', 'status', 'output', 'error', 'started_at', 'completed_at', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def status_badge(self, obj):
        """状态标识"""
        color_map = {
            'pending': 'gray',
            'running': 'blue',
            'success': 'green',
            'failed': 'red',
            'skipped': 'orange',
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">●</span> {}',
            color, obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def duration_display(self, obj):
        """时长显示"""
        duration = obj.duration
        if duration > 0:
            return f"{duration:.2f} 秒"
        return '-'
    duration_display.short_description = '执行时长'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'task_type', 'frequency', 'is_active', 'next_run', 'last_run']
    list_filter = ['task_type', 'frequency', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['next_run', 'last_run', 'created_at', 'updated_at', 'created_by']
    filter_horizontal = ['target_devices', 'target_groups']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('任务配置', {
            'fields': ('task_type', 'target_devices', 'target_groups', 'template', 'template_vars', 'commands')
        }),
        ('调度配置', {
            'fields': ('frequency', 'cron_expression')
        }),
        ('执行信息', {
            'fields': ('next_run', 'last_run'),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_schedules', 'deactivate_schedules']
    
    def save_model(self, request, obj, form, change):
        """保存时记录创建者"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def activate_schedules(self, request, queryset):
        """激活定时任务"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {count} 个定时任务', messages.SUCCESS)
    activate_schedules.short_description = '激活选中的定时任务'
    
    def deactivate_schedules(self, request, queryset):
        """停用定时任务"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {count} 个定时任务', messages.SUCCESS)
    deactivate_schedules.short_description = '停用选中的定时任务'

