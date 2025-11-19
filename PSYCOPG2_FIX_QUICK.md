# ⚡ 一分钟解决依赖问题

## 问题症状

```
ERROR: Could not find a version that satisfies the requirement psycopg2-binary==2.9.9
```

## 已修复

✅ `backend/requirements.txt` 第 7 行已删除

## 现在执行

在你的**生产服务器**上：

```bash
cd /opt/trustagency
git pull origin main
bash fix-memory-error.sh
```

**或手动操作**：

```bash
cd /opt/trustagency

# 清理旧镜像
docker-compose -f docker-compose.prod.yml down
docker system prune -a -f

# 重建
docker-compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 验证（10-15 分钟后）
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8001/health
```

---

**成功标志**：
```
所有容器 Up (healthy)
API 返回 {"status": "ok"}
```

这次就能成功了！🎉
