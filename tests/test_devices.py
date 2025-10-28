"""
设备管理模块测试
"""
import pytest
from django.contrib.auth.models import User
from devices.models import Device, DeviceGroup, DeviceCredential


@pytest.mark.django_db
class TestDeviceGroup:
    """设备组测试"""
    
    def test_create_device_group(self):
        """测试创建设备组"""
        group = DeviceGroup.objects.create(
            name='Core Switches',
            description='Core network switches'
        )
        assert group.name == 'Core Switches'
        assert str(group) == 'Core Switches'
    
    def test_device_count(self, device_group, test_device):
        """测试设备计数"""
        assert device_group.devices.count() == 1


@pytest.mark.django_db
class TestDevice:
    """设备测试"""
    
    def test_create_device(self, test_device):
        """测试创建设备"""
        assert test_device.name == 'Test Switch'
        assert test_device.ip_address == '192.168.1.1'
        assert test_device.device_type == 'switch'
    
    def test_device_str(self, test_device):
        """测试设备字符串表示"""
        assert str(test_device) == 'Test Switch (192.168.1.1)'
    
    def test_update_status(self, test_device):
        """测试更新设备状态"""
        test_device.update_status('offline', 'Connection timeout')
        test_device.refresh_from_db()
        assert test_device.status == 'offline'
        assert test_device.last_check_result == 'Connection timeout'
        assert test_device.last_check is not None
    
    def test_get_ansible_vars(self, test_device):
        """测试获取 Ansible 变量"""
        ansible_vars = test_device.get_ansible_vars()
        assert ansible_vars['ansible_host'] == '192.168.1.1'
        assert ansible_vars['ansible_port'] == 22
        assert ansible_vars['ansible_user'] == 'admin'
        assert ansible_vars['ansible_network_os'] == 'ios'
    
    def test_device_groups(self, test_device, device_group):
        """测试设备分组"""
        assert test_device.groups.count() == 1
        assert device_group in test_device.groups.all()


@pytest.mark.django_db
class TestDeviceCredential:
    """设备凭据测试"""
    
    def test_create_credential(self):
        """测试创建设备凭据"""
        cred = DeviceCredential.objects.create(
            name='Default Cisco',
            username='cisco',
            password='cisco123',
            enable_password='enable123',
            description='Default Cisco credentials'
        )
        assert cred.name == 'Default Cisco'
        assert str(cred) == 'Default Cisco'

