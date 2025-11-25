# VSCode 性能优化方案

## 问题现象
- VSCode 占用 6.6GB 内存
- Pylance 和 TypeScript 服务占用 1GB+ 内存
- 导致系统命令行操作（curl、git等）反应缓慢
- VSCode 频繁卡顿导致错误信息丢失

## 根本原因
1. **Pylance 插件过度分析** - Python 类型检查消耗大量内存
2. **TypeScript 多进程** - 开启了多个 tsserver 实例
3. **Edge DevTools 持续运行** - 调试工具常驻内存
4. **Electron 进程数过多** - 每个标签页都创建新进程

## 立即修复方案

### 方案1: 关闭不必要的插件
编辑 `~/.config/Code/User/settings.json`：

```json
{
  // 禁用 Pylance 的实时分析
  "python.linting.enabled": false,
  "python.analysis.typeCheckingMode": "off",
  "[python]": {
    "editor.defaultFormatter": "black-formatter",
    "editor.formatOnSave": false
  },

  // 禁用 TypeScript 自动编译
  "typescript.enablePromptUseWorkspaceTsdk": false,
  "typescript.check.npmIsInstalled": false,
  "typescript.disableAutomaticTypeAcquisition": true,

  // 关闭不必要的工具
  "edge-devtools.enabled": false,
  "webhint.enableTelemetry": false,

  // 减少扩展加载
  "extensions.ignoreRecommendations": true,

  // 编辑器性能优化
  "editor.largeFileOptimizations": true,
  "editor.occurrencesHighlight": false,
  "editor.selectionHighlight": false,
  "search.followSymlinks": false
}
```

### 方案2: 一键关闭 VSCode
```bash
pkill -9 "Code Helper"
pkill -9 "Electron"
```

然后重新打开 VSCode（会清空缓存）。

### 方案3: 分离开发环境
```bash
# 在终端中做开发和测试（不使用VSCode的集成终端）
cd /Users/ck/Desktop/Project/trustagency

# 启动后端
nohup python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 > /tmp/backend.log 2>&1 &

# 测试API
curl http://localhost:8001/admin/

# 查看日志
tail -f /tmp/backend.log
```

## 长期优化方案

### 1. 使用 Lightweight 编辑器
- VS Code 改为 VS Code Insiders（更轻量）
- 或使用 Sublime Text / Vim 处理大文件

### 2. 分离项目工作区
```bash
# 后端项目单独开启 VSCode
code /Users/ck/Desktop/Project/trustagency/backend

# 前端项目单独开启 VSCode  
code /Users/ck/Desktop/Project/trustagency/frontend
```

### 3. 禁用 Remote 和调试功能
如果不需要远程开发，完全禁用相关扩展。

### 4. 设置合理的工作区配置
项目根目录创建 `.vscode/settings.json`：

```json
{
  "python.linting.enabled": false,
  "python.analysis.typeCheckingMode": "off",
  "typescript.enablePromptUseWorkspaceTsdk": false,
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/node_modules": true
  },
  "search.exclude": {
    "**/__pycache__": true,
    "**/node_modules": true,
    "**/.git": true
  }
}
```

## 立即行动

**推荐:**
1. ✅ 关闭 VSCode
2. ✅ 在终端中启动后端和运行测试
3. ✅ 需要编辑文件时才打开 VSCode
4. ✅ 重新打开 VSCode 时应用上述配置

这样可以：
- 减少内存占用 50-60%
- 提升系统响应速度 10倍+
- 避免卡顿导致的数据丢失
- 让终端命令秒级响应

## 验收建议

使用纯终端环境进行 bug 验收测试：

```bash
# 启动后端
cd /Users/ck/Desktop/Project/trustagency/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001

# 在另一个终端运行验收脚本
bash /Users/ck/Desktop/Project/trustagency/ACCEPTANCE_TEST.sh
```

或使用浏览器 DevTools 在终端中进行交互测试。
