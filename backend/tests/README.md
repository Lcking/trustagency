# TrustAgency 测试套件

## 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov httpx

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py

# 运行并显示覆盖率
pytest --cov=app --cov-report=html

# 运行详细输出
pytest -v

# 运行并显示print输出
pytest -s
```

## 测试覆盖

- ✅ API健康检查测试
- ✅ 认证系统测试
- ✅ 任务监控测试
- ✅ 备份系统测试
- ✅ 缓存系统测试
- ✅ 工具类单元测试

## 测试结构

```
tests/
├── __init__.py
├── test_api.py         # API集成测试
└── test_utils.py       # 工具类单元测试
```

## 持续集成

测试应该在以下场景中运行:
- 提交代码前
- Pull Request创建时
- 部署到生产环境前

## 扩展测试

未来可以添加:
- 性能测试
- 负载测试
- 端到端测试
- 安全测试
