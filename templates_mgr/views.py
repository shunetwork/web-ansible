"""
模板管理视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ConfigTemplate, TemplateVersion, TemplateVariable
from .serializers import (
    ConfigTemplateSerializer, TemplateVersionSerializer, 
    TemplateVariableSerializer, TemplateRenderSerializer
)


class ConfigTemplateViewSet(viewsets.ModelViewSet):
    """配置模板 ViewSet"""
    queryset = ConfigTemplate.objects.all()
    serializer_class = ConfigTemplateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['name', 'version', 'created_at', 'updated_at']
    
    @action(detail=True, methods=['post'])
    def render(self, request, pk=None):
        """渲染模板"""
        template = self.get_object()
        serializer = TemplateRenderSerializer(data=request.data)
        
        if serializer.is_valid():
            variables = serializer.validated_data.get('variables', {})
            try:
                rendered = template.render(variables)
                return Response({
                    'success': True,
                    'template': template.name,
                    'variables': variables,
                    'rendered': rendered
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """创建版本快照"""
        template = self.get_object()
        change_note = request.data.get('change_note', '手动创建版本快照')
        
        version = TemplateVersion.objects.create(
            template=template,
            version=template.version,
            content=template.content,
            variables=template.variables,
            change_note=change_note,
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'message': f'已创建版本 {version.version}',
            'version': TemplateVersionSerializer(version).data
        })
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """获取模板版本历史"""
        template = self.get_object()
        versions = template.versions.all()
        serializer = TemplateVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore_version(self, request, pk=None):
        """恢复到指定版本"""
        template = self.get_object()
        version_id = request.data.get('version_id')
        
        if not version_id:
            return Response(
                {'error': '请提供版本 ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            version = TemplateVersion.objects.get(id=version_id, template=template)
            
            # 保存当前版本
            TemplateVersion.objects.create(
                template=template,
                version=template.version,
                content=template.content,
                variables=template.variables,
                change_note=f'恢复版本前的备份',
                created_by=request.user
            )
            
            # 恢复到指定版本
            template.content = version.content
            template.variables = version.variables
            template.increment_version()
            
            return Response({
                'success': True,
                'message': f'已恢复到版本 {version.version}',
                'current_version': template.version
            })
            
        except TemplateVersion.DoesNotExist:
            return Response(
                {'error': '版本不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取所有分类"""
        categories = [
            {'value': choice[0], 'label': choice[1]} 
            for choice in ConfigTemplate.CATEGORY_CHOICES
        ]
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def search_by_tags(self, request):
        """按标签搜索"""
        tags = request.query_params.get('tags', '').split(',')
        templates = ConfigTemplate.objects.filter(is_active=True)
        
        for tag in tags:
            if tag.strip():
                templates = templates.filter(tags__icontains=tag.strip())
        
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


class TemplateVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """模板版本 ViewSet（只读）"""
    queryset = TemplateVersion.objects.all()
    serializer_class = TemplateVersionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['template']
    ordering_fields = ['version', 'created_at']


class TemplateVariableViewSet(viewsets.ModelViewSet):
    """模板变量 ViewSet"""
    queryset = TemplateVariable.objects.all()
    serializer_class = TemplateVariableSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['template', 'variable_type', 'required']
    ordering_fields = ['order', 'name']

