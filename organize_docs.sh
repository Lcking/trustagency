#!/bin/bash
# 将根目录的 MD 文件整理到 kanban/archives 文件夹

set -e

REPO_ROOT="/Users/ck/Desktop/Project/trustagency"
KANBAN_DIR="$REPO_ROOT/kanban"
ARCHIVE_DIR="$KANBAN_DIR/archives"

# 创建 archives 目录
mkdir -p "$ARCHIVE_DIR"

# 按类别创建子目录
mkdir -p "$ARCHIVE_DIR/tasks"           # 任务相关
mkdir -p "$ARCHIVE_DIR/sessions"        # 会话总结
mkdir -p "$ARCHIVE_DIR/bug_fixes"       # Bug 修复
mkdir -p "$ARCHIVE_DIR/deployments"     # 部署相关
mkdir -p "$ARCHIVE_DIR/verification"    # 验收和验证
mkdir -p "$ARCHIVE_DIR/frontend"        # 前端相关
mkdir -p "$ARCHIVE_DIR/backend"         # 后端相关
mkdir -p "$ARCHIVE_DIR/completion"      # 完成报告
mkdir -p "$ARCHIVE_DIR/misc"            # 其他杂项

# 定义文件分类函数
categorize_file() {
    local filename="$1"
    
    # 任务文件
    if [[ $filename =~ ^TASK_[0-9] ]]; then
        echo "tasks"
    # 会话总结
    elif [[ $filename =~ (SESSION|SUMMARY|PROGRESS|STATUS).*2025 ]]; then
        echo "sessions"
    # Bug 修复
    elif [[ $filename =~ (BUG|FIX|BUG_FIX) ]]; then
        echo "bug_fixes"
    # 部署
    elif [[ $filename =~ (DEPLOY|DOCKER|PORT|PRODUCTION|RESOURCE_ASSESSMENT) ]]; then
        echo "deployments"
    # 验收和验证
    elif [[ $filename =~ (ACCEPTANCE|VERIFICATION|VERIFY|CODE_REVIEW|VERIFICATION_REPORT) ]]; then
        echo "verification"
    # 前端
    elif [[ $filename =~ (FRONTEND|API_INTEGRATION|SEO|QUALITY_ISSUE|QUALITY_FIX|PLATFORM_LOADING) ]]; then
        echo "frontend"
    # 后端和集成
    elif [[ $filename =~ (INTEGRATION|BACKEND|SCHEMA) ]]; then
        echo "backend"
    # 完成报告
    elif [[ $filename =~ (COMPLETION|COMPLETE|DELIVERY|CERTIFICATE|PROJECT_FINAL|RELEASE_CHECKLIST) ]]; then
        echo "completion"
    # 其他
    else
        echo "misc"
    fi
}

# 遍历根目录的所有 MD 文件
cd "$REPO_ROOT"
count=0
for file in *.md; do
    if [ -f "$file" ]; then
        category=$(categorize_file "$file")
        target_dir="$ARCHIVE_DIR/$category"
        
        # 移动文件
        mv "$file" "$target_dir/"
        echo "✓ 已移动: $file → $category/"
        ((count++))
    fi
done

echo ""
echo "========================================="
echo "✅ 整理完成！共整理 $count 个文件"
echo "========================================="
echo ""
echo "新的文件结构："
tree -L 2 "$ARCHIVE_DIR" 2>/dev/null || find "$ARCHIVE_DIR" -type d | sort | sed 's|[^/]*/| |g'

echo ""
echo "统计："
for subdir in "$ARCHIVE_DIR"/*; do
    if [ -d "$subdir" ]; then
        count=$(find "$subdir" -maxdepth 1 -name "*.md" | wc -l)
        dirname=$(basename "$subdir")
        printf "  %-20s: %3d 个文件\n" "$dirname" "$count"
    fi
done

echo ""
echo "下次访问 kanban 文件夹查看所有文档！"
