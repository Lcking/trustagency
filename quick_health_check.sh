#!/bin/bash

echo "🔍 快速系统检查"
echo "==============="

# 1. 数据库
SECTIONS=$(sqlite3 trustagency.db "SELECT COUNT(*) FROM sections" 2>/dev/null || echo "0")
echo "✅ 数据库: 栏目=$SECTIONS"

# 2. 后端
if pgrep -f "uvicorn.*app.main" > /dev/null; then
    echo "✅ 后端: 运行中"
else
    echo "⚠️  后端: 未运行"
fi

# 3. 前端
if [[ -f "backend/site/admin/index.html" ]]; then
    LINES=$(wc -l < backend/site/admin/index.html)
    echo "✅ 前端: HTML=$LINES 行"
else
    echo "❌ 前端: HTML 缺失"
fi

# 4. Git
if [[ -z $(git status -s 2>/dev/null) ]]; then
    echo "✅ Git: 工作区干净"
else
    echo "⚠️  Git: 有未提交更改"
fi

echo "==============="
echo "✅ 系统检查完成"
