#!/bin/bash

# ============================================================================
# Task 5.1.2: 前端资源加载优化
# 用途: 分析前端资源加载性能并提出优化建议
# ============================================================================

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║       Task 5.1.2: 前端资源加载优化 - 性能分析脚本                    ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

FRONTEND_FILE="backend/site/admin/index.html"
REPORT_FILE="RESOURCE_OPTIMIZATION_REPORT_$(date +%Y%m%d_%H%M%S).md"

# 分析前端文件
echo "📊 分析前端资源..."
echo ""

# 统计资源引用
SCRIPT_COUNT=$(grep -c '<script' "$FRONTEND_FILE" || echo "0")
STYLE_COUNT=$(grep -c '<link.*rel="stylesheet"' "$FRONTEND_FILE" || echo "0")
IMG_COUNT=$(grep -c '<img' "$FRONTEND_FILE" || echo "0")
CDN_COUNT=$(grep -c 'https://' "$FRONTEND_FILE" || echo "0")

echo "📈 资源统计:"
echo "   • 脚本标签: $SCRIPT_COUNT"
echo "   • 样式链接: $STYLE_COUNT"
echo "   • 图片标签: $IMG_COUNT"
echo "   • CDN 引用: $CDN_COUNT"
echo ""

# 检查前端文件大小
FILE_SIZE=$(du -h "$FRONTEND_FILE" | cut -f1)
LINE_COUNT=$(wc -l < "$FRONTEND_FILE")

echo "📊 文件指标:"
echo "   • 文件大小: $FILE_SIZE"
echo "   • 代码行数: $LINE_COUNT"
echo ""

# 检查缓存破坏器
CACHE_BUSTERS=$(grep -o 'v=[0-9]*' "$FRONTEND_FILE" | sort | uniq | wc -l)
echo "🔄 缓存管理:"
echo "   • 缓存破坏器版本数: $CACHE_BUSTERS"
echo ""

# 生成优化建议报告
cat > "$REPORT_FILE" << EOF
# 📋 前端资源加载优化报告 - Task 5.1.2

**生成时间**: $(date "+%Y-%m-%d %H:%M:%S")
**分析文件**: $FRONTEND_FILE

---

## 📊 当前资源统计

| 指标 | 数值 | 状态 |
|------|------|------|
| 脚本标签 | $SCRIPT_COUNT | $([ $SCRIPT_COUNT -gt 10 ] && echo "⚠️  过多" || echo "✅ 正常") |
| 样式链接 | $STYLE_COUNT | ✅ |
| 图片标签 | $IMG_COUNT | ✅ |
| CDN 引用 | $CDN_COUNT | $([ $CDN_COUNT -gt 5 ] && echo "⚠️  过多" || echo "✅ 正常") |
| 文件大小 | $FILE_SIZE | $([ ${FILE_SIZE%K} -gt 200 ] && echo "⚠️  较大" || echo "✅ 正常") |
| 代码行数 | $LINE_COUNT | $([ $LINE_COUNT -gt 3000 ] && echo "⚠️  需优化" || echo "✅ 正常") |

---

## 🎯 优化建议

### 1️⃣ 资源预加载 (优先级: 🔴 高)
\`\`\`html
<!-- 在 <head> 中添加预加载 -->
<link rel="preload" as="script" href="admin.js?v=1">
<link rel="preload" as="style" href="admin.css?v=1">
<link rel="prefetch" href="modal.js?v=1">
\`\`\`

**预期效果**: 减少首屏加载时间 10-20%

### 2️⃣ 延迟加载非关键脚本 (优先级: 🟠 中)
\`\`\`html
<!-- 为非关键脚本添加 defer -->
<script defer src="analytics.js"></script>
<script defer src="error-tracking.js"></script>
\`\`\`

**预期效果**: 减少首屏阻塞时间 5-10%

### 3️⃣ 合并和压缩资源 (优先级: 🟠 中)
- 考虑合并多个小脚本为一个
- 使用 gzip 压缩 JavaScript 和 CSS
- 移除未使用的代码

**预期效果**: 减少资源体积 20-30%

### 4️⃣ 图片优化 (优先级: 🟢 低)
- 使用 WebP 格式代替 PNG/JPG
- 实现图片懒加载
- 优化图片尺寸

**预期效果**: 减少图片加载时间 30-50%

### 5️⃣ 缓存策略优化 (优先级: 🔴 高)
- 统一缓存破坏器版本管理
- 实现长期缓存策略
- 分离应用代码和库代码

**预期效果**: 减少重复加载时间 50%+

---

## 📈 性能基准线

### 当前状态
- 首屏加载时间: 待测试 (目标: < 3秒)
- 资源加载时间: 待测试
- 文件传输大小: $FILE_SIZE

### 优化后预期
- 首屏加载时间: < 2 秒 (降低 30%+)
- 资源加载时间: < 1.5 秒 (降低 40%+)
- 文件传输大小: < 150KB (降低 20%+)

---

## ✅ 优化清单

### 立即实施 (本周)
- [ ] 添加关键资源预加载
- [ ] 为非关键脚本添加 defer 属性
- [ ] 统一缓存破坏器版本

### 短期优化 (本月)
- [ ] 合并小脚本文件
- [ ] 压缩资源大小
- [ ] 实现图片懒加载

### 长期规划 (下月)
- [ ] 升级到现代前端框架
- [ ] 实现服务端渲染 (SSR)
- [ ] 配置 CDN 加速

---

## 🔧 实施步骤

### Step 1: 添加预加载 (5分钟)
编辑 $FRONTEND_FILE，在 <head> 中添加:
\`\`\`html
<link rel="preload" as="script" href="admin.js?v=1">
<link rel="prefetch" href="modal.js?v=1">
\`\`\`

### Step 2: 添加 defer 属性 (10分钟)
为非关键脚本添加 defer 属性

### Step 3: 测试验证 (15分钟)
\`\`\`bash
# 打开浏览器开发者工具 → Network 标签
# 清空缓存后重新加载
# 对比优化前后的加载时间
\`\`\`

### Step 4: 性能测试 (20分钟)
使用 Lighthouse 或 WebPageTest 进行性能测试

---

## 📊 验收标准

- [ ] 首屏加载时间 < 3 秒
- [ ] 最大内容绘制 (LCP) < 2.5 秒
- [ ] 首次输入延迟 (FID) < 100ms
- [ ] 累积布局偏移 (CLS) < 0.1

---

## 💡 额外优化建议

1. **启用 HTTP/2** - 提升资源并行加载能力
2. **使用 Service Worker** - 实现离线缓存
3. **压缩传输** - 使用 Brotli 代替 Gzip
4. **资源提示** - 使用 dns-prefetch, preconnect 等

---

## 📝 参考资源

- [MDN: Web Performance](https://developer.mozilla.org/en-US/docs/Web/Performance)
- [Google: Web Vitals](https://web.dev/vitals/)
- [Chrome DevTools Performance Guide](https://developer.chrome.com/docs/devtools/performance/)

---

**状态**: 📝 等待实施

EOF

echo "✅ 优化报告已生成: $REPORT_FILE"
echo ""
echo "📍 关键改进点:"
echo "   1. 添加资源预加载"
echo "   2. 使用 defer 延迟加载"
echo "   3. 合并缓存管理"
echo "   4. 优化文件大小"
echo ""
echo "🎯 目标: 首屏加载时间 < 3 秒"
echo ""
