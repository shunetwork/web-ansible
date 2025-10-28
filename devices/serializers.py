"""
设备管理序列化器
"""
from rest_framework import serializers
from .models import Device, DeviceGroup, DeviceCredential


class DeviceGroupSerializer(serializers.ModelSerializer):
    """设备组序列化器"""
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DeviceGroup
        fields = ['id', 'name', 'description', 'device_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_device_count(self, obj):
        return obj.devices.count()


class DeviceSerializer(serializers.ModelSerializer):
    """设备序列化器"""
    groups_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    
    class Meta:
        model = Device
        fields = [
            'id', 'name', 'hostname', 'ip_address', 'device_type', 'device_type_display',
            'model', 'serial_number', 'ssh_port', 'username', 'password', 'enable_password',
            'os_version', 'groups', 'groups_display', 'status', 'status_display', 'is_active',
            'description', 'location', 'last_check', 'last_check_result',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['last_check', 'last_check_result', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'enable_password': {'write_only': True}
        }
    
    def get_groups_display(self, obj):
        return [{'id': g.id, 'name': g.name} for g in obj.groups.all()]


class DeviceCredentialSerializer(serializers.ModelSerializer):
    """设备凭据序列化器"""
    
    class Meta:
        model = DeviceCredential
        fields = ['id', 'name', 'username', 'password', 'enable_password', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'enable_password': {'write_only': True}
        }

