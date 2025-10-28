"""
任务执行模型
"""
from django.db import models
from django.contrib.auth.models import User
from devices.models import Device, DeviceGroup
from templates_mgr.models import ConfigTemplate
from django.utils import timezone


class Task(models.Model):
    """任务"""
    
    TASK_TYPE_CHOICES = [
        ('command', '命令执行'),
        ('template', '模板下发'),
        ('backup', '配置备份'),
        ('health_check', '健康检查'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '执行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('partial', '部分成功'),
        ('cancelled', '已取消'),
    ]
    
    # 基本信息
    name = models.CharField('任务名称', max_length=200)
    task_type = models.CharField('任务类型', max_length=20, choices=TASK_TYPE_CHOICES)
    description = models.TextField('描述', blank=True)
    
    # 目标设备
    target_devices = models.ManyToManyField(Device, verbose_name='目标设备', related_name='tasks', blank=True)
    target_groups = models.ManyToManyField(DeviceGroup, verbose_name='目标设备组', related_name='tasks', blank=True)
    
    # 任务内容
    template = models.ForeignKey(ConfigTemplate, verbose_name='配置模板', on_delete=models.SET_NULL, null=True, blank=True)
    template_vars = models.JSONField('模板变量', default=dict, blank=True)
    commands = models.TextField('命令列表', blank=True, help_text='每行一个命令')
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField('进度', default=0, help_text='百分比 0-100')
    
    # Celery 任务 ID
    celery_task_id = models.CharField('Celery 任务 ID', max_length=100, blank=True)
    
    # 执行结果
    success_count = models.IntegerField('成功数', default=0)
    failed_count = models.IntegerField('失败数', default=0)
    total_count = models.IntegerField('总数', default=0)
    
    # 创建者
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['task_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_task_type_display()})"
    
    def get_all_target_devices(self):
        """获取所有目标设备（包括组内设备）"""
        devices = set(self.target_devices.all())
        for group in self.target_groups.all():
            devices.update(group.devices.all())
        return list(devices)
    
    def update_status(self, status, progress=None):
        """更新任务状态"""
        self.status = status
        if progress is not None:
            self.progress = progress
        
        if status == 'running' and not self.started_at:
            self.started_at = timezone.now()
        elif status in ['success', 'failed', 'partial', 'cancelled']:
            self.completed_at = timezone.now()
        
        self.save(update_fields=['status', 'progress', 'started_at', 'completed_at'])
    
    def update_counts(self, success=0, failed=0):
        """更新统计数"""
        self.success_count = success
        self.failed_count = failed
        self.total_count = success + failed
        
        # 更新进度
        if self.total_count > 0:
            self.progress = int((success + failed) / len(self.get_all_target_devices()) * 100)
        
        self.save(update_fields=['success_count', 'failed_count', 'total_count', 'progress'])
    
    @property
    def duration(self):
        """执行时长"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (timezone.now() - self.started_at).total_seconds()
        return 0


class TaskResult(models.Model):
    """任务执行结果"""
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '执行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('skipped', '已跳过'),
    ]
    
    # 关联
    task = models.ForeignKey(Task, verbose_name='任务', on_delete=models.CASCADE, related_name='results')
    device = models.ForeignKey(Device, verbose_name='设备', on_delete=models.CASCADE, related_name='task_results')
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 执行结果
    output = models.TextField('输出', blank=True)
    error = models.TextField('错误信息', blank=True)
    
    # 时间戳
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '任务结果'
        verbose_name_plural = '任务结果'
        ordering = ['device__name']
        unique_together = ['task', 'device']
        indexes = [
            models.Index(fields=['task', 'status']),
            models.Index(fields=['device', 'created_at']),
        ]

    def __str__(self):
        return f"{self.task.name} - {self.device.name} ({self.get_status_display()})"
    
    @property
    def duration(self):
        """执行时长"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0


class Schedule(models.Model):
    """定时任务"""
    
    FREQUENCY_CHOICES = [
        ('once', '一次性'),
        ('hourly', '每小时'),
        ('daily', '每天'),
        ('weekly', '每周'),
        ('monthly', '每月'),
    ]
    
    # 基本信息
    name = models.CharField('任务名称', max_length=200)
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    
    # 任务配置
    task_type = models.CharField('任务类型', max_length=20, choices=Task.TASK_TYPE_CHOICES)
    target_devices = models.ManyToManyField(Device, verbose_name='目标设备', related_name='schedules', blank=True)
    target_groups = models.ManyToManyField(DeviceGroup, verbose_name='目标设备组', related_name='schedules', blank=True)
    template = models.ForeignKey(ConfigTemplate, verbose_name='配置模板', on_delete=models.SET_NULL, null=True, blank=True)
    template_vars = models.JSONField('模板变量', default=dict, blank=True)
    commands = models.TextField('命令列表', blank=True)
    
    # 调度配置
    frequency = models.CharField('频率', max_length=20, choices=FREQUENCY_CHOICES)
    cron_expression = models.CharField('Cron 表达式', max_length=100, blank=True, help_text='自定义 Cron 表达式')
    
    # 执行时间
    next_run = models.DateTimeField('下次执行时间', null=True, blank=True)
    last_run = models.DateTimeField('上次执行时间', null=True, blank=True)
    
    # 创建者
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.SET_NULL, null=True, related_name='created_schedules')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '定时任务'
        verbose_name_plural = '定时任务'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"

