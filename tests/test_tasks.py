"""
任务执行模块测试
"""
import pytest
from django.utils import timezone
from tasks.models import Task, TaskResult, Schedule


@pytest.mark.django_db
class TestTask:
    """任务测试"""
    
    def test_create_task(self, test_task):
        """测试创建任务"""
        assert test_task.name == 'Test Task'
        assert test_task.task_type == 'template'
        assert test_task.status == 'pending'
        assert test_task.progress == 0
    
    def test_task_str(self, test_task):
        """测试任务字符串表示"""
        assert '模板下发' in str(test_task)
    
    def test_get_all_target_devices(self, test_task, test_device):
        """测试获取所有目标设备"""
        devices = test_task.get_all_target_devices()
        assert len(devices) == 1
        assert test_device in devices
    
    def test_update_task_status(self, test_task):
        """测试更新任务状态"""
        test_task.update_status('running', progress=50)
        test_task.refresh_from_db()
        assert test_task.status == 'running'
        assert test_task.progress == 50
        assert test_task.started_at is not None
    
    def test_update_task_counts(self, test_task):
        """测试更新任务统计"""
        test_task.update_counts(success=5, failed=2)
        test_task.refresh_from_db()
        assert test_task.success_count == 5
        assert test_task.failed_count == 2
        assert test_task.total_count == 7
    
    def test_task_duration(self, test_task):
        """测试任务时长"""
        # 未开始
        assert test_task.duration == 0
        
        # 已开始
        test_task.started_at = timezone.now()
        test_task.save()
        assert test_task.duration > 0


@pytest.mark.django_db
class TestTaskResult:
    """任务结果测试"""
    
    def test_create_task_result(self, test_task, test_device):
        """测试创建任务结果"""
        result = TaskResult.objects.create(
            task=test_task,
            device=test_device,
            status='success',
            output='Configuration applied successfully'
        )
        assert result.task == test_task
        assert result.device == test_device
        assert result.status == 'success'
    
    def test_task_result_str(self, test_task, test_device):
        """测试任务结果字符串表示"""
        result = TaskResult.objects.create(
            task=test_task,
            device=test_device,
            status='success'
        )
        assert 'Test Task' in str(result)
        assert 'Test Switch' in str(result)


@pytest.mark.django_db
class TestSchedule:
    """定时任务测试"""
    
    def test_create_schedule(self, test_user, test_device, config_template):
        """测试创建定时任务"""
        schedule = Schedule.objects.create(
            name='Daily Backup',
            description='Daily configuration backup',
            is_active=True,
            task_type='backup',
            frequency='daily',
            created_by=test_user
        )
        schedule.target_devices.add(test_device)
        
        assert schedule.name == 'Daily Backup'
        assert schedule.task_type == 'backup'
        assert schedule.frequency == 'daily'
        assert schedule.is_active is True
    
    def test_schedule_str(self, test_user):
        """测试定时任务字符串表示"""
        schedule = Schedule.objects.create(
            name='Hourly Check',
            task_type='health_check',
            frequency='hourly',
            created_by=test_user
        )
        assert 'Hourly Check' in str(schedule)
        assert '每小时' in str(schedule)

