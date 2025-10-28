"""
模板管理 Admin 配置
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ConfigTemplate, TemplateVersion, TemplateVariable
import json


class TemplateVariableInline(admin.TabularInline):
    """模板变量内联"""
    model = TemplateVariable
    extra = 1
    fields = ['name', 'variable_type', 'default_value', 'description', 'required', 'order']


class TemplateVersionInline(admin.TabularInline):
    """模板版本内联"""
    model = TemplateVersion
    extra = 0
    fields = ['version', 'change_note', 'created_by', 'created_at']
    readonly_fields = ['version', 'created_by', 'created_at']
    can_delete = False
    max_num = 5  # 只显示最近 5 个版本


@admin.register(ConfigTemplate)
class ConfigTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'version', 'is_active', 'tags_display', 'updated_at', 'action_buttons']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'tags']
    readonly_fields = ['version', 'created_at', 'updated_at', 'created_by', 'preview_content']
    filter_horizontal = []
    inlines = [TemplateVariableInline, TemplateVersionInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'category', 'tags', 'description')
        }),
        ('模板内容', {
            'fields': ('content', 'preview_content')
        }),
        ('变量配置', {
            'fields': ('variables', 'example_vars'),
            'classes': ('collapse',)
        }),
        ('状态和版本', {
            'fields': ('is_active', 'version')
        }),
        ('元数据', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_templates', 'deactivate_templates', 'create_versions']
    
    def tags_display(self, obj):
        """标签显示"""
        tags = obj.get_tags_list()
        if tags:
            return format_html(' '.join([f'<span style="background: #e0e0e0; padding: 2px 6px; border-radius: 3px; margin-right: 3px;">{tag}</span>' for tag in tags]))
        return '-'
    tags_display.short_description = '标签'
    
    def preview_content(self, obj):
        """预览渲染结果"""
        if not obj.id:
            return '保存后可预览'
        
        try:
            rendered = obj.render()
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px;">{}</pre>', rendered)
        except Exception as e:
            return format_html('<span style="color: red;">渲染失败: {}</span>', str(e))
    preview_content.short_description = '预览'
    
    def action_buttons(self, obj):
        """操作按钮"""
        return format_html(
            '<a class="button" href="{}">预览</a> '
            '<a class="button" href="{}">创建版本</a>',
            f'/admin/templates_mgr/configtemplate/{obj.id}/preview/',
            f'/admin/templates_mgr/configtemplate/{obj.id}/create-version/'
        )
    action_buttons.short_description = '操作'
    
    def save_model(self, request, obj, form, change):
        """保存时记录创建者"""
        if not change:
            obj.created_by = request.user
        
        # 如果是修改且内容变化，创建版本历史
        if change and 'content' in form.changed_data:
            old_obj = ConfigTemplate.objects.get(pk=obj.pk)
            TemplateVersion.objects.create(
                template=obj,
                version=old_obj.version,
                content=old_obj.content,
                variables=old_obj.variables,
                change_note=f'自动保存版本 {old_obj.version}',
                created_by=request.user
            )
            obj.increment_version()
        
        super().save_model(request, obj, form, change)
    
    def activate_templates(self, request, queryset):
        """激活模板"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {count} 个模板', messages.SUCCESS)
    activate_templates.short_description = '激活选中的模板'
    
    def deactivate_templates(self, request, queryset):
        """停用模板"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {count} 个模板', messages.SUCCESS)
    deactivate_templates.short_description = '停用选中的模板'
    
    def create_versions(self, request, queryset):
        """创建版本快照"""
        count = 0
        for template in queryset:
            TemplateVersion.objects.create(
                template=template,
                version=template.version,
                content=template.content,
                variables=template.variables,
                change_note='手动创建版本快照',
                created_by=request.user
            )
            count += 1
        self.message_user(request, f'成功创建 {count} 个版本快照', messages.SUCCESS)
    create_versions.short_description = '创建版本快照'
    
    def get_urls(self):
        """添加自定义 URL"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:template_id>/preview/',
                self.admin_site.admin_view(self.preview_view),
                name='template-preview',
            ),
            path(
                '<int:template_id>/create-version/',
                self.admin_site.admin_view(self.create_version_view),
                name='template-create-version',
            ),
        ]
        return custom_urls + urls
    
    def preview_view(self, request, template_id):
        """预览视图"""
        template = ConfigTemplate.objects.get(pk=template_id)
        
        if request.method == 'POST':
            # 获取用户输入的变量
            variables = {}
            for key in request.POST:
                if key.startswith('var_'):
                    var_name = key[4:]
                    variables[var_name] = request.POST[key]
            
            try:
                rendered = template.render(variables)
                context = {
                    'template': template,
                    'variables': variables,
                    'rendered': rendered,
                }
            except Exception as e:
                context = {
                    'template': template,
                    'variables': variables,
                    'error': str(e),
                }
        else:
            try:
                rendered = template.render()
                context = {
                    'template': template,
                    'variables': template.example_vars,
                    'rendered': rendered,
                }
            except Exception as e:
                context = {
                    'template': template,
                    'variables': template.example_vars,
                    'error': str(e),
                }
        
        return render(request, 'admin/templates_mgr/template_preview.html', context)
    
    def create_version_view(self, request, template_id):
        """创建版本视图"""
        template = ConfigTemplate.objects.get(pk=template_id)
        
        if request.method == 'POST':
            change_note = request.POST.get('change_note', '')
            TemplateVersion.objects.create(
                template=template,
                version=template.version,
                content=template.content,
                variables=template.variables,
                change_note=change_note,
                created_by=request.user
            )
            self.message_user(request, f'已为 {template.name} 创建版本 {template.version}', messages.SUCCESS)
            return redirect('admin:templates_mgr_configtemplate_changelist')
        
        return render(request, 'admin/templates_mgr/create_version.html', {'template': template})


@admin.register(TemplateVersion)
class TemplateVersionAdmin(admin.ModelAdmin):
    list_display = ['template', 'version', 'change_note', 'created_by', 'created_at']
    list_filter = ['template', 'created_at']
    search_fields = ['template__name', 'change_note']
    readonly_fields = ['template', 'version', 'content', 'variables', 'created_by', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # 只允许删除旧版本
        return True


@admin.register(TemplateVariable)
class TemplateVariableAdmin(admin.ModelAdmin):
    list_display = ['template', 'name', 'variable_type', 'required', 'order']
    list_filter = ['variable_type', 'required']
    search_fields = ['template__name', 'name', 'description']
    ordering = ['template', 'order', 'name']

