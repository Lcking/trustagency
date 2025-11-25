# ✅ 日常工作检查清单

**用途**: 每天开始开发工作前运行，防止系统出现意外问题

---

## 🔍 启动前检查 (5分钟)

```bash
#!/bin/bash
set -e

echo "🔍 TrustAgency 日常检查清单"
echo "=================================="

# 1. 检查git状态
echo "📌 [1/10] 检查Git状态..."
if [[ -n $(git status -s) ]]; then
    echo "⚠️  有未提交的更改:"
    git status -s | head -5
    read -p "是否先提交? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "checkpoint: 日常工作检查点"
    fi
fi
echo "✅ Git检查完成\n"

# 2. 检查数据库完整性
echo "📌 [2/10] 检查数据库完整性..."
SECTIONS=$(sqlite3 trustagency.db "SELECT COUNT(*) FROM sections")
CATEGORIES=$(sqlite3 trustagency.db "SELECT COUNT(*) FROM categories")
PLATFORMS=$(sqlite3 trustagency.db "SELECT COUNT(*) FROM platforms")
ARTICLES=$(sqlite3 trustagency.db "SELECT COUNT(*) FROM articles")

echo "  📊 栏目: $SECTIONS | 分类: $CATEGORIES | 平台: $PLATFORMS | 文章: $ARTICLES"

if [[ "$SECTIONS" -eq 0 ]]; then
    echo "❌ 栏目数为0，数据可能损坏!"
    echo "🔧 尝试恢复..."
    python3 << 'EOF'
import sqlite3
from datetime import datetime
conn = sqlite3.connect('trustagency.db')
c = conn.cursor()

# 检查是否有备份
import glob
backups = sorted(glob.glob('backups/baseline_*.db'))
if backups:
    latest_backup = backups[-1]
    print(f"找到备份: {latest_backup}")
    import shutil
    shutil.copy(latest_backup, f"trustagency.db.recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy(latest_backup, 'trustagency.db')
    print("✅ 已从备份恢复数据库")
else:
    print("❌ 没有找到备份文件")
EOF
    exit 1
fi
echo "✅ 数据库完整性检查通过\n"

# 3. 检查后端进程
echo "📌 [3/10] 检查后端服务..."
if pgrep -f "uvicorn.*app.main" > /dev/null; then
    echo "✅ 后端已运行"
else
    echo "⚠️  后端未运行，建议启动:"
    echo "    bash /Users/ck/Desktop/Project/trustagency/start-backend-simple.sh"
fi
echo

# 4. 检查前端文件
echo "📌 [4/10] 检查前端文件..."
HTML_LINES=$(wc -l < backend/site/admin/index.html)
echo "  📄 HTML文件: $HTML_LINES 行"

if [[ $HTML_LINES -lt 1400 ]]; then
    echo "❌ HTML文件可能被损坏 (应该 > 4000行)"
    echo "🔧 尝试恢复..."
    git show HEAD~1:backend/site/admin/index.html > backend/site/admin/index.html.recovery
    echo "✅ 已保存恢复版本为 index.html.recovery"
    exit 1
fi
echo "✅ 前端文件完整\n"

# 5. 检查JavaScript模块
echo "📌 [5/10] 检查模块文件..."
MODULES_COUNT=$(find backend/site/admin/js -name "*.js" 2>/dev/null | wc -l)
echo "  📦 模块数量: $MODULES_COUNT"

if [[ $MODULES_COUNT -lt 5 ]]; then
    echo "⚠️  模块数量较少，可能遗失文件"
fi
echo "✅ 模块检查完成\n"

# 6. 检查系统资源
echo "📌 [6/10] 检查系统资源..."
MEM_USAGE=$(ps aux | grep -E "Code|Chrome|python" | awk '{print $6}' | awk '{sum+=$1} END {print sum/1024 " MB"}')
echo "  💾 进程内存占用: $MEM_USAGE"

DISK_USAGE=$(du -sh . | cut -f1)
echo "  💿 项目磁盘占用: $DISK_USAGE"
echo "✅ 资源检查完成\n"

# 7. 检查备份
echo "📌 [7/10] 检查备份..."
BACKUP_COUNT=$(ls backups/*.db 2>/dev/null | wc -l)
echo "  🗂️  备份文件数: $BACKUP_COUNT"

if [[ $BACKUP_COUNT -lt 3 ]]; then
    echo "⚠️  备份文件不足，建议创建新备份:"
    echo "    cp trustagency.db backups/backup_$(date +%Y%m%d_%H%M%S).db"
fi
echo "✅ 备份检查完成\n"

# 8. 检查日志
echo "📌 [8/10] 检查日志..."
if [[ -f "/tmp/backend.log" ]]; then
    ERRORS=$(grep -i "error\|exception" /tmp/backend.log | wc -l)
    WARNINGS=$(grep -i "warning" /tmp/backend.log | wc -l)
    echo "  📝 错误数: $ERRORS | 警告数: $WARNINGS"
    
    if [[ $ERRORS -gt 5 ]]; then
        echo "⚠️  错误较多，检查最近10行:"
        tail -10 /tmp/backend.log | grep -i "error\|exception"
    fi
fi
echo "✅ 日志检查完成\n"

# 9. 检查最后提交
echo "📌 [9/10] 检查最后提交..."
LAST_COMMIT=$(git log -1 --pretty=format:"%h - %s (%ai)")
echo "  🔄 最后提交: $LAST_COMMIT"

DAYS_SINCE=$(git log -1 --pretty=format:"%aI" | xargs -I {} date -j -f "%Y-%m-%dT%H:%M:%S%z" {} +%s | xargs -I {} echo $(($(date +%s) - {})) | awk '{print int($1 / 86400)}')
if [[ $DAYS_SINCE -gt 7 ]]; then
    echo "⚠️  7天内没有提交"
fi
echo "✅ 提交检查完成\n"

# 10. 最终总结
echo "📌 [10/10] 检查总结..."
echo "✅ 所有检查完成!"
echo ""
echo "📋 建议:"
echo "   1. 如果有任何警告，请立即处理"
echo "   2. 定期创建备份"
echo "   3. 监控后端日志"
echo ""
echo "🚀 现在可以开始工作了!"
```

---

## 🛡️ 开发过程中的检查点

### 每次修改代码后
```bash
# 1. 检查语法
python3 -m py_compile backend/app/*.py

# 2. 验证数据库
sqlite3 trustagency.db ".integrity_check"

# 3. 运行测试
python3 -m pytest tests/ -v --tb=short
```

### 每次修改前端后
```bash
# 1. 验证HTML
npm run validate-html  # 需要设置

# 2. 清除浏览器缓存
# Ctrl+Shift+Del (Windows/Linux) 或 Cmd+Shift+Delete (Mac)

# 3. 硬刷新
# Ctrl+F5 (Windows/Linux) 或 Cmd+Shift+R (Mac)
```

### 每天结束前
```bash
# 1. 创建每日备份
cp trustagency.db "backups/daily_$(date +%Y%m%d).db"

# 2. 提交代码
git add .
git commit -m "checkpoint: 每日工作完成 - $(date +%Y%m%d)"

# 3. 推送到GitHub
git push origin refactor/admin-panel-phase4

# 4. 生成状态报告
cat << EOF
📊 今日工作总结
================
工作时长: ?
提交数: $(git log --oneline --since="24 hours ago" | wc -l)
代码行数变化: $(git diff HEAD~1 --shortstat)
问题数: ?
EOF
```

---

## 🆘 应急处理流程

### 如果系统卡顿
```bash
# 1. 停止所有进程
pkill -f uvicorn
pkill -f python

# 2. 等待5秒
sleep 5

# 3. 检查资源
ps aux | grep -E "python|node" | head -5

# 4. 重启后端
bash start-backend-simple.sh
```

### 如果数据库出错
```bash
# 1. 立即备份当前版本
cp trustagency.db "trustagency.db.broken_$(date +%s)"

# 2. 尝试修复
sqlite3 trustagency.db "PRAGMA integrity_check;"

# 3. 如果无法修复，从备份恢复
cp backups/baseline_*.db trustagency.db
```

### 如果前端不响应
```bash
# 1. 检查HTML文件大小
wc -l backend/site/admin/index.html

# 2. 如果太小 (< 2000行)，从git恢复
git checkout backend/site/admin/index.html

# 3. 硬刷新浏览器
# Cmd+Shift+R (Mac)

# 4. 检查浏览器控制台是否有错误
# F12 → Console
```

---

## 📊 性能基准线

开发过程中使用这些数值作为参考，如果超过即可能出现问题:

```
内存占用:
  ✅ 正常: 100-300 MB
  ⚠️  警告: 300-500 MB
  ❌ 严重: > 500 MB

后端响应时间:
  ✅ 正常: < 500ms
  ⚠️  警告: 500ms-1s
  ❌ 严重: > 1s

数据库大小:
  ✅ 正常: < 100 MB
  ⚠️  警告: 100-200 MB
  ❌ 严重: > 200 MB

前端加载:
  ✅ 正常: < 3s
  ⚠️  警告: 3-5s
  ❌ 严重: > 5s
```

---

## 🔗 快速命令速查表

```bash
# 启动系统
bash start-backend-simple.sh
open http://localhost:8001/admin/

# 查看后端日志
tail -f /tmp/backend.log

# 查看数据库
sqlite3 trustagency.db ".mode column" "SELECT * FROM sections;"

# 运行单元测试
python3 -m pytest tests/ -v

# 创建备份
cp trustagency.db "backups/backup_$(date +%Y%m%d_%H%M%S).db"

# 恢复备份
cp backups/baseline_20251123.db trustagency.db

# 提交代码
git add . && git commit -m "your message"

# 查看日志
git log --oneline -10

# 查看差异
git diff HEAD~1

# 强制推送
git push origin refactor/admin-panel-phase4 -f
```

---

**记住**: 好的习惯能防止90%的问题。每次修改前检查，每次修改后验证，这是成功的秘诀。✨

