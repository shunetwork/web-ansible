"""
审计日志模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AuditLog(models.Model):
    """审计日志"""
    
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('view', '查看'),
        ('execute', '执行'),
        ('login', '登录'),
        ('logout', '登出'),
        ('export', '导出'),
        ('import', '导入'),
        ('backup', '备份'),
        ('restore', '恢复'),
        ('other', '其他'),
    ]
    
    LEVEL_CHOICES = [
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('critical', '严重'),
    ]
    
    # 用户信息
    user = models.ForeignKey(User, verbose_name='操作用户', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    username = models.CharField('用户名', max_length=150)  # 冗余存储，防止用户删除
    ip_address = models.GenericIPAddressField('IP 地址', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    
    # 操作信息
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    description = models.TextField('操作描述')
    level = models.CharField('级别', max_length=20, choices=LEVEL_CHOICES, default='info')
    
    # 关联对象（使用 GenericForeignKey）
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField('对象表示', max_length=200, blank=True)
    
    # 详细信息
    changes = models.JSONField('变更详情', default=dict, blank=True)
    extra_data = models.JSONField('额外数据', default=dict, blank=True)
    
    # 结果
    success = models.BooleanField('是否成功', default=True)
    error_message = models.TextField('错误信息', blank=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['level', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.username} - {self.get_action_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @classmethod
    def log(cls, user, action, description, **kwargs):
        """快速创建审计日志"""
        return cls.objects.create(
            user=user,
            username=user.username if user else 'Anonymous',
            action=action,
            description=description,
            **kwargs
        )


class LoginHistory(models.Model):
    """登录历史"""
    
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
    ]
    
    # 用户信息
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, related_name='login_history', null=True, blank=True)
    username = models.CharField('用户名', max_length=150)
    
    # 登录信息
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES)
    ip_address = models.GenericIPAddressField('IP 地址', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    
    # 失败原因
    failure_reason = models.CharField('失败原因', max_length=200, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField('登录时间', auto_now_add=True)

    class Meta:
        verbose_name = '登录历史'
        verbose_name_plural = '登录历史'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.username} - {self.get_status_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class OperationStatistics(models.Model):
    """操作统计（按天汇总）"""
    
    # 日期
    date = models.DateField('日期', unique=True)
    
    # 用户统计
    active_users = models.IntegerField('活跃用户数', default=0)
    new_users = models.IntegerField('新增用户数', default=0)
    
    # 登录统计
    login_success = models.IntegerField('登录成功次数', default=0)
    login_failed = models.IntegerField('登录失败次数', default=0)
    
    # 操作统计
    total_operations = models.IntegerField('总操作次数', default=0)
    create_operations = models.IntegerField('创建操作', default=0)
    update_operations = models.IntegerField('更新操作', default=0)
    delete_operations = models.IntegerField('删除操作', default=0)
    execute_operations = models.IntegerField('执行操作', default=0)
    
    # 任务统计
    tasks_created = models.IntegerField('创建任务数', default=0)
    tasks_success = models.IntegerField('成功任务数', default=0)
    tasks_failed = models.IntegerField('失败任务数', default=0)
    
    # 备份统计
    backups_created = models.IntegerField('创建备份数', default=0)
    backups_success = models.IntegerField('成功备份数', default=0)
    backups_failed = models.IntegerField('失败备份数', default=0)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '操作统计'
        verbose_name_plural = '操作统计'
        ordering = ['-date']

    def __str__(self):
        return f"统计 - {self.date}"

