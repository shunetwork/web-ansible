"""
设备管理视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Device, DeviceGroup, DeviceCredential
from .serializers import DeviceSerializer, DeviceGroupSerializer, DeviceCredentialSerializer
from .tasks import test_device_connection, import_devices_from_csv
import csv
import io


class DeviceViewSet(viewsets.ModelViewSet):
    """设备管理 ViewSet"""
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['device_type', 'status', 'is_active']
    search_fields = ['name', 'hostname', 'ip_address']
    ordering_fields = ['name', 'ip_address', 'created_at']
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """测试设备连接"""
        device = self.get_object()
        task = test_device_connection.delay(device.id)
        return Response({
            'message': '连接测试任务已提交',
            'task_id': task.id,
            'device': device.name
        })
    
    @action(detail=False, methods=['post'])
    def bulk_test(self, request):
        """批量测试连接"""
        device_ids = request.data.get('device_ids', [])
        if not device_ids:
            return Response(
                {'error': '请提供设备 ID 列表'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = []
        for device_id in device_ids:
            task = test_device_connection.delay(device_id)
            tasks.append({'device_id': device_id, 'task_id': task.id})
        
        return Response({
            'message': f'已提交 {len(tasks)} 个连接测试任务',
            'tasks': tasks
        })
    
    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """导入 CSV 文件"""
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response(
                {'error': '请提供 CSV 文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 读取 CSV 文件
        try:
            decoded_file = csv_file.read().decode('utf-8')
            task = import_devices_from_csv.delay(decoded_file, request.user.id)
            return Response({
                'message': 'CSV 导入任务已提交',
                'task_id': task.id
            })
        except Exception as e:
            return Response(
                {'error': f'CSV 文件解析失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """导出为 CSV 文件"""
        devices = self.filter_queryset(self.get_queryset())
        
        # 创建 CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'name', 'hostname', 'ip_address', 'device_type', 'model',
            'ssh_port', 'username', 'password', 'location', 'description'
        ])
        
        for device in devices:
            writer.writerow([
                device.name, device.hostname, device.ip_address, device.device_type,
                device.model, device.ssh_port, device.username, device.password,
                device.location, device.description
            ])
        
        response = Response(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="devices.csv"'
        return response
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """设备统计信息"""
        total = Device.objects.count()
        online = Device.objects.filter(status='online').count()
        offline = Device.objects.filter(status='offline').count()
        maintenance = Device.objects.filter(status='maintenance').count()
        
        by_type = {}
        for choice in Device.DEVICE_TYPE_CHOICES:
            device_type = choice[0]
            count = Device.objects.filter(device_type=device_type).count()
            by_type[choice[1]] = count
        
        return Response({
            'total': total,
            'online': online,
            'offline': offline,
            'maintenance': maintenance,
            'by_type': by_type,
        })


class DeviceGroupViewSet(viewsets.ModelViewSet):
    """设备组管理 ViewSet"""
    queryset = DeviceGroup.objects.all()
    serializer_class = DeviceGroupSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def devices(self, request, pk=None):
        """获取组内设备"""
        group = self.get_object()
        devices = group.devices.all()
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)


class DeviceCredentialViewSet(viewsets.ModelViewSet):
    """设备凭据管理 ViewSet"""
    queryset = DeviceCredential.objects.all()
    serializer_class = DeviceCredentialSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'username']

