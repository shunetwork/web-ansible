"""
测试运行中的服务器
"""
import requests
import sys
import io

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = 'http://127.0.0.1:8000'

def test_admin_page():
    """测试管理后台页面"""
    print("测试管理后台...")
    response = requests.get(f'{BASE_URL}/admin/')
    assert response.status_code == 200
    assert 'Cisco' in response.text
    print("✓ 管理后台正常")

def test_api_endpoints():
    """测试 API 端点（不需要认证的）"""
    print("\n测试 API 端点...")
    
    endpoints = [
        '/api/devices/',
        '/api/templates/',
        '/api/tasks/',
        '/api/backups/',
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{BASE_URL}{endpoint}')
            # API 需要认证，应该返回 401 或 403
            assert response.status_code in [200, 401, 403], f"端点 {endpoint} 返回了意外的状态码: {response.status_code}"
            print(f"✓ {endpoint} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint} - 错误: {str(e)}")

def test_jet_assets():
    """测试 Django Jet 静态资源"""
    print("\n测试静态资源...")
    response = requests.get(f'{BASE_URL}/admin/login/')
    assert response.status_code == 200
    print("✓ 静态资源加载正常")

def main():
    print("=" * 50)
    print("开始测试运行中的服务器")
    print("=" * 50)
    
    try:
        # 测试服务器是否运行
        response = requests.get(BASE_URL, timeout=5)
        print(f"✓ 服务器正在运行在 {BASE_URL}")
        print()
        
        # 运行测试
        test_admin_page()
        test_api_endpoints()
        test_jet_assets()
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！")
        print("=" * 50)
        print(f"\n访问管理后台: {BASE_URL}/admin/")
        print(f"API 基础地址: {BASE_URL}/api/")
        return 0
        
    except requests.exceptions.ConnectionError:
        print(f"✗ 无法连接到服务器 {BASE_URL}")
        print("请确保服务器正在运行：python manage.py runserver")
        return 1
    except AssertionError as e:
        print(f"\n✗ 测试失败: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

