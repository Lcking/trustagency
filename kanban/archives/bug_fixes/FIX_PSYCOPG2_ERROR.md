# 🔧 紧急修复：requirements.txt 依赖问题

## 问题

Docker 构建失败，错误信息：
```
ERROR: Could not find a version that satisfies the requirement psycopg2-binary==2.9.9
ERROR: No matching distribution found for psycopg2-binary==2.9.9
```

## 原因

- `requirements.txt` 中仍然包含 `psycopg2-binary==2.9.9`（PostgreSQL 数据库驱动）
- 但这个版本已经从 PyPI 中移除
- 我们已经使用 SQLite，不需要 PostgreSQL 驱动

## 解决方案

从 `backend/requirements.txt` 中删除第 7 行：
```diff
  # Database
  sqlalchemy==2.0.23
  alembic==1.13.0
- psycopg2-binary==2.9.9
  
  # Authentication
```

## 修复完成

✅ `requirements.txt` 已更新，删除了不可用的 psycopg2-binary

## 现在该做什么

在你的**生产服务器**上执行：

```bash
cd /opt/trustagency
git pull origin main
bash fix-memory-error.sh
```

或手动操作：

```bash
# 清理旧镜像
docker-compose -f docker-compose.prod.yml down
docker rmi -f $(docker images | grep backend | awk '{print $3}')
docker system prune -a -f

# 重新构建
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 等待 10-15 分钟...

# 验证
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8001/health
```

---

**预期输出**：
```json
{"status": "ok"}
```

这次应该能成功了！🚀
