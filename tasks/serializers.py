"""
任务执行序列化器
"""
from rest_framework import serializers
from .models import Task, TaskResult, Schedule


class TaskResultSerializer(serializers.ModelSerializer):
    """任务结果序列化器"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_ip = serializers.CharField(source='device.ip_address', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration = serializers.FloatField(read_only=True)
    
    class Meta:
        model = TaskResult
        fields = [
            'id', 'task', 'device', 'device_name', 'device_ip',
            'status', 'status_display', 'output', 'error',
            'started_at', 'completed_at', 'duration', 'created_at'
        ]
        read_only_fields = ['created_at']


class TaskSerializer(serializers.ModelSerializer):
    """任务序列化器"""
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    duration = serializers.FloatField(read_only=True)
    target_device_names = serializers.SerializerMethodField()
    target_group_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'name', 'task_type', 'task_type_display', 'description',
            'target_devices', 'target_device_names', 'target_groups', 'target_group_names',
            'template', 'template_vars', 'commands',
            'status', 'status_display', 'progress', 'celery_task_id',
            'success_count', 'failed_count', 'total_count',
            'created_by', 'created_by_name', 'created_at', 'started_at', 'completed_at', 'duration'
        ]
        read_only_fields = [
            'status', 'progress', 'celery_task_id',
            'success_count', 'failed_count', 'total_count',
            'created_at', 'started_at', 'completed_at'
        ]
    
    def get_target_device_names(self, obj):
        return [{'id': d.id, 'name': d.name, 'ip': d.ip_address} for d in obj.target_devices.all()]
    
    def get_target_group_names(self, obj):
        return [{'id': g.id, 'name': g.name} for g in obj.target_groups.all()]


class TaskCreateSerializer(serializers.ModelSerializer):
    """任务创建序列化器"""
    
    class Meta:
        model = Task
        fields = [
            'name', 'task_type', 'description',
            'target_devices', 'target_groups',
            'template', 'template_vars', 'commands'
        ]
    
    def validate(self, data):
        """验证数据"""
        # 检查目标设备
        if not data.get('target_devices') and not data.get('target_groups'):
            raise serializers.ValidationError('必须指定目标设备或设备组')
        
        # 根据任务类型验证
        task_type = data.get('task_type')
        
        if task_type == 'template':
            if not data.get('template'):
                raise serializers.ValidationError('模板下发任务必须指定模板')
        elif task_type == 'command':
            if not data.get('commands'):
                raise serializers.ValidationError('命令执行任务必须提供命令列表')
        
        return data


class ScheduleSerializer(serializers.ModelSerializer):
    """定时任务序列化器"""
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    target_device_names = serializers.SerializerMethodField()
    target_group_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'name', 'description', 'is_active',
            'task_type', 'task_type_display',
            'target_devices', 'target_device_names', 'target_groups', 'target_group_names',
            'template', 'template_vars', 'commands',
            'frequency', 'frequency_display', 'cron_expression',
            'next_run', 'last_run',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['next_run', 'last_run', 'created_at', 'updated_at']
    
    def get_target_device_names(self, obj):
        return [{'id': d.id, 'name': d.name} for d in obj.target_devices.all()]
    
    def get_target_group_names(self, obj):
        return [{'id': g.id, 'name': g.name} for g in obj.target_groups.all()]

