#!/bin/bash

# ========================================
# GitHub 推送前部署检查清单
# ========================================
# 这个脚本检查所有生产部署的先决条件

set -e

echo "🚀 TrustAgency 部署前检查清单"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数
PASSED=0
FAILED=0

# 辅助函数
check_item() {
    local description=$1
    local command=$2
    
    echo -n "📋 检查: $description ... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 通过${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ 失败${NC}"
        ((FAILED++))
    fi
}

check_file() {
    local description=$1
    local filepath=$2
    
    echo -n "📋 检查文件: $description ($filepath) ... "
    
    if [ -f "$filepath" ]; then
        echo -e "${GREEN}✅ 存在${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ 缺失${NC}"
        ((FAILED++))
    fi
}

# ==================== 代码质量检查 ====================
echo ""
echo "👨‍💻 代码质量检查"
echo "---------"

# 检查 .env 文件不在 Git 中
check_item ".env 不在版本控制中" "! git ls-files | grep -q '^.env$'"

# 检查 .gitignore 包含 .env
check_item ".gitignore 包含 .env" "grep -q '^\\.env$' .gitignore"

# 检查是否有硬编码的本地路径
check_item "代码中没有硬编码的本地路径" "! grep -r '/Users/ck/Desktop' backend/app || exit 0"

# 检查是否有硬编码的 API 密钥
check_item "代码中没有 OpenAI API 密钥" "! grep -r 'sk-' backend/app || exit 0"

# ==================== 配置文件检查 ====================
echo ""
echo "⚙️  配置文件检查"
echo "---------"

check_file ".env.example 存在" "backend/.env.example"
check_file "docker-compose.prod.yml 存在" "docker-compose.prod.yml"
check_file ".gitignore 存在" ".gitignore"

# 检查 .env.example 不包含敏感值
check_item ".env.example 不含敏感密钥" "! grep -i 'password' backend/.env.example"

# ==================== Docker 配置检查 ====================
echo ""
echo "🐳 Docker 配置检查"
echo "---------"

check_file "Dockerfile 存在（后端）" "backend/Dockerfile"
check_item "docker-compose.prod.yml 格式有效" "docker-compose -f docker-compose.prod.yml config > /dev/null"

# ==================== 依赖检查 ====================
echo ""
echo "📦 依赖检查"
echo "---------"

check_file "requirements.txt 存在" "backend/requirements.txt"

# 检查 requirements.txt 是否有版本固定
check_item "requirements.txt 有版本固定" "grep -q '==' backend/requirements.txt"

# ==================== 数据库检查 ====================
echo ""
echo "🗄️  数据库配置检查"
echo "---------"

# 检查是否有迁移脚本
if [ -d "backend/migrations" ]; then
    echo -n "📋 检查: Alembic 迁移脚本 ... "
    echo -e "${GREEN}✅ 存在${NC}"
    ((PASSED++))
else
    echo -n "📋 检查: Alembic 迁移脚本 ... "
    echo -e "${YELLOW}⚠️  缺失（可选）${NC}"
fi

# ==================== 文档检查 ====================
echo ""
echo "📚 文档检查"
echo "---------"

check_file "生产部署指南" "PRODUCTION_DEPLOYMENT_GUIDE.md"
check_file "README.md" "README.md"

# ==================== 安全检查 ====================
echo ""
echo "🔒 安全检查"
echo "---------"

# 检查没有 .pem 或 .key 文件被提交
check_item "没有私钥文件被提交" "! git ls-files | grep -E '\\.pem$|\\.key$'"

# 检查 DEBUG 模式设置
check_item ".env.example 中 DEBUG=False" "grep -q 'DEBUG=False' backend/.env.example"

# ==================== Git 检查 ====================
echo ""
echo "🔄 Git 检查"
echo "---------"

# 检查是否在主分支
check_item "在 Git 仓库中" "git rev-parse --git-dir > /dev/null"

# 检查是否有未 staged 的更改
check_item "没有未 staged 的关键文件更改" "! git diff backend/app/main.py | grep -q '^+.*DATABASE_URL' || exit 0"

# ==================== 最终总结 ====================
echo ""
echo "================================"
echo "检查结果总结"
echo "================================"
echo -e "✅ 通过: ${GREEN}$PASSED${NC}"
echo -e "❌ 失败: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有检查通过！可以安全地推送到 GitHub！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  有 $FAILED 项检查失败，请在推送前修复！${NC}"
    exit 1
fi
