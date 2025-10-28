"""
审计日志视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import AuditLog, LoginHistory, OperationStatistics
from .serializers import AuditLogSerializer, LoginHistorySerializer, OperationStatisticsSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """审计日志 ViewSet（只读）"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['user', 'action', 'level', 'success']
    search_fields = ['username', 'description', 'object_repr', 'ip_address']
    ordering_fields = ['created_at']
    
    @action(detail=False, methods=['get'])
    def my_logs(self, request):
        """获取当前用户的操作日志"""
        logs = AuditLog.objects.filter(user=request.user)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """审计日志统计"""
        # 时间范围
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        logs = AuditLog.objects.filter(created_at__gte=start_date)
        
        # 按操作类型统计
        by_action = logs.values('action').annotate(count=Count('id'))
        
        # 按用户统计
        by_user = logs.values('user__username').annotate(count=Count('id')).order_by('-count')[:10]
        
        # 按日期统计
        by_date = logs.extra(
            select={'date': 'date(created_at)'}
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        # 成功/失败统计
        success_count = logs.filter(success=True).count()
        failed_count = logs.filter(success=False).count()
        
        return Response({
            'total': logs.count(),
            'success': success_count,
            'failed': failed_count,
            'by_action': list(by_action),
            'by_user': list(by_user),
            'by_date': list(by_date),
        })


class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """登录历史 ViewSet（只读）"""
    queryset = LoginHistory.objects.all()
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['user', 'status']
    search_fields = ['username', 'ip_address']
    ordering_fields = ['created_at']
    
    @action(detail=False, methods=['get'])
    def my_history(self, request):
        """获取当前用户的登录历史"""
        history = LoginHistory.objects.filter(user=request.user)
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """登录统计"""
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        history = LoginHistory.objects.filter(created_at__gte=start_date)
        
        success_count = history.filter(status='success').count()
        failed_count = history.filter(status='failed').count()
        
        # 按日期统计
        by_date = history.extra(
            select={'date': 'date(created_at)'}
        ).values('date').annotate(
            success=Count('id', filter=Q(status='success')),
            failed=Count('id', filter=Q(status='failed'))
        ).order_by('date')
        
        # 失败原因统计
        failed_reasons = history.filter(status='failed').values('failure_reason').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total': history.count(),
            'success': success_count,
            'failed': failed_count,
            'by_date': list(by_date),
            'failed_reasons': list(failed_reasons),
        })


class OperationStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """操作统计 ViewSet（只读）"""
    queryset = OperationStatistics.objects.all()
    serializer_class = OperationStatisticsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['date']
    ordering_fields = ['date']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """统计概览"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        stats = OperationStatistics.objects.filter(date__gte=start_date)
        
        # 汇总统计
        total_users = sum(s.active_users for s in stats)
        total_operations = sum(s.total_operations for s in stats)
        total_tasks = sum(s.tasks_created for s in stats)
        total_backups = sum(s.backups_created for s in stats)
        
        # 趋势数据
        trend_data = [{
            'date': s.date,
            'active_users': s.active_users,
            'operations': s.total_operations,
            'tasks': s.tasks_created,
            'backups': s.backups_created,
        } for s in stats]
        
        return Response({
            'period_days': days,
            'total_users': total_users,
            'total_operations': total_operations,
            'total_tasks': total_tasks,
            'total_backups': total_backups,
            'trend': trend_data,
        })

