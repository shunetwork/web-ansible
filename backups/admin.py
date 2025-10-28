"""
配置备份 Admin 配置
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ConfigBackup, ConfigDiff, RestoreHistory
from .tasks import backup_device_config, restore_device_config


@admin.register(ConfigBackup)
class ConfigBackupAdmin(admin.ModelAdmin):
    list_display = [
        'device', 'created_at', 'file_size_display', 'status_badge',
        'backup_type', 'has_changes_display', 'action_buttons'
    ]
    list_filter = ['status', 'backup_type', 'created_at', 'device']
    search_fields = ['device__name', 'device__ip_address', 'description']
    readonly_fields = [
        'device', 'config_content', 'file_path', 'file_size', 'status',
        'error_message', 'created_at', 'created_by', 'file_size_display'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('device', 'backup_type', 'description')
        }),
        ('配置内容', {
            'fields': ('config_content',)
        }),
        ('文件信息', {
            'fields': ('file_path', 'file_size', 'file_size_display')
        }),
        ('状态', {
            'fields': ('status', 'error_message')
        }),
        ('元数据', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['compare_backups', 'restore_backups']
    
    def status_badge(self, obj):
        """状态标识"""
        color_map = {
            'success': 'green',
            'failed': 'red',
            'in_progress': 'blue',
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">●</span> {}',
            color, obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def file_size_display(self, obj):
        """文件大小显示"""
        return obj.get_file_size_display()
    file_size_display.short_description = '文件大小'
    
    def has_changes_display(self, obj):
        """是否有变化"""
        if obj.has_changes():
            return format_html('<span style="color: orange;">●</span> 有变化')
        return format_html('<span style="color: green;">-</span> 无变化')
    has_changes_display.short_description = '变化'
    
    def action_buttons(self, obj):
        """操作按钮"""
        return format_html(
            '<a class="button" href="{}">对比</a> '
            '<a class="button" href="{}">恢复</a>',
            f'/admin/backups/configbackup/{obj.id}/compare/',
            f'/admin/backups/configbackup/{obj.id}/restore/'
        )
    action_buttons.short_description = '操作'
    
    def has_add_permission(self, request):
        return False
    
    def compare_backups(self, request, queryset):
        """对比备份"""
        if queryset.count() != 2:
            self.message_user(request, '请选择两个备份进行对比', messages.WARNING)
            return
        
        backups = list(queryset.order_by('created_at'))
        backup_old, backup_new = backups[0], backups[1]
        
        diff_content = backup_new.compare_with(backup_old)
        
        # 创建差异记录
        ConfigDiff.objects.get_or_create(
            backup_old=backup_old,
            backup_new=backup_new,
            defaults={'diff_content': diff_content, 'created_by': request.user}
        )
        
        self.message_user(request, '已生成差异对比', messages.SUCCESS)
    compare_backups.short_description = '对比选中的备份'
    
    def restore_backups(self, request, queryset):
        """恢复备份"""
        for backup in queryset:
            if backup.status == 'success':
                restore_device_config.delay(backup.id, request.user.id)
        self.message_user(request, f'已提交 {queryset.count()} 个恢复任务', messages.SUCCESS)
    restore_backups.short_description = '恢复选中的备份'
    
    def get_urls(self):
        """添加自定义 URL"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:backup_id>/compare/',
                self.admin_site.admin_view(self.compare_view),
                name='backup-compare',
            ),
            path(
                '<int:backup_id>/restore/',
                self.admin_site.admin_view(self.restore_view),
                name='backup-restore',
            ),
        ]
        return custom_urls + urls
    
    def compare_view(self, request, backup_id):
        """对比视图"""
        backup = ConfigBackup.objects.get(pk=backup_id)
        previous = backup.get_previous_backup()
        
        if not previous:
            self.message_user(request, '没有可对比的历史备份', messages.WARNING)
            return redirect('admin:backups_configbackup_changelist')
        
        diff_content = backup.compare_with(previous)
        
        context = {
            'backup': backup,
            'previous': previous,
            'diff_content': diff_content,
        }
        
        return render(request, 'admin/backups/backup_compare.html', context)
    
    def restore_view(self, request, backup_id):
        """恢复视图"""
        backup = ConfigBackup.objects.get(pk=backup_id)
        
        if request.method == 'POST':
            restore_device_config.delay(backup_id, request.user.id)
            self.message_user(request, f'已提交 {backup.device.name} 的配置恢复任务', messages.SUCCESS)
            return redirect('admin:backups_configbackup_changelist')
        
        return render(request, 'admin/backups/backup_restore.html', {'backup': backup})


@admin.register(ConfigDiff)
class ConfigDiffAdmin(admin.ModelAdmin):
    list_display = [
        'backup_old', 'backup_new', 'lines_added', 'lines_removed',
        'lines_changed', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['backup_old__device__name', 'backup_new__device__name']
    readonly_fields = [
        'backup_old', 'backup_new', 'diff_content',
        'lines_added', 'lines_removed', 'lines_changed',
        'created_by', 'created_at'
    ]
    
    def has_add_permission(self, request):
        return False


@admin.register(RestoreHistory)
class RestoreHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'device', 'backup', 'status_badge', 'created_at',
        'started_at', 'completed_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['device__name', 'device__ip_address']
    readonly_fields = [
        'device', 'backup', 'status', 'output', 'error_message',
        'created_by', 'created_at', 'started_at', 'completed_at'
    ]
    
    def status_badge(self, obj):
        """状态标识"""
        color_map = {
            'pending': 'gray',
            'in_progress': 'blue',
            'success': 'green',
            'failed': 'red',
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">●</span> {}',
            color, obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def has_add_permission(self, request):
        return False

