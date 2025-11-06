# TrustAgency Backend

后端项目采用 Python FastAPI + SQLAlchemy + Celery + Redis 的现代架构。

## 快速开始

### 1. 虚拟环境设置

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

访问 http://localhost:8001/api/docs 查看 API 文档

### 4. 启动 Redis（可选，用于任务队列）

```bash
redis-server
```

### 5. 启动 Celery Worker（可选，用于后台任务）

```bash
celery -A app.celery_tasks worker --loglevel=info
```

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用主文件
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # 数据库模型
│   ├── schemas/                # Pydantic Schema
│   ├── routes/                 # API 路由
│   ├── services/               # 业务逻辑
│   ├── utils/                  # 工具函数
│   ├── middleware/             # 中间件
│   └── admin/                  # FastAPI Admin 配置
├── migrations/                 # 数据库迁移（Alembic）
├── tests/                      # 测试用例
├── .env                        # 环境变量（本地开发）
├── .env.example                # 环境变量示例
├── requirements.txt            # 依赖列表
├── pyproject.toml              # 项目配置
├── alembic.ini                 # 迁移工具配置
├── Dockerfile                  # Docker 镜像配置
├── docker-compose.yml          # Docker Compose 配置
└── README.md                   # 本文件
```

## 环境配置

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 配置必要的环境变量：
- `DATABASE_URL`: 数据库连接字符串
- `SECRET_KEY`: JWT 加密密钥
- `OPENAI_API_KEY`: OpenAI API 密钥
- 其他必要配置

## API 文档

启动应用后访问：
- **Swagger UI**: http://localhost:8001/api/docs
- **ReDoc**: http://localhost:8001/api/redoc

## 主要功能

### 认证系统
- 管理员登录
- JWT Token 认证
- 密码管理

### 平台管理
- CRUD 操作
- 搜索和排序
- 批量操作

### 文章管理
- CRUD 操作
- 分类管理
- 发布/草稿

### AI 内容生成
- 批量标题输入
- 自动文章生成
- 异步任务处理
- 进度跟踪

### 管理后台
- FastAPI Admin 集成
- 实时搜索和排序
- 用户友好的界面

## 技术栈

- **框架**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT + Passlib
- **任务队列**: Celery + Redis
- **AI 集成**: OpenAI API
- **测试**: Pytest
- **部署**: Docker

## 开发

### 代码格式

```bash
# Black 格式化
black app/

# Flake8 检查
flake8 app/

# MyPy 类型检查
mypy app/
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 显示覆盖率
pytest --cov=app tests/
```

## 部署

### Docker 部署

```bash
docker-compose up -d
```

### 手动部署

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## 故障排除

### 数据库错误
- 检查 `DATABASE_URL` 配置
- 确保数据库服务正在运行

### Redis 错误
- 确保 Redis 服务正在运行
- 检查 `REDIS_URL` 配置

### OpenAI 错误
- 检查 API 密钥是否正确
- 确保账户有足够的配额

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**当前进度**: Task 1 - 项目初始化和环境配置 (进行中)
