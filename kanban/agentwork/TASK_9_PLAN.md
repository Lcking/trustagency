# 📋 Task 9 计划 - 后端单元测试编写

**预计耗时**: 3.0 小时  
**优先级**: 高 (代码质量保证)  
**状态**: 准备就绪

---

## 🎯 目标

编写覆盖率 90%+ 的完整单元测试套件，确保后端功能的正确性和稳定性。

---

## 📊 测试范围

### 1. 认证系统测试 (0.5 小时)

**文件**: `tests/test_auth.py`

**测试覆盖**:
- ✅ 用户注册
- ✅ 用户登录
- ✅ 令牌生成和验证
- ✅ 密码加密
- ✅ 认证失败场景

**关键测试用例**:
```python
def test_admin_registration_success()
def test_admin_registration_duplicate_email()
def test_admin_login_success()
def test_admin_login_invalid_credentials()
def test_token_generation()
def test_token_verification()
def test_token_expiry()
```

### 2. 平台 API 测试 (0.5 小时)

**文件**: `tests/test_platforms.py`

**测试覆盖**:
- ✅ 平台创建
- ✅ 平台列表查询
- ✅ 平台更新
- ✅ 平台删除
- ✅ 搜索和过滤
- ✅ 分页功能

**关键测试用例**:
```python
def test_create_platform()
def test_list_platforms()
def test_update_platform()
def test_delete_platform()
def test_platform_search()
def test_platform_pagination()
```

### 3. 文章 API 测试 (0.5 小时)

**文件**: `tests/test_articles.py`

**测试覆盖**:
- ✅ 文章创建
- ✅ 文章列表查询
- ✅ 文章更新
- ✅ 文章发布
- ✅ 自动 slug 生成
- ✅ 浏览统计

**关键测试用例**:
```python
def test_create_article()
def test_list_articles()
def test_update_article()
def test_publish_article()
def test_slug_generation()
def test_view_count_increment()
```

### 4. AI 任务测试 (0.5 小时)

**文件**: `tests/test_ai_tasks.py`

**测试覆盖**:
- ✅ 任务创建
- ✅ 任务查询
- ✅ 任务状态更新
- ✅ 任务错误处理

**关键测试用例**:
```python
def test_create_ai_task()
def test_query_ai_task()
def test_update_task_status()
def test_task_error_handling()
```

### 5. Celery 任务测试 (0.4 小时)

**文件**: `tests/test_celery_tasks.py`

**测试覆盖**:
- ✅ 任务提交
- ✅ 任务执行
- ✅ 错误重试
- ✅ 任务完成回调

**关键测试用例**:
```python
def test_generate_article_batch_submission()
def test_generate_single_article_execution()
def test_task_retry_mechanism()
def test_task_completion_callback()
```

### 6. OpenAI 集成测试 (0.4 小时)

**文件**: `tests/test_openai_service.py`

**测试覆盖**:
- ✅ OpenAI 连接
- ✅ 文章生成
- ✅ 错误处理
- ✅ 重试机制
- ✅ 健康检查

**关键测试用例**:
```python
def test_openai_initialization()
def test_article_generation()
def test_rate_limit_handling()
def test_connection_error_handling()
def test_health_check()
```

### 7. 数据库操作测试 (0.2 小时)

**文件**: `tests/test_database.py`

**测试覆盖**:
- ✅ 数据库连接
- ✅ CRUD 操作
- ✅ 事务处理
- ✅ 数据一致性

**关键测试用例**:
```python
def test_database_connection()
def test_model_crud_operations()
def test_transaction_rollback()
def test_data_integrity()
```

---

## 🛠️ 测试框架

### 依赖包

```bash
pip install pytest==7.4.3
pip install pytest-cov==4.1.0
pip install pytest-asyncio==0.21.1
pip install pytest-mock==3.12.0
pip install httpx==0.25.0
```

### 项目结构

```
backend/
├── app/
│   ├── main.py
│   ├── models/
│   ├── routes/
│   └── services/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # 共享 fixtures
│   ├── test_auth.py             # 认证测试
│   ├── test_platforms.py        # 平台测试
│   ├── test_articles.py         # 文章测试
│   ├── test_ai_tasks.py         # AI 任务测试
│   ├── test_celery_tasks.py     # Celery 任务测试
│   ├── test_openai_service.py   # OpenAI 服务测试
│   ├── test_database.py         # 数据库测试
│   └── test_admin_routes.py     # Admin 路由测试
└── pytest.ini                   # pytest 配置
```

### conftest.py 模板

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

# 使用内存数据库用于测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def admin_token(client):
    # 创建测试用户并返回令牌
    response = client.post(
        "/api/admin/register",
        json={"email": "test@test.com", "password": "test123", "full_name": "Test User"}
    )
    return response.json()["access_token"]
```

---

## 📝 测试编写指南

### 1. 基本测试结构

```python
def test_feature_success_case():
    """测试成功场景"""
    # 准备数据 (Arrange)
    # 执行操作 (Act)
    # 验证结果 (Assert)
    pass

def test_feature_failure_case():
    """测试失败场景"""
    # 准备数据
    # 执行操作，预期异常
    # 验证异常类型和消息
    pass

def test_feature_edge_case():
    """测试边界情况"""
    # 测试边界值、空值等
    pass
```

### 2. API 测试示例

```python
def test_create_article(client, admin_token):
    response = client.post(
        "/api/articles",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Test Article",
            "content": "Test Content",
            "category": "guide"
        }
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Article"
```

### 3. 数据库测试示例

```python
def test_create_platform(db_session):
    from app.models import Platform
    
    platform = Platform(
        name="Test Platform",
        description="Test Description"
    )
    db_session.add(platform)
    db_session.commit()
    
    assert platform.id is not None
    assert db_session.query(Platform).filter(Platform.name == "Test Platform").first()
```

---

## 🏃 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_auth.py
```

### 运行特定测试函数

```bash
pytest tests/test_auth.py::test_admin_login_success
```

### 查看覆盖率

```bash
pytest --cov=app --cov-report=html
# 报告生成在 htmlcov/index.html
```

### 并行运行测试

```bash
pytest -n auto  # 自动并行
pytest -n 4     # 使用 4 个进程
```

---

## 📊 覆盖率目标

| 模块 | 目标 | 说明 |
|------|------|------|
| routes/ | 95% | API 端点完整测试 |
| models/ | 100% | 数据模型全覆盖 |
| services/ | 90% | 业务逻辑充分测试 |
| schemas/ | 80% | 验证逻辑测试 |
| 总体 | 90% | 整体覆盖率目标 |

---

## ✅ 测试检查清单

- [ ] 认证测试完成且通过
- [ ] 平台 API 测试完成且通过
- [ ] 文章 API 测试完成且通过
- [ ] AI 任务测试完成且通过
- [ ] Celery 任务测试完成且通过
- [ ] OpenAI 服务测试完成且通过
- [ ] 数据库测试完成且通过
- [ ] 管理后台测试完成且通过
- [ ] 覆盖率 >= 90%
- [ ] 所有测试通过 ✅

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install pytest pytest-cov pytest-asyncio pytest-mock httpx
```

### 2. 创建测试目录

```bash
mkdir tests
touch tests/__init__.py
touch tests/conftest.py
```

### 3. 编写第一个测试

```bash
# 创建 tests/test_auth.py
# 编写测试用例
# 运行测试: pytest tests/test_auth.py
```

### 4. 检查覆盖率

```bash
pytest --cov=app --cov-report=term-missing
```

---

## 💡 最佳实践

✅ **AAA 模式**: 准备 (Arrange) → 执行 (Act) → 验证 (Assert)  
✅ **命名规范**: `test_<feature>_<scenario>`  
✅ **单一职责**: 每个测试只测试一个功能  
✅ **使用 fixtures**: 共享测试数据和配置  
✅ **模拟外部依赖**: Mock API、数据库等  
✅ **测试分类**: 单元测试、集成测试分离  
✅ **持续运行**: 在每次代码变更前运行  

---

## 📝 预期成果

✅ 70+ 个单元测试用例  
✅ 90%+ 代码覆盖率  
✅ 所有核心功能验证  
✅ 完整的测试文档  
✅ 测试用例示例  
✅ 可持续集成基础  

---

## 🎯 时间估算

| 阶段 | 时间 | 说明 |
|------|------|------|
| 准备工作 | 0.3h | 环境配置、fixtures 编写 |
| 认证测试 | 0.5h | 5-8 个测试用例 |
| API 测试 | 1.0h | 15-20 个测试用例 |
| 任务测试 | 0.7h | 8-10 个测试用例 |
| 覆盖率优化 | 0.5h | 提高覆盖率到 90%+ |
| **总计** | **3.0h** | |

---

**准备状态**: ✅ 就绪  
**下一步**: 立即开始 Task 9 实施  
**预计完成**: 2025-11-06 21:50

