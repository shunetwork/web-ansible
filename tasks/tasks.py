"""
任务执行 Celery 任务
"""
try:
    from celery import shared_task
except ImportError:
    from web_ansible.celery_stub import shared_task

from django.utils import timezone
from .models import Task, TaskResult
from devices.models import Device
import subprocess
import json
import os
from django.conf import settings


@shared_task(bind=True)
def execute_task(self, task_id):
    """执行任务"""
    try:
        task = Task.objects.get(id=task_id)
        task.update_status('running', progress=0)
        
        # 获取所有目标设备
        devices = task.get_all_target_devices()
        task.total_count = len(devices)
        task.save(update_fields=['total_count'])
        
        # 为每个设备创建结果记录
        for device in devices:
            TaskResult.objects.get_or_create(task=task, device=device)
        
        # 根据任务类型执行
        if task.task_type == 'command':
            return execute_command_task(task, devices)
        elif task.task_type == 'template':
            return execute_template_task(task, devices)
        elif task.task_type == 'backup':
            return execute_backup_task(task, devices)
        elif task.task_type == 'health_check':
            return execute_health_check_task(task, devices)
        else:
            task.update_status('failed')
            return {'success': False, 'error': '未知的任务类型'}
            
    except Task.DoesNotExist:
        return {'success': False, 'error': '任务不存在'}
    except Exception as e:
        if 'task' in locals():
            task.update_status('failed')
        return {'success': False, 'error': str(e)}


def execute_command_task(task, devices):
    """执行命令任务"""
    commands = task.commands.strip().split('\n')
    success_count = 0
    failed_count = 0
    
    for device in devices:
        result = TaskResult.objects.get(task=task, device=device)
        result.status = 'running'
        result.started_at = timezone.now()
        result.save()
        
        try:
            # 使用 Ansible 执行命令
            output = run_ansible_command(device, commands)
            result.output = output
            result.status = 'success'
            success_count += 1
        except Exception as e:
            result.error = str(e)
            result.status = 'failed'
            failed_count += 1
        
        result.completed_at = timezone.now()
        result.save()
        
        # 更新任务进度
        task.update_counts(success_count, failed_count)
    
    # 更新任务状态
    if failed_count == 0:
        task.update_status('success', progress=100)
    elif success_count == 0:
        task.update_status('failed', progress=100)
    else:
        task.update_status('partial', progress=100)
    
    return {
        'success': True,
        'task_id': task.id,
        'success_count': success_count,
        'failed_count': failed_count
    }


def execute_template_task(task, devices):
    """执行模板任务"""
    if not task.template:
        task.update_status('failed')
        return {'success': False, 'error': '未指定模板'}
    
    success_count = 0
    failed_count = 0
    
    # 渲染模板
    try:
        config = task.template.render(task.template_vars)
    except Exception as e:
        task.update_status('failed')
        return {'success': False, 'error': f'模板渲染失败: {str(e)}'}
    
    for device in devices:
        result = TaskResult.objects.get(task=task, device=device)
        result.status = 'running'
        result.started_at = timezone.now()
        result.save()
        
        try:
            # 使用 Ansible 下发配置
            output = run_ansible_config(device, config)
            result.output = output
            result.status = 'success'
            success_count += 1
        except Exception as e:
            result.error = str(e)
            result.status = 'failed'
            failed_count += 1
        
        result.completed_at = timezone.now()
        result.save()
        
        # 更新任务进度
        task.update_counts(success_count, failed_count)
    
    # 更新任务状态
    if failed_count == 0:
        task.update_status('success', progress=100)
    elif success_count == 0:
        task.update_status('failed', progress=100)
    else:
        task.update_status('partial', progress=100)
    
    return {
        'success': True,
        'task_id': task.id,
        'success_count': success_count,
        'failed_count': failed_count
    }


def execute_backup_task(task, devices):
    """执行备份任务"""
    from backups.tasks import backup_device_config
    
    success_count = 0
    failed_count = 0
    
    for device in devices:
        result = TaskResult.objects.get(task=task, device=device)
        result.status = 'running'
        result.started_at = timezone.now()
        result.save()
        
        try:
            # 调用备份任务
            backup_result = backup_device_config(device.id)
            if backup_result.get('success'):
                result.output = f"备份成功: {backup_result.get('file_path')}"
                result.status = 'success'
                success_count += 1
            else:
                result.error = backup_result.get('error', '备份失败')
                result.status = 'failed'
                failed_count += 1
        except Exception as e:
            result.error = str(e)
            result.status = 'failed'
            failed_count += 1
        
        result.completed_at = timezone.now()
        result.save()
        
        # 更新任务进度
        task.update_counts(success_count, failed_count)
    
    # 更新任务状态
    if failed_count == 0:
        task.update_status('success', progress=100)
    elif success_count == 0:
        task.update_status('failed', progress=100)
    else:
        task.update_status('partial', progress=100)
    
    return {
        'success': True,
        'task_id': task.id,
        'success_count': success_count,
        'failed_count': failed_count
    }


def execute_health_check_task(task, devices):
    """执行健康检查任务"""
    from devices.tasks import test_device_connection
    
    success_count = 0
    failed_count = 0
    
    for device in devices:
        result = TaskResult.objects.get(task=task, device=device)
        result.status = 'running'
        result.started_at = timezone.now()
        result.save()
        
        try:
            # 调用健康检查
            check_result = test_device_connection(device.id)
            if check_result.get('success'):
                result.output = check_result.get('message', '连接正常')
                result.status = 'success'
                success_count += 1
            else:
                result.error = check_result.get('error', '连接失败')
                result.status = 'failed'
                failed_count += 1
        except Exception as e:
            result.error = str(e)
            result.status = 'failed'
            failed_count += 1
        
        result.completed_at = timezone.now()
        result.save()
        
        # 更新任务进度
        task.update_counts(success_count, failed_count)
    
    # 更新任务状态
    if failed_count == 0:
        task.update_status('success', progress=100)
    elif success_count == 0:
        task.update_status('failed', progress=100)
    else:
        task.update_status('partial', progress=100)
    
    return {
        'success': True,
        'task_id': task.id,
        'success_count': success_count,
        'failed_count': failed_count
    }


def run_ansible_command(device, commands):
    """使用 Ansible 执行命令"""
    # 创建临时 inventory
    inventory = {
        'all': {
            'hosts': {
                device.hostname: device.get_ansible_vars()
            }
        }
    }
    
    # 创建 playbook
    playbook = [{
        'name': 'Execute commands',
        'hosts': 'all',
        'gather_facts': False,
        'tasks': [{
            'name': 'Run commands',
            'ios_command': {
                'commands': commands
            },
            'register': 'output'
        }, {
            'name': 'Display output',
            'debug': {
                'var': 'output.stdout_lines'
            }
        }]
    }]
    
    # 写入临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as inv_file:
        json.dump(inventory, inv_file)
        inv_path = inv_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as pb_file:
        import yaml
        yaml.dump(playbook, pb_file)
        pb_path = pb_file.name
    
    try:
        # 执行 ansible-playbook
        result = subprocess.run(
            ['ansible-playbook', '-i', inv_path, pb_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return result.stdout
    finally:
        # 清理临时文件
        os.unlink(inv_path)
        os.unlink(pb_path)


def run_ansible_config(device, config):
    """使用 Ansible 下发配置"""
    # 创建临时 inventory
    inventory = {
        'all': {
            'hosts': {
                device.hostname: device.get_ansible_vars()
            }
        }
    }
    
    # 创建 playbook
    playbook = [{
        'name': 'Deploy configuration',
        'hosts': 'all',
        'gather_facts': False,
        'tasks': [{
            'name': 'Apply configuration',
            'ios_config': {
                'lines': config.split('\n'),
                'save_when': 'changed'
            },
            'register': 'output'
        }]
    }]
    
    # 写入临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as inv_file:
        json.dump(inventory, inv_file)
        inv_path = inv_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as pb_file:
        import yaml
        yaml.dump(playbook, pb_file)
        pb_path = pb_file.name
    
    try:
        # 执行 ansible-playbook
        result = subprocess.run(
            ['ansible-playbook', '-i', inv_path, pb_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return result.stdout
    finally:
        # 清理临时文件
        os.unlink(inv_path)
        os.unlink(pb_path)

