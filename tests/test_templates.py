"""
模板管理模块测试
"""
import pytest
from django.core.exceptions import ValidationError
from templates_mgr.models import ConfigTemplate, TemplateVersion, TemplateVariable


@pytest.mark.django_db
class TestConfigTemplate:
    """配置模板测试"""
    
    def test_create_template(self, config_template):
        """测试创建模板"""
        assert config_template.name == 'Test Template'
        assert config_template.category == 'interface'
        assert config_template.version == 1
        assert config_template.is_active is True
    
    def test_template_str(self, config_template):
        """测试模板字符串表示"""
        assert str(config_template) == 'Test Template (v1)'
    
    def test_template_validation(self, test_user):
        """测试模板语法验证"""
        # 有效的模板
        valid_template = ConfigTemplate(
            name='Valid Template',
            category='interface',
            content='interface {{ name }}',
            created_by=test_user
        )
        valid_template.clean()  # 不应抛出异常
        
        # 无效的模板
        invalid_template = ConfigTemplate(
            name='Invalid Template',
            category='interface',
            content='interface {{ name',  # 缺少闭合括号
            created_by=test_user
        )
        with pytest.raises(ValidationError):
            invalid_template.clean()
    
    def test_render_template(self, config_template):
        """测试模板渲染"""
        rendered = config_template.render({
            'interface_name': 'GigabitEthernet0/3',
            'description': 'Uplink to Core'
        })
        assert 'GigabitEthernet0/3' in rendered
        assert 'Uplink to Core' in rendered
    
    def test_render_with_default_vars(self, config_template):
        """测试使用默认变量渲染"""
        rendered = config_template.render()
        assert 'GigabitEthernet0/1' in rendered
        assert 'Test Interface' in rendered
    
    def test_get_tags_list(self, config_template):
        """测试获取标签列表"""
        config_template.tags = 'cisco, switch, interface'
        config_template.save()
        tags = config_template.get_tags_list()
        assert tags == ['cisco', 'switch', 'interface']
    
    def test_increment_version(self, config_template):
        """测试增加版本号"""
        old_version = config_template.version
        config_template.increment_version()
        config_template.refresh_from_db()
        assert config_template.version == old_version + 1


@pytest.mark.django_db
class TestTemplateVersion:
    """模板版本测试"""
    
    def test_create_version(self, config_template, test_user):
        """测试创建版本"""
        version = TemplateVersion.objects.create(
            template=config_template,
            version=1,
            content=config_template.content,
            variables=config_template.variables,
            change_note='Initial version',
            created_by=test_user
        )
        assert version.template == config_template
        assert version.version == 1
        assert str(version) == 'Test Template v1'


@pytest.mark.django_db
class TestTemplateVariable:
    """模板变量测试"""
    
    def test_create_variable(self, config_template):
        """测试创建模板变量"""
        var = TemplateVariable.objects.create(
            template=config_template,
            name='interface_name',
            variable_type='string',
            default_value='GigabitEthernet0/1',
            description='Interface name',
            required=True,
            order=1
        )
        assert var.name == 'interface_name'
        assert var.variable_type == 'string'
        assert var.required is True
        assert str(var) == 'Test Template.interface_name'

