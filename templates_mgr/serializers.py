"""
模板管理序列化器
"""
from rest_framework import serializers
from .models import ConfigTemplate, TemplateVersion, TemplateVariable


class TemplateVariableSerializer(serializers.ModelSerializer):
    """模板变量序列化器"""
    
    class Meta:
        model = TemplateVariable
        fields = ['id', 'template', 'name', 'variable_type', 'default_value', 'description', 'required', 'order']


class TemplateVersionSerializer(serializers.ModelSerializer):
    """模板版本序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = TemplateVersion
        fields = ['id', 'template', 'version', 'content', 'variables', 'change_note', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['created_at']


class ConfigTemplateSerializer(serializers.ModelSerializer):
    """配置模板序列化器"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    tags_list = serializers.SerializerMethodField()
    variables_list = TemplateVariableSerializer(source='variable_definitions', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ConfigTemplate
        fields = [
            'id', 'name', 'category', 'category_display', 'description',
            'content', 'variables', 'example_vars', 'variables_list',
            'version', 'is_active', 'tags', 'tags_list',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['version', 'created_at', 'updated_at']
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    def validate_content(self, value):
        """验证模板内容"""
        from jinja2 import Template, TemplateSyntaxError
        try:
            Template(value)
        except TemplateSyntaxError as e:
            raise serializers.ValidationError(f'模板语法错误: {str(e)}')
        return value


class TemplateRenderSerializer(serializers.Serializer):
    """模板渲染请求序列化器"""
    variables = serializers.JSONField(required=False, default=dict)

