"""
配置备份模型
"""
from django.db import models
from django.contrib.auth.models import User
from devices.models import Device
import os
import difflib
from django.conf import settings


class ConfigBackup(models.Model):
    """配置备份"""
    
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('in_progress', '进行中'),
    ]
    
    # 关联设备
    device = models.ForeignKey(Device, verbose_name='设备', on_delete=models.CASCADE, related_name='backups')
    
    # 备份信息
    config_content = models.TextField('配置内容')
    file_path = models.CharField('文件路径', max_length=500)
    file_size = models.IntegerField('文件大小(字节)', default=0)
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='success')
    error_message = models.TextField('错误信息', blank=True)
    
    # 元数据
    backup_type = models.CharField('备份类型', max_length=50, default='manual', help_text='manual/scheduled/auto')
    description = models.TextField('备份说明', blank=True)
    
    # 创建者（手动备份时）
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_backups')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '配置备份'
        verbose_name_plural = '配置备份'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def get_file_size_display(self):
        """文件大小显示"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"
    
    def compare_with(self, other_backup):
        """与其他备份对比"""
        if not other_backup:
            return None
        
        diff = difflib.unified_diff(
            other_backup.config_content.splitlines(keepends=True),
            self.config_content.splitlines(keepends=True),
            fromfile=f"{other_backup.device.name} ({other_backup.created_at})",
            tofile=f"{self.device.name} ({self.created_at})"
        )
        
        return ''.join(diff)
    
    def get_previous_backup(self):
        """获取上一个备份"""
        return ConfigBackup.objects.filter(
            device=self.device,
            created_at__lt=self.created_at,
            status='success'
        ).first()
    
    def has_changes(self):
        """是否有变化"""
        previous = self.get_previous_backup()
        if not previous:
            return True
        return self.config_content != previous.config_content
    
    def delete_file(self):
        """删除备份文件"""
        if self.file_path and os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
                return True
            except Exception:
                return False
        return False


class ConfigDiff(models.Model):
    """配置差异记录"""
    
    # 对比的两个备份
    backup_old = models.ForeignKey(ConfigBackup, verbose_name='旧备份', on_delete=models.CASCADE, related_name='diffs_as_old')
    backup_new = models.ForeignKey(ConfigBackup, verbose_name='新备份', on_delete=models.CASCADE, related_name='diffs_as_new')
    
    # 差异内容
    diff_content = models.TextField('差异内容')
    
    # 统计
    lines_added = models.IntegerField('新增行数', default=0)
    lines_removed = models.IntegerField('删除行数', default=0)
    lines_changed = models.IntegerField('修改行数', default=0)
    
    # 创建者
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.SET_NULL, null=True, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '配置差异'
        verbose_name_plural = '配置差异'
        ordering = ['-created_at']
        unique_together = ['backup_old', 'backup_new']

    def __str__(self):
        return f"{self.backup_old.device.name} 差异对比 ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"


class RestoreHistory(models.Model):
    """恢复历史记录"""
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('in_progress', '进行中'),
        ('success', '成功'),
        ('failed', '失败'),
    ]
    
    # 关联
    device = models.ForeignKey(Device, verbose_name='设备', on_delete=models.CASCADE, related_name='restore_history')
    backup = models.ForeignKey(ConfigBackup, verbose_name='备份', on_delete=models.CASCADE, related_name='restore_history')
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 结果
    output = models.TextField('输出', blank=True)
    error_message = models.TextField('错误信息', blank=True)
    
    # 创建者
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.SET_NULL, null=True, related_name='created_restores')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        verbose_name = '恢复历史'
        verbose_name_plural = '恢复历史'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device.name} 恢复 ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"

