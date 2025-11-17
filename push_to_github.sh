#!/bin/bash

# 上传项目到 GitHub 的 Shell 脚本

PROJECT_DIR="/Users/ck/Desktop/Project/trustagency"
cd "$PROJECT_DIR"

echo "========================================"
echo "📦 GitHub 上传脚本"
echo "========================================"
echo ""

# 1. 检查 Git 状态
echo "1️⃣ 检查 Git 状态..."
git status --short

# 2. 添加所有更改
echo ""
echo "2️⃣ 添加所有更改..."
git add -A
echo "✅ 文件已添加"

# 3. 创建提交
echo ""
echo "3️⃣ 创建提交..."
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "chore: 完备的程序版本及当前更改 ($TIMESTAMP)"

# 4. 推送到 GitHub
echo ""
echo "4️⃣ 推送到 GitHub..."
git push origin main 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 上传成功！"
else
    echo ""
    echo "⚠️ 尝试推送 master 分支..."
    git push origin master 2>&1
fi

# 5. 显示最近的提交
echo ""
echo "5️⃣ 最近的提交:"
git log --oneline -5

echo ""
echo "========================================"
echo "✅ 完成！"
echo "========================================"
echo ""
echo "📍 GitHub 仓库: https://github.com/Lcking/trustagency"
