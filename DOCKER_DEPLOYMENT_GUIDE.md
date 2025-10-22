# Docker 容器部署和测试指南

## 📋 部署前检查清单

### 1. 环境要求
- ✅ Docker 已安装（版本 20.10+）
- ✅ Docker Compose 已安装（版本 1.29+）
- ✅ 端口 80 未被占用（检查：`sudo lsof -i :80`）
- ✅ 足够的磁盘空间（nginx:alpine ~42MB）

### 2. 文件完整性检查
```bash
# 检查必需文件是否存在
ls -la Dockerfile                           # 应该存在
ls -la docker-compose.build.yml           # 应该存在
ls -la nginx/default.conf                 # 应该存在
ls -la site/                               # 应该存在
```

---

## 🚀 部署步骤

### 步骤 1: 构建 Docker 镜像

```bash
cd /Users/ck/Desktop/Project/trustagency

# 构建镜像（详细输出）
docker compose -f docker-compose.build.yml build

# 或者显示构建进度
docker compose -f docker-compose.build.yml build --progress=plain
```

**预期输出**：
```
[+] Building 15.2s (8/8) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [internal] load build context
 => [stage-0 0/6] FROM nginx:alpine
 => [stage-0 1/6] COPY ./site /usr/share/nginx/html
 => [stage-0 2/6] COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
 => [stage-0 3/6] EXPOSE 80
 => [stage-0 4/6] HEALTHCHECK --interval=30s ...
 => [stage-0 5/6] CMD ["nginx", "-g", "daemon off;"]
 => exporting to image
 => => naming to trustagency-web:latest
```

**如果出错**：
- 检查 Dockerfile 语法：`docker build --dry-run .`
- 检查 nginx 配置：`docker run -it nginx:alpine /bin/sh -c "nginx -t"`

---

### 步骤 2: 启动容器

```bash
# 启动单个容器（前台运行，方便查看日志）
docker compose -f docker-compose.build.yml up

# 或者后台运行
docker compose -f docker-compose.build.yml up -d

# 查看容器状态
docker compose -f docker-compose.build.yml ps

# 查看日志
docker compose -f docker-compose.build.yml logs -f web
```

**预期输出**：
```
trustagency-web    | /docker-entrypoint.sh: /docker-entrypoint.d is not empty, will attempt to execute files in lexicographic order
trustagency-web    | /docker-entrypoint.sh: info: Looking for shell scripts in /docker-entrypoint.d/
trustagency-web    | /docker-entrypoint.sh: info: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
trustagency-web    | 2025/10/22 11:15:00 [notice] 1#1: master process started
trustagency-web    | 2025/10/22 11:15:00 [notice] 1#1: signal process started
```

**如果容器启动失败**：
- 查看错误日志：`docker compose -f docker-compose.build.yml logs web`
- 检查端口是否被占用：`sudo lsof -i :80`
- 检查 nginx 配置：`docker exec trustagency-web nginx -t`

---

### 步骤 3: 测试容器访问

```bash
# 1. 访问首页
curl -i http://localhost/

# 2. 测试 HTTPS/HTTP2（如果启用）
curl -I http://localhost/index.html

# 3. 测试 robots.txt（HEALTHCHECK 使用）
curl -I http://localhost/robots.txt

# 4. 完整响应（包括所有头部）
curl -v http://localhost/
```

**预期响应**：
```
HTTP/1.1 200 OK
Server: nginx/1.27.0
Date: Wed, 22 Oct 2025 11:15:00 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 12345
Connection: keep-alive
Cache-Control: public, must-revalidate, no-store
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self';...
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## 🔍 详细验证步骤

### 验证 1: 缓存头配置生效

```bash
# HTML 文件 - 应该是 no-cache, no-store
curl -I http://localhost/index.html | grep -i cache-control

# 预期输出：
# Cache-Control: public, must-revalidate, no-store

# CSS 文件 - 应该是 7 天（604800 秒）
curl -I http://localhost/assets/css/main.css | grep -i cache-control

# 预期输出：
# Cache-Control: public, immutable, max-age=604800

# JavaScript 文件 - 应该是 7 天
curl -I http://localhost/assets/js/bootstrap.bundle.min.js | grep -i cache-control

# 预期输出：
# Cache-Control: public, immutable, max-age=604800

# 图片文件 - 应该是 30 天（2592000 秒）
curl -I http://localhost/assets/images/logo.png | grep -i cache-control

# 预期输出：
# Cache-Control: public, immutable, max-age=2592000
```

### 验证 2: 安全头配置生效

```bash
# 完整安全头检查
curl -I http://localhost/ | grep -E "X-Content-Type-Options|X-Frame-Options|X-XSS-Protection|Referrer-Policy|Content-Security-Policy|Permissions-Policy"

# 预期输出：
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Referrer-Policy: strict-origin-when-cross-origin
# Content-Security-Policy: default-src 'self';...
# Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 验证 3: Gzip 压缩生效

```bash
# 测试 gzip 压缩
curl -I --compressed http://localhost/assets/css/main.css | grep -i "content-encoding"

# 预期输出：
# Content-Encoding: gzip

# 对比压缩前后大小
echo "=== 未压缩大小 ==="
curl -s http://localhost/assets/css/main.css | wc -c

echo "=== 已压缩大小 ==="
curl -s --compressed http://localhost/assets/css/main.css | wc -c
```

### 验证 4: 健康检查运行

```bash
# 检查容器健康状态
docker ps | grep trustagency-web

# 预期输出应该显示：
# UP X seconds (healthy)

# 或者使用 inspect 查看详细信息
docker inspect --format='{{.State.Health.Status}}' trustagency-web

# 预期输出：
# healthy

# 查看健康检查日志
docker inspect trustagency-web | grep -A 10 "HealthCheck"
```

### 验证 5: 侧边栏内容验证

```bash
# 检查首页侧边栏是否正常加载
curl -s http://localhost/ | grep -c "相关资源"

# 预期输出：
# 1 或 2（取决于模板结构）

# 检查百科卡片
curl -s http://localhost/ | grep "热门百科" | head -1

# 检查指南卡片
curl -s http://localhost/ | grep "热门指南" | head -1
```

### 验证 6: 404 和错误处理

```bash
# 测试 404 错误处理
curl -I http://localhost/nonexistent-page

# 预期输出：
# HTTP/1.1 404 Not Found

# 测试隐藏文件保护（应该被拒绝）
curl -I http://localhost/.env

# 预期输出：
# HTTP/1.1 403 Forbidden

curl -I http://localhost/.git

# 预期输出：
# HTTP/1.1 403 Forbidden
```

---

## 📊 容器管理命令

```bash
# 查看容器日志
docker compose -f docker-compose.build.yml logs web

# 查看实时日志
docker compose -f docker-compose.build.yml logs -f web

# 执行命令在容器内
docker compose -f docker-compose.build.yml exec web nginx -t

# 进入容器 shell
docker compose -f docker-compose.build.yml exec web sh

# 重启容器
docker compose -f docker-compose.build.yml restart web

# 停止容器
docker compose -f docker-compose.build.yml stop

# 删除容器和网络
docker compose -f docker-compose.build.yml down

# 清理所有镜像和容器
docker compose -f docker-compose.build.yml down --rmi all

# 查看容器资源使用情况
docker stats trustagency-web
```

---

## 🔧 故障排除

### 问题 1: 端口 80 已被占用

```bash
# 查找占用端口 80 的进程
sudo lsof -i :80

# 杀死该进程
kill -9 <PID>

# 或者修改 docker-compose 使用其他端口
# 在 docker-compose.build.yml 中修改：
# ports:
#   - "8080:80"
```

### 问题 2: nginx 配置错误

```bash
# 进入容器验证 nginx 配置
docker compose -f docker-compose.build.yml exec web nginx -t

# 查看 nginx 进程状态
docker compose -f docker-compose.build.yml exec web ps aux | grep nginx

# 检查 nginx 监听的端口
docker compose -f docker-compose.build.yml exec web netstat -tlnp | grep nginx
```

### 问题 3: 容器启动失败

```bash
# 查看完整日志
docker compose -f docker-compose.build.yml logs web --tail=100

# 查看启动历史
docker inspect trustagency-web | grep -A 5 "State"

# 重新构建镜像（清除缓存）
docker compose -f docker-compose.build.yml build --no-cache
```

### 问题 4: 文件权限问题

```bash
# 检查 nginx 进程用户
docker compose -f docker-compose.build.yml exec web whoami

# 检查文件权限
docker compose -f docker-compose.build.yml exec web ls -la /usr/share/nginx/html/

# 修复权限（如果需要）
docker compose -f docker-compose.build.yml exec web chmod -R 755 /usr/share/nginx/html/
```

---

## ✅ GitHub 推送清单

在推送到 GitHub 前，请确保：

### 1. 代码完整性检查
```bash
# 检查所有必需文件
ls -la Dockerfile
ls -la docker-compose.build.yml
ls -la nginx/default.conf
ls -la site/
ls -la assets/

# 检查 .gitignore 配置（确保不上传敏感信息）
cat .gitignore
```

### 2. 文件大小检查
```bash
# 检查项目大小
du -sh /Users/ck/Desktop/Project/trustagency

# 列出超过 100MB 的文件
find . -size +100M -type f

# 如果有大文件，应该添加到 .gitignore
```

### 3. 敏感信息检查
```bash
# 检查是否有密钥、密码、token
grep -r "password\|secret\|token\|api_key" . --exclude-dir=.git --exclude-dir=node_modules

# 检查是否有私钥
find . -name "*.pem" -o -name "*.key" -o -name "*.ppk"

# 检查 .env 文件
ls -la .env* 2>/dev/null || echo "无 .env 文件，良好"
```

### 4. Git 准备
```bash
# 查看当前状态
git status

# 查看未跟踪的文件
git ls-files --others --exclude-standard

# 查看即将提交的文件
git diff --cached --name-only

# 查看修改但未暂存的文件
git diff --name-only
```

### 5. 提交和推送
```bash
# 添加所有文件
git add -A

# 查看待提交文件
git status

# 提交（包含详细信息）
git commit -m "feat: 完成 A-8 任务 - Docker 容器化和 Nginx 配置

- 创建 Dockerfile，基于 nginx:alpine
- 配置 nginx/default.conf 包含缓存策略、安全头、gzip 压缩
- 创建 docker-compose.build.yml 文件
- 验证容器启动和健康检查
- 验证缓存头、安全头、gzip 压缩生效
- 修复侧边栏 CSS 问题
- 完成侧边栏内容优化（3 个 bug 修复）"

# 查看提交历史
git log --oneline -5

# 推送到 GitHub
git push origin main

# 或者推送到特定分支
git push origin develop
```

---

## 📈 性能监测

### 持续监测容器
```bash
# 实时监测资源使用
docker stats trustagency-web --no-stream

# 查看容器网络统计
docker stats trustagency-web

# 查看镜像大小
docker images trustagency-web
```

### 日志分析
```bash
# 查看访问日志
docker compose -f docker-compose.build.yml exec web tail -f /var/log/nginx/access.log

# 查看错误日志
docker compose -f docker-compose.build.yml exec web tail -f /var/log/nginx/error.log

# 统计 HTTP 状态码
docker compose -f docker-compose.build.yml exec web tail -n 1000 /var/log/nginx/access.log | awk '{print $9}' | sort | uniq -c
```

---

## 📝 验证检查表

将以下检查项标记为完成：

- [ ] 构建镜像成功
- [ ] 容器启动成功
- [ ] 首页可访问（http://localhost/）
- [ ] 侧边栏正确显示（3 张卡片）
- [ ] 缓存头正确：HTML (no-store) / CSS/JS (7d) / Images (30d)
- [ ] 安全头全部存在：6 种安全头
- [ ] Gzip 压缩工作正常
- [ ] 健康检查返回 healthy
- [ ] 404 页面显示正确
- [ ] 隐藏文件被拒绝 (.git, .env)
- [ ] 日志输出正常
- [ ] 容器资源占用合理
- [ ] 所有文件已检查敏感信息
- [ ] .gitignore 配置正确
- [ ] 项目大小合理（<500MB）
- [ ] 可以安全推送到 GitHub

---

## 🎯 下一步计划

1. ✅ 完成部署和测试（本指南）
2. ✅ 验证所有配置生效
3. 🔄 推送到 GitHub（待执行）
4. 📋 创建发布说明（Release Notes）
5. 🚀 考虑生产部署（如需要）

---

**创建时间**: 2025-10-22 11:15
**最后更新**: 2025-10-22 11:15
**状态**: 准备部署测试 ✅
