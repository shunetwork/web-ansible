"""
配置备份模块测试
"""
import pytest
from backups.models import ConfigBackup, ConfigDiff, RestoreHistory


@pytest.mark.django_db
class TestConfigBackup:
    """配置备份测试"""
    
    def test_create_backup(self, config_backup):
        """测试创建备份"""
        assert config_backup.device.name == 'Test Switch'
        assert config_backup.status == 'success'
        assert config_backup.backup_type == 'manual'
    
    def test_backup_str(self, config_backup):
        """测试备份字符串表示"""
        assert 'Test Switch' in str(config_backup)
    
    def test_get_file_size_display(self, config_backup):
        """测试文件大小显示"""
        size_display = config_backup.get_file_size_display()
        assert 'KB' in size_display or 'B' in size_display
    
    def test_compare_backups(self, test_device, test_user):
        """测试备份对比"""
        backup1 = ConfigBackup.objects.create(
            device=test_device,
            config_content='hostname test-sw-01\ninterface GigabitEthernet0/1',
            file_path='/tmp/backup1.cfg',
            file_size=100,
            status='success',
            created_by=test_user
        )
        
        backup2 = ConfigBackup.objects.create(
            device=test_device,
            config_content='hostname test-sw-01\ninterface GigabitEthernet0/1\n description Changed',
            file_path='/tmp/backup2.cfg',
            file_size=120,
            status='success',
            created_by=test_user
        )
        
        diff = backup2.compare_with(backup1)
        assert diff is not None
        assert 'Changed' in diff
    
    def test_get_previous_backup(self, test_device, test_user):
        """测试获取上一个备份"""
        backup1 = ConfigBackup.objects.create(
            device=test_device,
            config_content='config 1',
            file_path='/tmp/backup1.cfg',
            file_size=100,
            status='success',
            created_by=test_user
        )
        
        backup2 = ConfigBackup.objects.create(
            device=test_device,
            config_content='config 2',
            file_path='/tmp/backup2.cfg',
            file_size=100,
            status='success',
            created_by=test_user
        )
        
        previous = backup2.get_previous_backup()
        assert previous == backup1
    
    def test_has_changes(self, test_device, test_user):
        """测试是否有变化"""
        backup1 = ConfigBackup.objects.create(
            device=test_device,
            config_content='config content',
            file_path='/tmp/backup1.cfg',
            file_size=100,
            status='success',
            created_by=test_user
        )
        
        # 相同内容
        backup2 = ConfigBackup.objects.create(
            device=test_device,
            config_content='config content',
            file_path='/tmp/backup2.cfg',
            file_size=100,
            status='success',
            created_by=test_user
        )
        assert not backup2.has_changes()
        
        # 不同内容
        backup3 = ConfigBackup.objects.create(
            device=test_device,
            config_content='different config',
            file_path='/tmp/backup3.cfg',
            file_size=100,
            status='success',
            created_by=test_user
        )
        assert backup3.has_changes()


@pytest.mark.django_db
class TestConfigDiff:
    """配置差异测试"""
    
    def test_create_diff(self, test_device, test_user):
        """测试创建差异记录"""
        backup1 = ConfigBackup.objects.create(
            device=test_device,
            config_content='config 1',
            file_path='/tmp/backup1.cfg',
            file_size=100,
            status='success',
            created_by=test_user
        )
        
        backup2 = ConfigBackup.objects.create(
            device=test_device,
            config_content='config 2',
            file_path='/tmp/backup2.cfg',
            file_size=100,
            status='success',
            created_by=test_user
        )
        
        diff = ConfigDiff.objects.create(
            backup_old=backup1,
            backup_new=backup2,
            diff_content='--- backup1\n+++ backup2',
            lines_added=1,
            lines_removed=1,
            created_by=test_user
        )
        
        assert diff.backup_old == backup1
        assert diff.backup_new == backup2
        assert diff.lines_added == 1
        assert diff.lines_removed == 1


@pytest.mark.django_db
class TestRestoreHistory:
    """恢复历史测试"""
    
    def test_create_restore_history(self, test_device, config_backup, test_user):
        """测试创建恢复历史"""
        restore = RestoreHistory.objects.create(
            device=test_device,
            backup=config_backup,
            status='success',
            output='Configuration restored successfully',
            created_by=test_user
        )
        
        assert restore.device == test_device
        assert restore.backup == config_backup
        assert restore.status == 'success'
    
    def test_restore_str(self, test_device, config_backup, test_user):
        """测试恢复历史字符串表示"""
        restore = RestoreHistory.objects.create(
            device=test_device,
            backup=config_backup,
            status='success',
            created_by=test_user
        )
        assert 'Test Switch' in str(restore)
        assert '恢复' in str(restore)

