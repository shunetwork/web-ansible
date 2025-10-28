"""
审计日志序列化器
"""
from rest_framework import serializers
from .models import AuditLog, LoginHistory, OperationStatistics


class AuditLogSerializer(serializers.ModelSerializer):
    """审计日志序列化器"""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'username', 'ip_address', 'user_agent',
            'action', 'action_display', 'description', 'level', 'level_display',
            'content_type', 'object_id', 'object_repr',
            'changes', 'extra_data', 'success', 'error_message',
            'created_at'
        ]
        read_only_fields = ['created_at']


class LoginHistorySerializer(serializers.ModelSerializer):
    """登录历史序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LoginHistory
        fields = [
            'id', 'user', 'username', 'status', 'status_display',
            'ip_address', 'user_agent', 'failure_reason',
            'created_at'
        ]
        read_only_fields = ['created_at']


class OperationStatisticsSerializer(serializers.ModelSerializer):
    """操作统计序列化器"""
    
    class Meta:
        model = OperationStatistics
        fields = [
            'id', 'date', 'active_users', 'new_users',
            'login_success', 'login_failed',
            'total_operations', 'create_operations', 'update_operations',
            'delete_operations', 'execute_operations',
            'tasks_created', 'tasks_success', 'tasks_failed',
            'backups_created', 'backups_success', 'backups_failed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

