"""
配置备份序列化器
"""
from rest_framework import serializers
from .models import ConfigBackup, ConfigDiff, RestoreHistory


class ConfigBackupSerializer(serializers.ModelSerializer):
    """配置备份序列化器"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_ip = serializers.CharField(source='device.ip_address', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    file_size_display = serializers.CharField(source='get_file_size_display', read_only=True)
    has_changes = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ConfigBackup
        fields = [
            'id', 'device', 'device_name', 'device_ip',
            'config_content', 'file_path', 'file_size', 'file_size_display',
            'status', 'status_display', 'error_message',
            'backup_type', 'description', 'has_changes',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class ConfigDiffSerializer(serializers.ModelSerializer):
    """配置差异序列化器"""
    device_name = serializers.CharField(source='backup_old.device.name', read_only=True)
    old_backup_time = serializers.DateTimeField(source='backup_old.created_at', read_only=True)
    new_backup_time = serializers.DateTimeField(source='backup_new.created_at', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ConfigDiff
        fields = [
            'id', 'backup_old', 'backup_new', 'device_name',
            'old_backup_time', 'new_backup_time',
            'diff_content', 'lines_added', 'lines_removed', 'lines_changed',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class RestoreHistorySerializer(serializers.ModelSerializer):
    """恢复历史序列化器"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    backup_time = serializers.DateTimeField(source='backup.created_at', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = RestoreHistory
        fields = [
            'id', 'device', 'device_name', 'backup', 'backup_time',
            'status', 'status_display', 'output', 'error_message',
            'created_by', 'created_by_name',
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'started_at', 'completed_at']

