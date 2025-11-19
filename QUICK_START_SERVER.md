# 🎯 在服务器上执行（只需3步）

## 代码已推送到GitHub ✅

---

## 🚀 在你的服务器上执行这些命令

### 第1步：进入项目并拉取最新代码
```bash
cd /opt/trustagency
git pull origin main
```

### 第2步：执行自动修复脚本
```bash
bash fix-deployment.sh
```

**这会自动完成：**
- 生成 SECRET_KEY
- 配置 .env.prod
- 设置 Docker 国内镜像源
- 重启所有容器
- 验证部署

**耗时：** 2-3 分钟

### 第3步：验证部署成功
```bash
# 查看容器状态（应该都是 Up）
docker-compose -f docker-compose.prod.yml ps

# 测试后端API（应该返回 {"status": "ok"}）
curl http://localhost:8001/health
```

---

## ✅ 成功标志

- ✅ 所有容器状态为 Up 或 (healthy)
- ✅ API 返回 {"status": "ok"}
- ✅ 能访问 http://your-domain.com/admin/
- ✅ 能用 admin/admin123 登录

---

## 🆘 如果出错

```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs backend

# 或查看完整文档
cat README_DEPLOYMENT_FIX.md
```

---

**就这么简单！现在就试试吧！🚀**
