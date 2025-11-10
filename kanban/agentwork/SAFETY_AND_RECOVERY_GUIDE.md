# 🛡️ 代码安全和恢复指南

## 概述
这份指南提供了机制来减少 AI 助手工作丢失、文件破坏等问题的影响。

---

## 📋 问题诊断

### 问题 1: 执行到一定程度卡死
**原因：**
- Token 上下文溢出（处理大文件时）
- VS Code AI 扩展超时
- 网络连接中断

**解决方案：**
1. **分解任务** - 每次修改不超过 50 行
2. **定期提交** - 每完成一个功能就 commit
3. **监控内存** - `top` 命令检查 VS Code 内存使用

### 问题 2: 重启后丢失工作成果
**原因：**
- VS Code 缓存被清除
- 对话历史没有保存
- 文件变更没有 commit

**解决方案：**
1. ✅ **启用自动保存** - 运行 `AUTO_SAVE_SCRIPT.sh`
2. ✅ **使用 Git commit** - 每次修改后立即 commit
3. ✅ **创建备份分支** - `git branch backup-$(date +%s)`

### 问题 3: 回溯代码时删除过多内容
**原因：**
- 使用 `replace_string_in_file` 时上下文不清晰
- 一次修改过多行导致误删
- 没有验证替换内容

**解决方案：**
1. ✅ **总是包含上下文** - 前后各 3-5 行
2. ✅ **小步骤修改** - 一次只改一个问题
3. ✅ **验证修改** - 使用 `git diff` 检查

---

## 🛠️ 最佳实践

### 1️⃣ 在开始任何修改前
```bash
# 创建备份分支
git branch backup-$(date +%Y%m%d-%H%M%S)

# 确保工作区干净
git status
```

### 2️⃣ 修改大文件时
```bash
# 分割成小文件（推荐）
# 不要在一个 3000+ 行文件中进行多个修改

# 或者分多个 commit
git add <file>
git commit -m "修复问题 A"
# ... 更多修改 ...
git commit -m "修复问题 B"
```

### 3️⃣ 修改前后
```bash
# 修改前：保存快照
git diff HEAD > before.patch

# 进行修改...

# 修改后：检查差异
git diff

# 如果有问题，立即恢复
git checkout -- <file>
# 或恢复到上一个 commit
git reset --hard HEAD~1
```

### 4️⃣ 启用自动保存
```bash
# 方式 1：后台运行（推荐）
nohup ./AUTO_SAVE_SCRIPT.sh > auto_save.log 2>&1 &

# 方式 2：查看进程
ps aux | grep AUTO_SAVE

# 方式 3：停止自动保存
pkill -f AUTO_SAVE_SCRIPT.sh
```

---

## 🔄 从故障恢复

### 场景 1: 意外删除了代码
```bash
# 查看所有分支
git branch -a

# 查看所有历史版本
git log --all --oneline | head -20

# 恢复到之前的版本
git checkout <commit-hash> -- <file>

# 或恢复整个分支
git checkout backup-<timestamp>
```

### 场景 2: 修改出错需要重做
```bash
# 查看最近 5 个 commit
git log --oneline -5

# 回到上一个良好状态
git reset --soft HEAD~1  # 保留更改，可以重新编辑
git reset --hard HEAD~1  # 完全抛弃最后一个 commit
```

### 场景 3: 文件被破坏
```bash
# 比较当前版本和上一个版本
git diff HEAD~1 <file>

# 显示文件的完整历史
git log -p --follow <file>

# 恢复到最后一个好版本
git checkout HEAD~1 -- <file>
git commit -m "恢复文件到正常状态"
```

---

## 📊 监控和验证

### 定期检查
```bash
# 查看未提交的更改
git status

# 查看本地分支
git branch -v

# 查看提交历史
git log --oneline --graph --all | head -20

# 统计代码行数
wc -l backend/site/admin/index.html
```

### 设置 Git 钩子（可选）
```bash
# 在 .git/hooks/pre-commit 中添加检查
# 防止提交大文件或有语法错误的文件

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# 检查文件大小
for file in $(git diff --cached --name-only); do
    size=$(git cat-file -s ":$file" 2>/dev/null || echo 0)
    if [ $size -gt 5242880 ]; then  # 5MB
        echo "❌ 文件过大: $file ($((size/1024/1024))MB)"
        exit 1
    fi
done
EOF

chmod +x .git/hooks/pre-commit
```

---

## 🎯 工作流建议

### 每日工作流
1. **早上启动**
   ```bash
   cd /Users/ck/Desktop/Project/trustagency
   nohup ./AUTO_SAVE_SCRIPT.sh > auto_save.log 2>&1 &
   git status
   ```

2. **工作期间**
   - 每完成一个小功能就 `git commit`
   - 修改大文件前创建备份分支
   - 定期查看 `git log` 确保有保存

3. **工作结束**
   ```bash
   # 最后一次提交
   git add -A
   git commit -m "end of day: 完成工作 - $(date)"
   
   # 停止自动保存
   pkill -f AUTO_SAVE_SCRIPT.sh
   
   # 推送到远程（如果有远程仓库）
   git push origin main
   ```

### 修改大文件时
1. 创建备份分支
2. 一次只修改 50-100 行
3. 修改后立即 commit
4. 在浏览器测试
5. 如果有问题，使用 `git diff` 检查或回滚

---

## 📞 紧急情况处理

### 如果 VS Code 崩溃
```bash
# 1. 强制保存所有更改
cd /Users/ck/Desktop/Project/trustagency
git add -A
git commit -m "emergency save - VS Code crash recovery"

# 2. 检查工作区是否有未保存的文件
git status

# 3. 重启 VS Code
# （所有 git 提交的内容会被保留）

# 4. 恢复工作
git log --oneline -5
```

### 如果 AI 助手连接断开
```bash
# 1. 快速提交当前更改
git add -A
git commit -m "checkpoint: AI连接中断时保存"

# 2. 启用自动保存以防再次断开
nohup ./AUTO_SAVE_SCRIPT.sh &

# 3. 继续工作
# 下次断开时已自动保存
```

---

## 📈 最终建议

| 问题 | 解决方案 | 优先级 |
|------|---------|--------|
| 卡死丢失 | ✅ 启用自动保存脚本 | 🔴 高 |
| 意外删除 | ✅ 创建备份分支 | 🔴 高 |
| 错误修改 | ✅ 每次修改前检查 git diff | 🟡 中 |
| 大文件问题 | ✅ 拆分文件或小步骤修改 | 🟡 中 |
| 文件破坏 | ✅ 建立 git 钩子检查 | 🟢 低 |

---

**记住：Git 是你的救生圈。常用 commit 和 branch，就不会丢失工作！**
