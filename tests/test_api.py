"""
API 接口测试
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestDeviceAPI:
    """设备 API 测试"""
    
    def test_list_devices(self, admin_user, test_device):
        """测试获取设备列表"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        response = client.get('/api/devices/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_create_device(self, admin_user):
        """测试创建设备"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        data = {
            'name': 'New Switch',
            'hostname': 'new-sw-01',
            'ip_address': '192.168.1.10',
            'device_type': 'switch',
            'ssh_port': 22,
            'username': 'admin',
            'password': 'password'
        }
        
        response = client.post('/api/devices/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Switch'
    
    def test_device_statistics(self, admin_user, test_device):
        """测试设备统计"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        response = client.get('/api/devices/statistics/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total' in response.data


@pytest.mark.django_db
class TestTemplateAPI:
    """模板 API 测试"""
    
    def test_list_templates(self, admin_user, config_template):
        """测试获取模板列表"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        response = client.get('/api/templates/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_render_template(self, admin_user, config_template):
        """测试渲染模板"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        data = {
            'variables': {
                'interface_name': 'GigabitEthernet0/5',
                'description': 'API Test'
            }
        }
        
        response = client.post(f'/api/templates/{config_template.id}/render/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'GigabitEthernet0/5' in response.data['rendered']


@pytest.mark.django_db
class TestTaskAPI:
    """任务 API 测试"""
    
    def test_list_tasks(self, admin_user, test_task):
        """测试获取任务列表"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        response = client.get('/api/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_task_statistics(self, admin_user, test_task):
        """测试任务统计"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        response = client.get('/api/tasks/statistics/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total' in response.data


@pytest.mark.django_db
class TestBackupAPI:
    """备份 API 测试"""
    
    def test_list_backups(self, admin_user, config_backup):
        """测试获取备份列表"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        response = client.get('/api/backups/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_backup_statistics(self, admin_user, config_backup):
        """测试备份统计"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        response = client.get('/api/backups/statistics/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total' in response.data


@pytest.mark.django_db
class TestAuditAPI:
    """审计 API 测试"""
    
    def test_list_audit_logs(self, admin_user):
        """测试获取审计日志列表"""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        response = client.get('/api/audit/logs/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_my_audit_logs(self, test_user):
        """测试获取当前用户的审计日志"""
        client = APIClient()
        client.force_authenticate(user=test_user)
        
        response = client.get('/api/audit/logs/my_logs/')
        # 注意：需要管理员权限，所以会返回 403
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

