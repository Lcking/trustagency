#!/bin/bash

echo "🔍 开始验证侧边栏修改..."
echo ""

echo "=== 验证 guides/index.html ==="
echo "检查快速导航是否已删除..."
if grep -q "快速导航" /Users/ck/Desktop/Project/trustagency/site/guides/index.html; then
    echo "❌ 快速导航仍然存在!"
else
    echo "✅ 快速导航已删除"
fi

echo "检查专家建议是否已删除..."
if grep -q "专家建议" /Users/ck/Desktop/Project/trustagency/site/guides/index.html; then
    echo "❌ 专家建议仍然存在!"
else
    echo "✅ 专家建议已删除"
fi

echo "检查相关资源是否保留..."
if grep -q "相关资源" /Users/ck/Desktop/Project/trustagency/site/guides/index.html; then
    echo "✅ 相关资源已保留"
else
    echo "❌ 相关资源丢失!"
fi
echo ""

echo "=== 验证 beta-margin/index.html ==="
echo "检查快速信息是否已删除..."
if grep -q "快速信息" /Users/ck/Desktop/Project/trustagency/site/platforms/beta-margin/index.html; then
    echo "❌ 快速信息仍然存在!"
else
    echo "✅ 快速信息已删除"
fi

echo "检查准备好开始了吗是否已删除..."
if grep -q "准备好开始了吗" /Users/ck/Desktop/Project/trustagency/site/platforms/beta-margin/index.html; then
    echo "❌ CTA 卡片仍然存在!"
else
    echo "✅ CTA 卡片已删除"
fi

echo "检查相关资源是否保留..."
if grep -q "相关资源" /Users/ck/Desktop/Project/trustagency/site/platforms/beta-margin/index.html; then
    echo "✅ 相关资源已保留"
else
    echo "❌ 相关资源丢失!"
fi
echo ""

echo "=== 验证 gamma-trader/index.html ==="
echo "检查新手资源是否保留..."
if grep -q "新手资源" /Users/ck/Desktop/Project/trustagency/site/platforms/gamma-trader/index.html; then
    echo "✅ 新手资源已保留"
else
    echo "❌ 新手资源丢失!"
fi

echo "检查快速信息是否已删除..."
if grep -q "快速信息" /Users/ck/Desktop/Project/trustagency/site/platforms/gamma-trader/index.html; then
    echo "❌ 快速信息仍然存在!"
else
    echo "✅ 快速信息已删除"
fi

echo "检查为什么推荐是否已删除..."
if grep -q "为什么推荐" /Users/ck/Desktop/Project/trustagency/site/platforms/gamma-trader/index.html; then
    echo "❌ 为什么推荐仍然存在!"
else
    echo "✅ 为什么推荐已删除"
fi
echo ""

echo "=== 验证 sticky-top 和 max-height ==="
sidebar_count=$(grep -r "sticky-top.*max-height" /Users/ck/Desktop/Project/trustagency/site/ | grep -v "navbar" | wc -l)
if [ "$sidebar_count" -eq 0 ]; then
    echo "✅ 侧边栏卡片中已移除所有 sticky-top 和 max-height"
else
    echo "❌ 还有 $sidebar_count 个侧边栏卡片仍然有 sticky-top 和 max-height"
fi

echo ""
echo "🎉 验证完成!"
