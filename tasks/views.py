"""
任务执行视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Task, TaskResult, Schedule
from .serializers import TaskSerializer, TaskResultSerializer, ScheduleSerializer, TaskCreateSerializer
from .tasks import execute_task


class TaskViewSet(viewsets.ModelViewSet):
    """任务 ViewSet"""
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task_type', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'started_at', 'completed_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """创建任务并执行"""
        task = serializer.save(created_by=self.request.user)
        # 异步执行任务
        celery_task = execute_task.delay(task.id)
        task.celery_task_id = celery_task.id
        task.save(update_fields=['celery_task_id'])
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消任务"""
        task = self.get_object()
        
        if task.status not in ['pending', 'running']:
            return Response(
                {'error': '只能取消等待中或执行中的任务'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.update_status('cancelled')
        
        # 尝试撤销 Celery 任务
        if task.celery_task_id:
            from celery import current_app
            current_app.control.revoke(task.celery_task_id, terminate=True)
        
        return Response({
            'success': True,
            'message': '任务已取消'
        })
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """重试任务"""
        old_task = self.get_object()
        
        # 创建新任务
        new_task = Task.objects.create(
            name=f"{old_task.name} (重试)",
            task_type=old_task.task_type,
            description=old_task.description,
            template=old_task.template,
            template_vars=old_task.template_vars,
            commands=old_task.commands,
            created_by=request.user
        )
        
        # 复制目标设备
        new_task.target_devices.set(old_task.target_devices.all())
        new_task.target_groups.set(old_task.target_groups.all())
        
        # 执行任务
        celery_task = execute_task.delay(new_task.id)
        new_task.celery_task_id = celery_task.id
        new_task.save(update_fields=['celery_task_id'])
        
        return Response({
            'success': True,
            'message': '已创建重试任务',
            'task_id': new_task.id,
            'celery_task_id': celery_task.id
        })
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """获取任务结果"""
        task = self.get_object()
        results = task.results.all()
        serializer = TaskResultSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """任务统计"""
        total = Task.objects.count()
        pending = Task.objects.filter(status='pending').count()
        running = Task.objects.filter(status='running').count()
        success = Task.objects.filter(status='success').count()
        failed = Task.objects.filter(status='failed').count()
        
        by_type = {}
        for choice in Task.TASK_TYPE_CHOICES:
            task_type = choice[0]
            count = Task.objects.filter(task_type=task_type).count()
            by_type[choice[1]] = count
        
        return Response({
            'total': total,
            'pending': pending,
            'running': running,
            'success': success,
            'failed': failed,
            'by_type': by_type,
        })


class TaskResultViewSet(viewsets.ReadOnlyModelViewSet):
    """任务结果 ViewSet（只读）"""
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task', 'device', 'status']
    ordering_fields = ['created_at', 'started_at', 'completed_at']


class ScheduleViewSet(viewsets.ModelViewSet):
    """定时任务 ViewSet"""
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task_type', 'frequency', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'next_run', 'last_run']
    
    def perform_create(self, serializer):
        """创建定时任务"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """激活定时任务"""
        schedule = self.get_object()
        schedule.is_active = True
        schedule.save(update_fields=['is_active'])
        return Response({'success': True, 'message': '定时任务已激活'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """停用定时任务"""
        schedule = self.get_object()
        schedule.is_active = False
        schedule.save(update_fields=['is_active'])
        return Response({'success': True, 'message': '定时任务已停用'})
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """立即执行定时任务"""
        schedule = self.get_object()
        
        # 创建任务
        task = Task.objects.create(
            name=f"{schedule.name} (手动执行)",
            task_type=schedule.task_type,
            description=schedule.description,
            template=schedule.template,
            template_vars=schedule.template_vars,
            commands=schedule.commands,
            created_by=request.user
        )
        
        # 复制目标设备
        task.target_devices.set(schedule.target_devices.all())
        task.target_groups.set(schedule.target_groups.all())
        
        # 执行任务
        celery_task = execute_task.delay(task.id)
        task.celery_task_id = celery_task.id
        task.save(update_fields=['celery_task_id'])
        
        return Response({
            'success': True,
            'message': '任务已提交执行',
            'task_id': task.id,
            'celery_task_id': celery_task.id
        })

