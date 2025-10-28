"""
配置备份 Celery 任务
"""
try:
    from celery import shared_task
except ImportError:
    from web_ansible.celery_stub import shared_task

from django.utils import timezone
from django.conf import settings
from .models import ConfigBackup, RestoreHistory
from devices.models import Device
import os
from django.contrib.auth import get_user_model

try:
    import paramiko
except ImportError:
    paramiko = None

User = get_user_model()


@shared_task
def backup_device_config(device_id, user_id=None):
    """备份设备配置"""
    try:
        device = Device.objects.get(id=device_id)
        user = User.objects.get(id=user_id) if user_id else None
        
        # 创建备份记录
        backup = ConfigBackup.objects.create(
            device=device,
            status='in_progress',
            backup_type='manual' if user else 'scheduled',
            created_by=user
        )
        
        try:
            # 使用 Paramiko 获取配置
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh_client.connect(
                hostname=device.ip_address,
                port=device.ssh_port,
                username=device.username,
                password=device.password,
                timeout=30,
                look_for_keys=False,
                allow_agent=False
            )
            
            # 执行命令获取 running-config
            stdin, stdout, stderr = ssh_client.exec_command('show running-config')
            config_content = stdout.read().decode('utf-8')
            
            ssh_client.close()
            
            # 保存配置到文件
            backup_dir = os.path.join(
                settings.BACKUP_DIR,
                device.hostname,
                timezone.now().strftime('%Y/%m/%d')
            )
            os.makedirs(backup_dir, exist_ok=True)
            
            file_name = f"{device.hostname}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.cfg"
            file_path = os.path.join(backup_dir, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # 更新备份记录
            backup.config_content = config_content
            backup.file_path = file_path
            backup.file_size = os.path.getsize(file_path)
            backup.status = 'success'
            backup.save()
            
            return {
                'success': True,
                'device_id': device_id,
                'device_name': device.name,
                'backup_id': backup.id,
                'file_path': file_path,
                'file_size': backup.file_size
            }
            
        except Exception as e:
            backup.status = 'failed'
            backup.error_message = str(e)
            backup.save()
            
            return {
                'success': False,
                'device_id': device_id,
                'error': str(e)
            }
            
    except Device.DoesNotExist:
        return {
            'success': False,
            'device_id': device_id,
            'error': '设备不存在'
        }
    except Exception as e:
        return {
            'success': False,
            'device_id': device_id,
            'error': str(e)
        }


@shared_task
def backup_all_devices(user_id=None):
    """备份所有设备"""
    devices = Device.objects.filter(is_active=True, status='online')
    results = []
    
    for device in devices:
        result = backup_device_config.delay(device.id, user_id)
        results.append({
            'device_id': device.id,
            'device_name': device.name,
            'task_id': result.id
        })
    
    return {
        'success': True,
        'message': f'已提交 {len(results)} 个备份任务',
        'results': results
    }


@shared_task
def restore_device_config(backup_id, user_id=None):
    """恢复设备配置"""
    try:
        backup = ConfigBackup.objects.get(id=backup_id)
        user = User.objects.get(id=user_id) if user_id else None
        device = backup.device
        
        # 创建恢复记录
        restore = RestoreHistory.objects.create(
            device=device,
            backup=backup,
            status='in_progress',
            created_by=user,
            started_at=timezone.now()
        )
        
        try:
            # 使用 Paramiko 恢复配置
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh_client.connect(
                hostname=device.ip_address,
                port=device.ssh_port,
                username=device.username,
                password=device.password,
                timeout=30,
                look_for_keys=False,
                allow_agent=False
            )
            
            # 进入配置模式并应用配置
            channel = ssh_client.invoke_shell()
            channel.send('configure terminal\n')
            
            # 逐行发送配置
            for line in backup.config_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('!'):
                    channel.send(f'{line}\n')
            
            channel.send('end\n')
            channel.send('write memory\n')
            
            # 读取输出
            import time
            time.sleep(5)
            output = ''
            while channel.recv_ready():
                output += channel.recv(4096).decode('utf-8')
            
            channel.close()
            ssh_client.close()
            
            # 更新恢复记录
            restore.output = output
            restore.status = 'success'
            restore.completed_at = timezone.now()
            restore.save()
            
            return {
                'success': True,
                'device_id': device.id,
                'device_name': device.name,
                'restore_id': restore.id
            }
            
        except Exception as e:
            restore.status = 'failed'
            restore.error_message = str(e)
            restore.completed_at = timezone.now()
            restore.save()
            
            return {
                'success': False,
                'device_id': device.id,
                'error': str(e)
            }
            
    except ConfigBackup.DoesNotExist:
        return {
            'success': False,
            'backup_id': backup_id,
            'error': '备份不存在'
        }
    except Exception as e:
        return {
            'success': False,
            'backup_id': backup_id,
            'error': str(e)
        }


@shared_task
def cleanup_old_backups():
    """清理过期备份"""
    from datetime import timedelta
    
    retention_days = settings.BACKUP_RETENTION_DAYS
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    old_backups = ConfigBackup.objects.filter(created_at__lt=cutoff_date)
    
    deleted_count = 0
    for backup in old_backups:
        # 删除文件
        if backup.delete_file():
            deleted_count += 1
        # 删除记录
        backup.delete()
    
    return {
        'success': True,
        'message': f'已清理 {deleted_count} 个过期备份',
        'deleted_count': deleted_count
    }

