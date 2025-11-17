#!/usr/bin/env bash
# 前后端集成验收测试清单

echo "=========================================="
echo "前后端文章链接集成验收测试"
echo "=========================================="
echo ""

# 测试用例
TEST_CASES=()

# 1. API 端点测试
echo "📋 测试 1: 验证后端 API 端点"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "1.1 测试 GET /api/articles/by-section/wiki"
curl -s http://localhost:8000/api/articles/by-section/wiki?limit=5 | python3 -m json.tool | head -50

echo ""
echo "1.2 测试 GET /api/articles/by-section/faq"
curl -s http://localhost:8000/api/articles/by-section/faq?limit=5 | python3 -m json.tool | head -50

echo ""
echo "1.3 测试 GET /api/articles/by-section/guide"
curl -s http://localhost:8000/api/articles/by-section/guide?limit=5 | python3 -m json.tool | head -50

echo ""
echo "=========================================="
echo "✅ API 端点测试完成"
echo "=========================================="

echo ""
echo "📋 测试 2: 前端页面验证（需要在浏览器中手动验证）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "请在浏览器中验证以下步骤："
echo ""
echo "2.1 Wiki 页面:"
echo "  - 打开: http://localhost:8000/wiki/"
echo "  - 预期: 显示动态加载的百科文章"
echo "  - 验证: 点击文章卡片，应链接到 /article/{slug}"
echo ""
echo "2.2 常见问题页面:"
echo "  - 打开: http://localhost:8000/qa/"
echo "  - 预期: 显示动态加载的常见问题"
echo "  - 验证: 点击文章链接，应打开 /article/{slug}"
echo ""
echo "2.3 指南页面:"
echo "  - 打开: http://localhost:8000/guides/"
echo "  - 预期: 支持动态加载指南文章"
echo "  - 验证: 浏览器控制台应显示加载成功日志"
echo ""

echo "=========================================="
echo "📋 测试 3: 数据库验证"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查数据库中的文章
echo ""
echo "3.1 检查 wiki 栏目文章数:"
python3 << 'EOF'
import sqlite3
con = sqlite3.connect('backend/trustagency.db')
cur = con.cursor()
cur.execute("""
SELECT COUNT(*) FROM articles a
WHERE a.section_id = (SELECT id FROM sections WHERE slug = 'wiki')
AND a.is_published = 1
""")
count = cur.fetchone()[0]
print(f"  Wiki 栏目已发布文章: {count} 篇")
con.close()
EOF

echo ""
echo "3.2 检查 faq 栏目文章数:"
python3 << 'EOF'
import sqlite3
con = sqlite3.connect('backend/trustagency.db')
cur = con.cursor()
cur.execute("""
SELECT COUNT(*) FROM articles a
WHERE a.section_id = (SELECT id FROM sections WHERE slug = 'faq')
AND a.is_published = 1
""")
count = cur.fetchone()[0]
print(f"  FAQ 栏目已发布文章: {count} 篇")
con.close()
EOF

echo ""
echo "=========================================="
echo "📋 测试 4: 浏览器控制台验证"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "在浏览器中打开各页面并按 F12 查看控制台 (Console 标签):"
echo ""
echo "4.1 Wiki 页面 (http://localhost:8000/wiki/):"
echo "  - 应显示: ✅ 成功加载 X 篇百科文章"
echo "  - 或显示: 后端加载失败，使用静态数据 (如果后端 API 无响应)"
echo ""
echo "4.2 FAQ 页面 (http://localhost:8000/qa/):"
echo "  - 应显示: ✅ 成功加载 X 篇常见问题文章"
echo ""
echo "4.3 Guides 页面 (http://localhost:8000/guides/):"
echo "  - 应显示: ✅ 成功加载 X 篇指南文章 (或类似消息)"
echo ""

echo "=========================================="
echo "✅ 测试清单完成！"
echo "=========================================="

echo ""
echo "📌 关键检查点："
echo "  ✓ API 端点返回正确的数据"
echo "  ✓ 前端页面显示来自后端的文章"
echo "  ✓ 文章链接指向 /article/{slug}"
echo "  ✓ 没有控制台错误"
echo "  ✓ 后端不可用时使用本地数据备份"
echo ""
