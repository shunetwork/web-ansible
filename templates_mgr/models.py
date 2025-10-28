"""
模板管理模型
"""
from django.db import models
from django.contrib.auth.models import User
from jinja2 import Template, TemplateSyntaxError
from django.core.exceptions import ValidationError


class ConfigTemplate(models.Model):
    """配置模板"""
    
    CATEGORY_CHOICES = [
        ('interface', '接口配置'),
        ('routing', '路由配置'),
        ('acl', '访问控制列表'),
        ('vlan', 'VLAN 配置'),
        ('qos', 'QoS 配置'),
        ('security', '安全配置'),
        ('system', '系统配置'),
        ('other', '其他'),
    ]
    
    # 基本信息
    name = models.CharField('模板名称', max_length=200, unique=True)
    category = models.CharField('分类', max_length=50, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField('描述', blank=True)
    
    # 模板内容（Jinja2 格式）
    content = models.TextField('模板内容')
    
    # 变量定义（JSON 格式）
    variables = models.JSONField('变量定义', default=dict, blank=True, help_text='定义模板中使用的变量及其默认值')
    
    # 示例数据
    example_vars = models.JSONField('示例变量', default=dict, blank=True, help_text='用于预览的示例变量值')
    
    # 版本控制
    version = models.IntegerField('版本号', default=1)
    is_active = models.BooleanField('是否启用', default=True)
    
    # 标签
    tags = models.CharField('标签', max_length=200, blank=True, help_text='用逗号分隔的标签')
    
    # 创建者
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.SET_NULL, null=True, related_name='created_templates')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '配置模板'
        verbose_name_plural = '配置模板'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    def clean(self):
        """验证模板语法"""
        try:
            Template(self.content)
        except TemplateSyntaxError as e:
            raise ValidationError({'content': f'模板语法错误: {str(e)}'})
    
    def render(self, variables=None):
        """渲染模板"""
        if variables is None:
            variables = self.example_vars
        
        try:
            template = Template(self.content)
            return template.render(**variables)
        except Exception as e:
            raise ValueError(f'模板渲染失败: {str(e)}')
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def increment_version(self):
        """增加版本号"""
        self.version += 1
        self.save(update_fields=['version', 'updated_at'])


class TemplateVersion(models.Model):
    """模板版本历史"""
    template = models.ForeignKey(ConfigTemplate, verbose_name='模板', on_delete=models.CASCADE, related_name='versions')
    version = models.IntegerField('版本号')
    content = models.TextField('模板内容')
    variables = models.JSONField('变量定义', default=dict)
    change_note = models.TextField('变更说明', blank=True)
    created_by = models.ForeignKey(User, verbose_name='创建者', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '模板版本'
        verbose_name_plural = '模板版本'
        ordering = ['-version']
        unique_together = ['template', 'version']

    def __str__(self):
        return f"{self.template.name} v{self.version}"


class TemplateVariable(models.Model):
    """模板变量定义"""
    
    TYPE_CHOICES = [
        ('string', '字符串'),
        ('integer', '整数'),
        ('boolean', '布尔值'),
        ('list', '列表'),
        ('dict', '字典'),
    ]
    
    template = models.ForeignKey(ConfigTemplate, verbose_name='模板', on_delete=models.CASCADE, related_name='variable_definitions')
    name = models.CharField('变量名', max_length=100)
    variable_type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='string')
    default_value = models.TextField('默认值', blank=True)
    description = models.CharField('描述', max_length=500, blank=True)
    required = models.BooleanField('必填', default=False)
    order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '模板变量'
        verbose_name_plural = '模板变量'
        ordering = ['order', 'name']
        unique_together = ['template', 'name']

    def __str__(self):
        return f"{self.template.name}.{self.name}"

