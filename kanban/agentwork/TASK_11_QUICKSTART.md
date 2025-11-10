# Task 11 - E2E 测试快速开始指南

## 🚀 3 分钟快速开始

### 第 1 步: 安装依赖 (1 分钟)
```bash
cd /Users/ck/Desktop/Project/trustagency
npm install
```

### 第 2 步: 启动后端服务
```bash
# 在另一个终端运行
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 第 3 步: 启动前端服务
```bash
# 在又一个终端运行
cd site
python -m http.server 80 --directory .
```

### 第 4 步: 运行测试 (2 分钟)
```bash
npm test
```

## 🎯 不同的运行方式

### 1️⃣ 最简单: UI 模式 (推荐新手)
```bash
npm run test:ui
```
- 打开交互式浏览器
- 可视化选择测试
- 实时观看执行
- 最方便的调试方式

### 2️⃣ 快速运行: Headless 模式
```bash
npm test
```
- 后台快速运行
- 所有浏览器
- 生成完整报告
- CI/CD 友好

### 3️⃣ 可视化: Headed 模式
```bash
npm run test:headed
```
- 看得到浏览器
- 便于理解流程
- 执行较慢
- 适合演示

### 4️⃣ 深度调试: Debug 模式
```bash
npm run test:debug
```
- Playwright Inspector
- 逐行执行
- 完整的变量检查
- 适合问题排查

## 🎪 运行特定测试

### 仅认证测试
```bash
npm run test:auth
```

### 仅平台功能
```bash
npm run test:platforms
```

### 仅文章功能
```bash
npm run test:articles
```

### 仅错误处理
```bash
npm run test:errors
```

### 仅性能和安全
```bash
npm run test:performance
```

## 📊 查看测试报告

运行测试后查看详细报告:
```bash
npm run report
```

报告包含:
- ✅ 每个测试的详细信息
- 📸 失败时的截图
- 🎬 失败时的视频录制
- ⏱️ 每个测试的执行时间
- 📈 整体测试统计

## 🔍 常见测试命令组合

### 运行所有 Chrome 测试
```bash
npx playwright test --project=chromium
```

### 运行所有 Firefox 测试
```bash
npx playwright test --project=firefox
```

### 运行所有 Safari 测试
```bash
npx playwright test --project=webkit
```

### 只运行失败的测试
```bash
npx playwright test --last-failed
```

### 运行特定文件
```bash
npx playwright test tests/e2e/auth.spec.js
```

### 运行特定测试 (按名称)
```bash
npx playwright test -g "should successfully register"
```

### 运行并更新快照 (如有)
```bash
npx playwright test --update-snapshots
```

## 🛠️ 故障排除

### ❌ 错误: "找不到 module"
```bash
# 重新安装依赖
npm install --force
```

### ❌ 错误: "端口 8001 已被占用"
```bash
# 杀死占用端口的进程
kill -9 $(lsof -t -i:8001)

# 或在 macOS 上:
sudo lsof -i :8001
sudo kill -9 <PID>
```

### ❌ 错误: "连接被拒绝"
```bash
# 确保后端已启动
curl http://localhost:8001/api/health

# 如果不可达，在后端目录运行:
cd backend
python -m uvicorn app.main:app --port 8001
```

### ❌ 错误: "测试超时"
```bash
# 增加超时时间 (在 test.beforeEach 中)
test.setTimeout(60000); // 60 秒
```

### ❌ 错误: "浏览器下载失败"
```bash
# 手动安装浏览器
npx playwright install
```

## 📝 测试套件说明

### 1. auth.spec.js (认证测试)
测试用户注册、登录、登出、token 管理
- 11 个测试用例
- 预计运行时间: 2 分钟

### 2. platforms.spec.js (平台功能)
测试平台列表、搜索、过滤、排序、分页
- 21 个测试用例  
- 预计运行时间: 3 分钟

### 3. articles.spec.js (文章功能)
测试文章列表、搜索、分类、排序、分页
- 23 个测试用例
- 预计运行时间: 3 分钟

### 4. error-scenarios.spec.js (错误处理)
测试网络错误、验证错误、API 错误等
- 20 个测试用例
- 预计运行时间: 2.5 分钟

### 5. performance.spec.js (性能和安全)
测试性能指标、安全防护、API 安全
- 18 个测试用例
- 预计运行时间: 2 分钟

**总计**: ~12.5 分钟（所有浏览器）

## 💡 有用的技巧

### 1. 快速编辑和重运行
```bash
# 编辑测试文件后，按 'R' 重运行
npm run test:ui
```

### 2. 观看特定测试流程
```bash
npx playwright test auth.spec.js --headed
```

### 3. 保存失败时的截图
截图自动保存在 `test-results/` 目录

### 4. 调试 JavaScript
在测试中使用:
```javascript
await page.pause();  // 暂停执行，打开 Inspector
```

### 5. 查看网络请求
在测试中使用:
```javascript
await page.on('response', response => {
  console.log(response.url(), response.status());
});
```

## 🎓 学习资源

### 官方文档
- https://playwright.dev/docs/intro

### 选择器参考
- Text: `text=登录`
- Locator: `page.locator()`
- XPath: `//button[@id="login"]`
- CSS: `button.btn-primary`

### 断言参考
```javascript
expect(element).toBeVisible();
expect(text).toContain('error');
expect(count).toBeGreaterThan(0);
expect(url).toMatch(/platforms/);
```

## 📈 预期测试结果

运行 `npm test` 后，应该看到:

```
...
✓ auth.spec.js (11 tests) [2.3 s]
✓ platforms.spec.js (21 tests) [3.1 s]
✓ articles.spec.js (23 tests) [3.2 s]
✓ error-scenarios.spec.js (20 tests) [2.5 s]
✓ performance.spec.js (18 tests) [2.0 s]

93 passed [12.8 s]
```

## 🚨 如果测试失败

1. **检查日志**
   ```bash
   npm run test:ui  # 查看具体失败信息
   ```

2. **查看截图**
   ```
   test-results/auth-should-successfully-register-chromium/
   ```

3. **查看视频**
   ```
   test-results/video.webm
   ```

4. **检查后端**
   ```bash
   curl http://localhost:8001/api/health
   ```

5. **检查前端**
   ```bash
   curl http://localhost/
   ```

## 🎉 测试成功标志

✅ 看到类似输出:
```
93 passed ✓
Total time: 12.8 s
```

✅ HTML 报告可访问:
```bash
npm run report
```

✅ 可以在浏览器中看到测试结果详情

## 📞 需要帮助?

1. 查看完整报告: `npm run report`
2. 使用调试模式: `npm run test:debug`
3. 查看特定测试: `npm run test:ui`
4. 检查文档: `TASK_11_COMPLETION_REPORT.md`

## 🎯 下一步

完成 E2E 测试后，可以:

1. **集成到 CI/CD**
   ```bash
   # 在 GitHub Actions 中运行
   npm test -- --reporter=junit
   ```

2. **生成覆盖率报告**
   ```bash
   npm test -- --reporter=html
   npm run report
   ```

3. **持续监控**
   - 定期运行测试
   - 跟踪性能趋势
   - 监控失败率

---

**祝测试顺利! 🚀**
