"""
审计中间件
"""
from .models import AuditLog, LoginHistory
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver


class AuditMiddleware(MiddlewareMixin):
    """审计中间件 - 记录所有请求"""
    
    def process_request(self, request):
        """处理请求"""
        # 保存 IP 地址到 request
        request.audit_ip = self.get_client_ip(request)
        request.audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    def get_client_ip(self, request):
        """获取客户端 IP 地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# 登录信号处理
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """记录用户登录"""
    ip_address = getattr(request, 'audit_ip', None)
    user_agent = getattr(request, 'audit_user_agent', '')
    
    # 记录登录历史
    LoginHistory.objects.create(
        user=user,
        username=user.username,
        status='success',
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # 记录审计日志
    AuditLog.objects.create(
        user=user,
        username=user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        action='login',
        description=f'用户 {user.username} 登录系统',
        level='info',
        success=True
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """记录用户登出"""
    if user:
        ip_address = getattr(request, 'audit_ip', None)
        user_agent = getattr(request, 'audit_user_agent', '')
        
        AuditLog.objects.create(
            user=user,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            action='logout',
            description=f'用户 {user.username} 登出系统',
            level='info',
            success=True
        )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """记录登录失败"""
    username = credentials.get('username', 'Unknown')
    ip_address = getattr(request, 'audit_ip', None)
    user_agent = getattr(request, 'audit_user_agent', '')
    
    # 记录登录历史
    LoginHistory.objects.create(
        username=username,
        status='failed',
        ip_address=ip_address,
        user_agent=user_agent,
        failure_reason='认证失败'
    )
    
    # 记录审计日志
    AuditLog.objects.create(
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        action='login',
        description=f'用户 {username} 登录失败',
        level='warning',
        success=False,
        error_message='认证失败'
    )


def log_audit(user, action, description, **kwargs):
    """工具函数 - 快速记录审计日志"""
    return AuditLog.log(user, action, description, **kwargs)

