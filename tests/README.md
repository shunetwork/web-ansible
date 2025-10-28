# 测试文档

本项目使用 pytest 和 pytest-django 进行测试。

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定测试文件
```bash
pytest tests/test_devices.py
```

### 运行特定测试类
```bash
pytest tests/test_devices.py::TestDevice
```

### 运行特定测试方法
```bash
pytest tests/test_devices.py::TestDevice::test_create_device
```

### 带详细输出运行测试
```bash
pytest -v
```

### 运行测试并显示覆盖率
```bash
pytest --cov=. --cov-report=html
```

### 运行标记的测试
```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"
```

## 测试组织

### 测试文件结构
```
tests/
├── __init__.py          # 测试包初始化
├── conftest.py          # pytest 配置和 fixtures
├── test_devices.py      # 设备管理测试
├── test_templates.py    # 模板管理测试
├── test_tasks.py        # 任务执行测试
├── test_backups.py      # 配置备份测试
├── test_audit.py        # 审计日志测试
└── test_api.py          # API 接口测试
```

### Fixtures

在 `conftest.py` 中定义了常用的 fixtures：

- `test_user`: 创建测试用户
- `admin_user`: 创建管理员用户
- `device_group`: 创建设备组
- `test_device`: 创建测试设备
- `config_template`: 创建配置模板
- `test_task`: 创建测试任务
- `config_backup`: 创建配置备份

## 测试覆盖

### 模型测试
- 设备模型（Device, DeviceGroup, DeviceCredential）
- 模板模型（ConfigTemplate, TemplateVersion, TemplateVariable）
- 任务模型（Task, TaskResult, Schedule）
- 备份模型（ConfigBackup, ConfigDiff, RestoreHistory）
- 审计模型（AuditLog, LoginHistory, OperationStatistics）

### API 测试
- 设备 API
- 模板 API
- 任务 API
- 备份 API
- 审计 API

### 功能测试
- 创建、读取、更新、删除操作
- 模型关系和方法
- 数据验证
- API 端点和序列化

## 编写新测试

### 测试模型
```python
import pytest

@pytest.mark.django_db
class TestMyModel:
    def test_create_model(self):
        obj = MyModel.objects.create(name='Test')
        assert obj.name == 'Test'
```

### 测试 API
```python
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestMyAPI:
    def test_list_endpoint(self, admin_user):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        response = client.get('/api/mymodel/')
        assert response.status_code == 200
```

### 使用 Fixtures
```python
@pytest.mark.django_db
def test_with_fixtures(test_user, test_device):
    # test_user 和 test_device 会自动创建
    assert test_device.created_by == test_user
```

## 持续集成

测试可以集成到 CI/CD 流程中：

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov
```

## 最佳实践

1. **每个测试应该独立**：不要依赖其他测试的执行顺序
2. **使用 fixtures**：重用测试数据和配置
3. **清晰的测试名称**：测试名称应该描述测试的内容
4. **测试边界情况**：不仅测试正常情况，也要测试异常情况
5. **保持测试简单**：每个测试只测试一个功能点
6. **及时更新测试**：当代码变化时，同步更新测试

## 调试测试

### 使用 pdb 调试
```bash
pytest --pdb
```

### 查看打印输出
```bash
pytest -s
```

### 只运行失败的测试
```bash
pytest --lf
```

### 运行失败后停止
```bash
pytest -x
```

