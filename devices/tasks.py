"""
设备管理异步任务
"""
try:
    from celery import shared_task
except ImportError:
    from web_ansible.celery_stub import shared_task

from django.utils import timezone
from .models import Device
import csv
import io
from django.contrib.auth import get_user_model

try:
    import paramiko
    import socket
except ImportError:
    paramiko = None
    socket = None

User = get_user_model()


@shared_task(bind=True)
def test_device_connection(self, device_id):
    """测试设备连接"""
    try:
        device = Device.objects.get(id=device_id)
        
        # 使用 Paramiko 测试 SSH 连接
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh_client.connect(
                hostname=device.ip_address,
                port=device.ssh_port,
                username=device.username,
                password=device.password,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )
            
            # 执行简单命令测试
            stdin, stdout, stderr = ssh_client.exec_command('show version')
            output = stdout.read().decode('utf-8')
            
            # 尝试获取设备信息
            if 'Cisco IOS' in output or 'Cisco Internetwork' in output:
                # 解析版本信息
                lines = output.split('\n')
                for line in lines:
                    if 'Version' in line and not device.os_version:
                        device.os_version = line.strip()
                        break
            
            device.update_status('online', '连接成功')
            ssh_client.close()
            
            return {
                'success': True,
                'device_id': device_id,
                'message': '连接成功',
                'os_version': device.os_version
            }
            
        except paramiko.AuthenticationException:
            device.update_status('offline', '认证失败')
            return {
                'success': False,
                'device_id': device_id,
                'error': '认证失败，请检查用户名和密码'
            }
        except socket.timeout:
            device.update_status('offline', '连接超时')
            return {
                'success': False,
                'device_id': device_id,
                'error': '连接超时'
            }
        except Exception as e:
            device.update_status('offline', f'连接失败: {str(e)}')
            return {
                'success': False,
                'device_id': device_id,
                'error': str(e)
            }
        finally:
            ssh_client.close()
            
    except Device.DoesNotExist:
        return {
            'success': False,
            'device_id': device_id,
            'error': '设备不存在'
        }


@shared_task
def check_all_devices_health():
    """检查所有设备健康状态"""
    devices = Device.objects.filter(is_active=True)
    results = []
    
    for device in devices:
        result = test_device_connection.delay(device.id)
        results.append({
            'device_id': device.id,
            'device_name': device.name,
            'task_id': result.id
        })
    
    return {
        'message': f'已提交 {len(results)} 个健康检查任务',
        'results': results
    }


@shared_task
def import_devices_from_csv(csv_content, user_id):
    """从 CSV 导入设备"""
    try:
        user = User.objects.get(id=user_id)
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        created_count = 0
        updated_count = 0
        errors = []
        
        for row in reader:
            try:
                # 检查设备是否已存在
                device, created = Device.objects.update_or_create(
                    ip_address=row['ip_address'],
                    defaults={
                        'name': row['name'],
                        'hostname': row.get('hostname', row['name']),
                        'device_type': row.get('device_type', 'switch'),
                        'model': row.get('model', ''),
                        'ssh_port': int(row.get('ssh_port', 22)),
                        'username': row['username'],
                        'password': row['password'],
                        'location': row.get('location', ''),
                        'description': row.get('description', ''),
                        'created_by': user if created else None,
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                errors.append(f"行 {reader.line_num}: {str(e)}")
        
        return {
            'success': True,
            'created': created_count,
            'updated': updated_count,
            'errors': errors
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

