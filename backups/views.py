"""
配置备份视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ConfigBackup, ConfigDiff, RestoreHistory
from .serializers import ConfigBackupSerializer, ConfigDiffSerializer, RestoreHistorySerializer
from .tasks import backup_device_config, restore_device_config, backup_all_devices
from devices.models import Device


class ConfigBackupViewSet(viewsets.ReadOnlyModelViewSet):
    """配置备份 ViewSet（只读）"""
    queryset = ConfigBackup.objects.all()
    serializer_class = ConfigBackupSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['device', 'status', 'backup_type']
    search_fields = ['device__name', 'description']
    ordering_fields = ['created_at', 'file_size']
    
    @action(detail=False, methods=['post'])
    def backup_device(self, request):
        """备份指定设备"""
        device_id = request.data.get('device_id')
        if not device_id:
            return Response(
                {'error': '请提供设备 ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            device = Device.objects.get(id=device_id)
            task = backup_device_config.delay(device_id, request.user.id)
            return Response({
                'success': True,
                'message': f'已提交 {device.name} 的备份任务',
                'task_id': task.id
            })
        except Device.DoesNotExist:
            return Response(
                {'error': '设备不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def backup_all(self, request):
        """备份所有设备"""
        task = backup_all_devices.delay(request.user.id)
        return Response({
            'success': True,
            'message': '已提交批量备份任务',
            'task_id': task.id
        })
    
    @action(detail=True, methods=['get'])
    def compare(self, request, pk=None):
        """对比备份"""
        backup = self.get_object()
        previous = backup.get_previous_backup()
        
        if not previous:
            return Response({
                'success': False,
                'message': '没有可对比的历史备份'
            })
        
        diff_content = backup.compare_with(previous)
        
        return Response({
            'success': True,
            'backup': ConfigBackupSerializer(backup).data,
            'previous': ConfigBackupSerializer(previous).data,
            'diff': diff_content
        })
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """恢复备份"""
        backup = self.get_object()
        
        if backup.status != 'success':
            return Response(
                {'error': '只能恢复成功的备份'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task = restore_device_config.delay(backup.id, request.user.id)
        
        return Response({
            'success': True,
            'message': f'已提交 {backup.device.name} 的配置恢复任务',
            'task_id': task.id
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """备份统计"""
        total = ConfigBackup.objects.count()
        success = ConfigBackup.objects.filter(status='success').count()
        failed = ConfigBackup.objects.filter(status='failed').count()
        
        # 按设备统计
        devices = Device.objects.all()
        by_device = []
        for device in devices:
            backup_count = device.backups.filter(status='success').count()
            latest = device.backups.filter(status='success').first()
            by_device.append({
                'device_id': device.id,
                'device_name': device.name,
                'backup_count': backup_count,
                'latest_backup': ConfigBackupSerializer(latest).data if latest else None
            })
        
        return Response({
            'total': total,
            'success': success,
            'failed': failed,
            'by_device': by_device,
        })


class ConfigDiffViewSet(viewsets.ReadOnlyModelViewSet):
    """配置差异 ViewSet（只读）"""
    queryset = ConfigDiff.objects.all()
    serializer_class = ConfigDiffSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['backup_old__device', 'backup_new__device']
    ordering_fields = ['created_at']


class RestoreHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """恢复历史 ViewSet（只读）"""
    queryset = RestoreHistory.objects.all()
    serializer_class = RestoreHistorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['device', 'status']
    ordering_fields = ['created_at', 'started_at', 'completed_at']

