# 🚀 VSCode 性能优化方案

**问题根源**：29个插件导致内存占用19GB/24GB (79%)，触发频繁Swap

## 📊 问题诊断结果

```
当前内存占用：
- Code Helper (Plugin): 1.4GB ❌ 泄漏
- Code Helper (Renderer): 1.2GB ⚠️ 高CPU
- Pylance: 503MB 
- TypeScript Server: 258MB
- Edge DevTools: 193MB
- HTML Language Server: 193MB

总计：3.7GB 仅用于VSCode插件和语言服务器
```

## ✅ 立即采取行动（5分钟）

### 步骤1：禁用不必要的插件

打开 Command Palette (Cmd+Shift+P) 并执行：

```
Extensions: Show Built-in Extensions
```

禁用以下插件（用于项目无关的工作）：
- ❌ MS MSSQL Tools & SQL相关 (3个)
- ❌ PHP Debug  
- ❌ PowerShell
- ❌ Azure Containers
- ❌ Codespaces
- ❌ Live Server (如果不做前端调试)
- ❌ NPM Intellisense (如果不用)

**预期效果**: 释放 500MB-800MB 内存

### 步骤2：禁用重型Language Servers

在 settings.json 添加：

```json
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": false
  },
  "[typescript]": {
    "editor.defaultFormatter": "vscode.typescript-language-features",
    "editor.formatOnSave": false
  },
  "python.analysis.typeCheckingMode": "off",
  "python.linting.enabled": false,
  "pylance.analysis.typeCheckingMode": "off",
  "typescript.tsserver.maxTsServerMemory": 1024,
  "[html]": {
    "editor.defaultFormatter": "vscode.html-language-features",
    "editor.formatOnSave": false
  }
}
```

**预期效果**: 释放 300MB-500MB 内存

### 步骤3：禁用Pylance（仅当Python不是主要语言时）

命令面板执行：
```
Extensions: Disable
```

选择 "Pylance"（但保留 ms-python.python）

**预期效果**: 释放 500MB 内存

### 步骤4：清理VSCode缓存

```bash
# 备份
cp -r ~/Library/Application\ Support/Code ~/vscode_backup_$(date +%s)

# 清理缓存
rm -rf ~/Library/Application\ Support/Code/CachedExtensionVSIXs/*
rm -rf ~/Library/Caches/com.microsoft.VSCode/*
rm -rf ~/.vscode/extensions/ms-python.*-darwin-arm64  # 清理旧版本

# 重启VSCode
```

**预期效果**: 释放 300MB-500MB 内存

## 🎯 预期优化结果

**优化前**:
- 内存占用: 19GB/24GB (79%)
- VSCode进程: 3.7GB
- 频繁卡顿: 是
- Swap使用: 频繁

**优化后（预期）**:
- 内存占用: 12-14GB/24GB (50-58%)
- VSCode进程: 1.5-2GB
- 频繁卡顿: 否
- Swap使用: 极少

## 📋 完整的优化版settings.json配置

将此内容添加到 `~/Library/Application Support/Code/User/settings.json`:

```json
{
  // 基础设置
  "editor.formatOnSave": false,
  "editor.formatOnPaste": false,
  "files.autoSave": "off",
  "window.zoomLevel": 0,
  
  // 性能优化
  "editor.largeFileOptimizations": true,
  "editor.wordBasedSuggestions": false,
  "editor.renderWhitespace": "none",
  "editor.minimap.enabled": false,
  
  // Python优化
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": false,
    "editor.codeActionsOnSave": {}
  },
  "python.analysis.typeCheckingMode": "off",
  "python.linting.enabled": false,
  "python.linting.pylintEnabled": false,
  "python.analysis.disabled": ["unresolutedImport"],
  
  // TypeScript优化
  "[typescript]": {
    "editor.defaultFormatter": "vscode.typescript-language-features",
    "editor.formatOnSave": false
  },
  "typescript.tsserver.maxTsServerMemory": 1024,
  "typescript.tsserver.useSeparateSyntacticServer": false,
  
  // HTML/CSS优化
  "[html]": {
    "editor.defaultFormatter": "vscode.html-language-features",
    "editor.formatOnSave": false
  },
  "[css]": {
    "editor.defaultFormatter": "vscode.css-language-features",
    "editor.formatOnSave": false
  },
  
  // 禁用不必要的功能
  "editor.hover.enabled": false,
  "editor.parameterHints.enabled": false,
  "editor.suggestOnTriggerCharacters": false,
  "search.followSymlinks": false,
  "search.useRipgrep": true,
  "search.ripgrep.args": ["--max-columns=1000"],
  
  // Git/Source Control
  "git.ignoreLimitWarning": true,
  "scm.diffDecorationsGutterWidth": 2,
  
  // 扩展相关
  "extensions.ignoreRecommendations": false,
  "extensions.showRecommendationsOnInstall": false,
  
  // 同步和遥测
  "settingsSync.keybindingsPerPlatform": false,
  "telemetry.telemetryLevel": "off"
}
```

## 🔍 如何监控优化效果

运行此命令持续监控内存：

```bash
# 监控VSCode内存（每2秒更新）
while true; do
  echo "=== $(date '+%H:%M:%S') ==="
  ps aux | grep -E "Code|Python|Node" | grep -v grep | awk '{print $2, $4, $11}' | head -5
  sleep 2
done
```

## ⚠️ 如果仍然卡顿

### 终极方案：创建轻量级配置文件

```bash
# 使用便携配置启动VSCode，完全隔离扩展
code --extensions-dir /tmp/vscode-extensions --user-data-dir /tmp/vscode-data ~/Desktop/Project/trustagency
```

### 检查是否有文件监控问题

```bash
# 检查项目中是否有巨大的node_modules或类似目录
du -sh ~/Desktop/Project/trustagency/* | sort -h

# 在.gitignore中添加node_modules等
echo "node_modules/" >> ~/.gitignore_global
echo "dist/" >> ~/.gitignore_global
```

## 🎓 预防措施

1. **每周检查插件** - 禁用未使用的插件
2. **定期清理缓存** - 每月执行步骤4
3. **监控内存** - 如果超过60%立即采取行动
4. **使用工作区设置** - 项目级別配置覆盖全局设置

## 📞 如果问题没有解决

可能的其他原因：
1. **node_modules过大** - 运行 `du -sh backend/node_modules frontend/node_modules`
2. **Git仓库过大** - 运行 `du -sh .git`
3. **IDE索引器卡死** - 重启VSCode
4. **某个后台进程** - 运行 `top` 查看

---

**预期完成时间**: 10分钟  
**预期效果**: 卡顿消失，内存占用下降30-40%
