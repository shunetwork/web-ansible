"""
设备管理模型
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_ipv4_address
from django.utils import timezone


class DeviceGroup(models.Model):
    """设备组"""
    name = models.CharField('组名', max_length=100, unique=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '设备组'
        verbose_name_plural = '设备组'
        ordering = ['name']

    def __str__(self):
        return self.name


class Device(models.Model):
    """网络设备"""
    
    # 设备类型选择
    DEVICE_TYPE_CHOICES = [
        ('router', '路由器'),
        ('switch', '交换机'),
        ('firewall', '防火墙'),
        ('other', '其他'),
    ]
    
    # 设备状态
    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('maintenance', '维护中'),
        ('unknown', '未知'),
    ]
    
    # 基本信息
    name = models.CharField('设备名称', max_length=100)
    hostname = models.CharField('主机名', max_length=255, unique=True)
    ip_address = models.GenericIPAddressField('IP 地址', validators=[validate_ipv4_address], unique=True)
    device_type = models.CharField('设备类型', max_length=20, choices=DEVICE_TYPE_CHOICES, default='switch')
    model = models.CharField('设备型号', max_length=100, blank=True)
    serial_number = models.CharField('序列号', max_length=100, blank=True)
    
    # 连接信息
    ssh_port = models.IntegerField('SSH 端口', default=22)
    username = models.CharField('用户名', max_length=100)
    password = models.CharField('密码', max_length=255)  # 生产环境应该加密存储
    enable_password = models.CharField('Enable 密码', max_length=255, blank=True)
    
    # 版本信息
    os_version = models.CharField('OS 版本', max_length=100, blank=True)
    
    # 分组
    groups = models.ManyToManyField(DeviceGroup, verbose_name='所属组', blank=True, related_name='devices')
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='unknown')
    is_active = models.BooleanField('是否启用', default=True)
    
    # 元数据
    description = models.TextField('描述', blank=True)
    location = models.CharField('位置', max_length=200, blank=True)
    
    # 健康检查
    last_check = models.DateTimeField('最后检查时间', null=True, blank=True)
    last_check_result = models.TextField('最后检查结果', blank=True)
    
    # 创建者
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.SET_NULL, null=True, related_name='created_devices')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '网络设备'
        verbose_name_plural = '网络设备'
        ordering = ['name']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['hostname']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.ip_address})"
    
    def update_status(self, status, check_result=''):
        """更新设备状态"""
        self.status = status
        self.last_check = timezone.now()
        self.last_check_result = check_result
        self.save(update_fields=['status', 'last_check', 'last_check_result', 'updated_at'])
    
    def get_ansible_vars(self):
        """获取 Ansible 变量"""
        return {
            'ansible_host': self.ip_address,
            'ansible_port': self.ssh_port,
            'ansible_user': self.username,
            'ansible_password': self.password,
            'ansible_network_os': 'ios',  # Cisco IOS
            'ansible_connection': 'network_cli',
            'device_type': self.device_type,
            'hostname': self.hostname,
        }


class DeviceCredential(models.Model):
    """设备凭据（用于批量管理）"""
    name = models.CharField('凭据名称', max_length=100, unique=True)
    username = models.CharField('用户名', max_length=100)
    password = models.CharField('密码', max_length=255)
    enable_password = models.CharField('Enable 密码', max_length=255, blank=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '设备凭据'
        verbose_name_plural = '设备凭据'

    def __str__(self):
        return self.name

