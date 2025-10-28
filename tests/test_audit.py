"""
审计日志模块测试
"""
import pytest
from audit.models import AuditLog, LoginHistory, OperationStatistics
from django.utils import timezone


@pytest.mark.django_db
class TestAuditLog:
    """审计日志测试"""
    
    def test_create_audit_log(self, test_user):
        """测试创建审计日志"""
        log = AuditLog.objects.create(
            user=test_user,
            username=test_user.username,
            ip_address='192.168.1.100',
            action='create',
            description='创建设备 Test Switch',
            level='info',
            success=True
        )
        assert log.user == test_user
        assert log.username == test_user.username
        assert log.action == 'create'
        assert log.success is True
    
    def test_audit_log_str(self, test_user):
        """测试审计日志字符串表示"""
        log = AuditLog.objects.create(
            user=test_user,
            username=test_user.username,
            action='update',
            description='更新设备配置',
            success=True
        )
        assert test_user.username in str(log)
    
    def test_log_quick_create(self, test_user):
        """测试快速创建审计日志"""
        log = AuditLog.log(
            user=test_user,
            action='execute',
            description='执行配置下发任务',
            level='info',
            success=True
        )
        assert log.user == test_user
        assert log.action == 'execute'
    
    def test_audit_log_with_changes(self, test_user):
        """测试包含变更详情的审计日志"""
        changes = {
            'field': 'ip_address',
            'old_value': '192.168.1.1',
            'new_value': '192.168.1.2'
        }
        log = AuditLog.objects.create(
            user=test_user,
            username=test_user.username,
            action='update',
            description='修改设备 IP 地址',
            changes=changes,
            success=True
        )
        assert log.changes['field'] == 'ip_address'
        assert log.changes['old_value'] == '192.168.1.1'


@pytest.mark.django_db
class TestLoginHistory:
    """登录历史测试"""
    
    def test_create_login_history(self, test_user):
        """测试创建登录历史"""
        history = LoginHistory.objects.create(
            user=test_user,
            username=test_user.username,
            status='success',
            ip_address='192.168.1.100'
        )
        assert history.user == test_user
        assert history.status == 'success'
    
    def test_login_history_str(self, test_user):
        """测试登录历史字符串表示"""
        history = LoginHistory.objects.create(
            user=test_user,
            username=test_user.username,
            status='success',
            ip_address='192.168.1.100'
        )
        assert test_user.username in str(history)
    
    def test_failed_login_history(self, test_user):
        """测试失败登录历史"""
        history = LoginHistory.objects.create(
            user=test_user,
            username=test_user.username,
            status='failed',
            ip_address='192.168.1.100',
            failure_reason='Invalid password'
        )
        assert history.status == 'failed'
        assert history.failure_reason == 'Invalid password'


@pytest.mark.django_db
class TestOperationStatistics:
    """操作统计测试"""
    
    def test_create_statistics(self):
        """测试创建操作统计"""
        today = timezone.now().date()
        stats = OperationStatistics.objects.create(
            date=today,
            active_users=10,
            new_users=2,
            login_success=50,
            login_failed=5,
            total_operations=100,
            create_operations=20,
            update_operations=30,
            delete_operations=10,
            execute_operations=40
        )
        assert stats.date == today
        assert stats.active_users == 10
        assert stats.total_operations == 100
    
    def test_statistics_str(self):
        """测试统计字符串表示"""
        today = timezone.now().date()
        stats = OperationStatistics.objects.create(
            date=today,
            active_users=5
        )
        assert '统计' in str(stats)
        assert str(today) in str(stats)

