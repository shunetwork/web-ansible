"""
Pytest 配置和 fixtures
"""
import pytest
from django.contrib.auth.models import User
from devices.models import Device, DeviceGroup
from templates_mgr.models import ConfigTemplate
from tasks.models import Task
from backups.models import ConfigBackup


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """创建管理员用户"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def device_group(db):
    """创建测试设备组"""
    return DeviceGroup.objects.create(
        name='Test Group',
        description='Test device group'
    )


@pytest.fixture
def test_device(db, test_user, device_group):
    """创建测试设备"""
    device = Device.objects.create(
        name='Test Switch',
        hostname='test-sw-01',
        ip_address='192.168.1.1',
        device_type='switch',
        model='Catalyst 2960',
        serial_number='SN123456',
        ssh_port=22,
        username='admin',
        password='password',
        os_version='15.2(4)E',
        status='online',
        is_active=True,
        location='Test Lab',
        created_by=test_user
    )
    device.groups.add(device_group)
    return device


@pytest.fixture
def config_template(db, test_user):
    """创建配置模板"""
    return ConfigTemplate.objects.create(
        name='Test Template',
        category='interface',
        description='Test interface configuration',
        content='interface {{ interface_name }}\n description {{ description }}\n no shutdown',
        variables={'interface_name': 'GigabitEthernet0/1', 'description': 'Test Interface'},
        example_vars={'interface_name': 'GigabitEthernet0/1', 'description': 'Test Interface'},
        is_active=True,
        created_by=test_user
    )


@pytest.fixture
def test_task(db, test_user, test_device, config_template):
    """创建测试任务"""
    task = Task.objects.create(
        name='Test Task',
        task_type='template',
        description='Test task for template deployment',
        template=config_template,
        template_vars={'interface_name': 'GigabitEthernet0/2', 'description': 'Production Interface'},
        status='pending',
        created_by=test_user
    )
    task.target_devices.add(test_device)
    return task


@pytest.fixture
def config_backup(db, test_device, test_user):
    """创建配置备份"""
    return ConfigBackup.objects.create(
        device=test_device,
        config_content='! Test configuration\nversion 15.2\nhostname test-sw-01',
        file_path='/tmp/test_backup.cfg',
        file_size=1024,
        status='success',
        backup_type='manual',
        created_by=test_user
    )

