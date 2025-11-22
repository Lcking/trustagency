# 🚀 TrustAgency 项目 - 质量保证体系快速导航

**最后更新**：2025-11-21  
**状态**：✅ 已建立完整的质量保证体系

---

## 📌 快速开始（针对所有开发者）

### 👨‍💻 我是新开发者，刚加入项目
1. 第一天必读：`CODING_STANDARDS.md` （30分钟）
2. 阅读流程：`PROJECT_QUALITY_SYSTEM.md`（20分钟）
3. 理解历史：`ROOT_CAUSE_ANALYSIS.md`（了解为什么需要这些规范）
4. 提交第一个 PR：参考 `CODE_REVIEW_PROCESS.md` 的"PR 提交规范"

### 👨‍💻 我要写代码
1. 打开 `CODING_STANDARDS.md`
2. 找到相应语言的规范部分
3. 开始编码前，记住三个强制规则：
   - ❌ 脚本块最多 2 个（前端）
   - ❌ HTML 标签要平衡（前端）
   - ❌ 所有 fetch 必须用 authenticatedFetch（前端）

### 👀 我要审查 PR
1. 打开 `CODE_REVIEW_PROCESS.md`
2. 使用"审查清单"中的 10 个检查点
3. 使用"审查反馈模板"提供反馈
4. 记住：前 6 项是强制规则，违反即拒绝

### 🧪 我要运行测试
1. 打开 `INTEGRATION_TESTS.md`
2. 运行集成测试：`pytest tests/ -m integration -v`
3. 生成覆盖率报告：`pytest tests/ --cov=backend --cov-report=html`

### 🎯 我要提交 PR
1. 完成编码和本地测试
2. 打开 `CODE_REVIEW_PROCESS.md` 的"PR 提交规范"
3. 按照模板填写 PR 信息
4. 在 PR 中包含"新功能开发检查清单"（来自 `CODING_STANDARDS.md`）
5. 等待审查

---

## 📚 文档体系介绍

### 🎯 核心文档（每个 PR 必读）

| 文档 | 用途 | 何时读 | 读多久 |
|------|------|--------|--------|
| **CODING_STANDARDS.md** | 编码规范 | 编码前 | 30分钟 |
| **CODE_REVIEW_PROCESS.md** | 审查流程 | 提交/审查 PR 前 | 20分钟 |
| **INTEGRATION_TESTS.md** | 测试指南 | 测试前 | 20分钟 |
| **PROJECT_QUALITY_SYSTEM.md** | 质量体系 | 第一周 | 30分钟 |

**总计**：2小时左右就能完全掌握

---

### 📖 补充文档（理解背景）

| 文档 | 用途 | 何时读 |
|------|------|--------|
| **ROOT_CAUSE_ANALYSIS.md** | 历史问题分析 | 理解为什么需要规范 |
| **DEVELOPMENT_PROCESS_REVIEW.md** | 开发流程评审 | 理解"打补丁"问题 |
| **QUALITY_SYSTEM_ESTABLISHED.md** | 建立总结 | 了解全景 |

---

## 🎯 重要规则速记

### 🚨 强制规则（违反即拒绝 PR）

#### 前端规范
```javascript
❌ 错误示例：
<script>
  function loginHandler() { ... }
</script>
<div>...</div>
<script>
  function showMenu() { ... }  // 多个脚本块
</script>

✅ 正确示例：
<div>...</div>
<script>
  // 所有代码在一个脚本块中
  function loginHandler() { ... }
  function showMenu() { ... }
</script>
```

#### API 调用
```javascript
❌ 错误：
fetch('http://localhost:8001/api/sections')

✅ 正确：
authenticatedFetch(`${API_URL}/sections`)
```

#### HTML 标签
```html
❌ 错误（开闭不平衡）：
<div id="container">
  <div id="item">...</div>
</div>  <!-- 只闭合了 1 个 div -->

✅ 正确：
<div id="container">
  <div id="item">...</div>
</div>  <!-- 闭合了 2 个 div -->
```

### ✅ 推荐规则（不符合时会被建议改进）

- 函数命名：camelCase (JS) / snake_case (Python)
- 错误处理：try-catch 中有有意义的错误信息
- 代码注释：复杂逻辑有解释性注释
- 测试覆盖：新增功能有相应测试

---

## 📋 常用命令速查

### 检查脚本块
```bash
# 查看脚本块数量和位置
grep -n "<script>" backend/site/admin/index.html

# 应该输出类似：
# 1347:<script>
# 4108:<script>  (最多这两个)
```

### 检查 HTML 标签平衡
```bash
# 统计开闭标签
open_divs=$(grep -o '<div' backend/site/admin/index.html | wc -l)
close_divs=$(grep -o '</div>' backend/site/admin/index.html | wc -l)
echo "Open: $open_divs, Close: $close_divs"

# 应该输出相同的数字
```

### 检查 inline event handlers
```bash
# 查找 onclick、onchange 等
grep -n "onclick\|onchange\|onload" backend/site/admin/index.html

# 如果输出为空，说明没有（这是好的）
```

### 运行集成测试
```bash
# 运行所有测试
pytest tests/ -m integration -v

# 运行特定测试
pytest tests/test_admin_login.py -v

# 生成 HTML 覆盖率报告
pytest tests/ --cov=backend --cov-report=html
```

---

## 🔄 典型工作流程

### 场景 1：添加新功能

```
1. 创建功能分支
   git checkout dev
   git checkout -b feature/new-feature-name

2. 编码（遵循 CODING_STANDARDS.md）

3. 本地测试
   pytest tests/ -m integration -v

4. 验证规范
   grep -c "<script>" backend/site/admin/index.html
   # 应该输出 2

5. 提交代码
   git add .
   git commit -m "feat(scope): add new feature"

6. 创建 PR
   - 标题：feat(scope): add new feature
   - 描述：填写完整信息
   - 检查清单：勾选所有项

7. 等待审查和测试

8. 根据反馈修改（如需要）

9. 合并到 dev
```

### 场景 2：修复 Bug

```
1. 创建修复分支
   git checkout dev
   git checkout -b bugfix/issue-description

2. 定位 bug（参考 ROOT_CAUSE_ANALYSIS.md 了解常见问题）

3. 修复并测试

4. 创建 PR（同上）

5. 审查员验证 bug 确实被修复

6. 合并到 dev
```

### 场景 3：紧急修复

```
1. 从 main 创建分支
   git checkout main
   git checkout -b hotfix/critical-bug

2. 快速修复

3. 测试

4. 创建 PR 到 main

5. 快速审查并合并

6. 同时合并回 dev 以保持同步
```

---

## ⚠️ 常见问题

### Q: 为什么脚本块最多 2 个？
A: 因为分割的脚本块会导致函数定义顺序混乱，容易出现"函数未定义"错误。这正是历史系统崩溃的根本原因。见 `ROOT_CAUSE_ANALYSIS.md`。

### Q: 如果违反了规范怎么办？
A: 审查员会指出问题，你修改后重新提交。这不是惩罚，而是学习的过程。

### Q: 新功能开发需要多长时间？
A: 相比之前的"打补丁"模式，现在每个功能会多花 30-60 分钟进行测试和审查。但长期来看，这节省了宝贵的调试时间和系统崩溃风险。

### Q: 我想快速部署一个功能，能跳过审查吗？
A: 不能。规范的流程就是为了防止历史上的"快速部署导致系统崩溃"问题。

### Q: 测试失败了怎么办？
A: 不要急着部署。根据测试错误信息修复代码，然后重新运行测试直到通过。

---

## 📞 需要帮助

### 我找不到某个信息
1. 查看本文档的"文档体系介绍"部分
2. 使用 Ctrl+F 在相应文档中搜索关键词
3. 如果仍未找到，联系技术委员会

### 我觉得某个规范不合理
1. 在 GitHub Issue 中描述你的想法
2. 在团队讨论中提出
3. 规范每个季度评审一次，会考虑所有反馈

### 我发现了系统漏洞
1. 如果与规范有关：更新相应规范文档
2. 记录到 `ISSUES_FOUND.md`（如有此文件）
3. 在下个季度的规范评审中讨论

---

## 🎓 深度学习路径

### 入门级（1天）
- [ ] CODING_STANDARDS.md
- [ ] PROJECT_QUALITY_SYSTEM.md 的"完整工作流程"

### 中级（1周）
- [ ] INTEGRATION_TESTS.md（运行所有例子）
- [ ] CODE_REVIEW_PROCESS.md（完整阅读）
- [ ] ROOT_CAUSE_ANALYSIS.md（理解历史）

### 高级（2周）
- [ ] DEVELOPMENT_PROCESS_REVIEW.md（深刻理解"打补丁"问题）
- [ ] 自己编写集成测试
- [ ] 作为审查员审查 3-5 个 PR

### 专家级（持续）
- [ ] 定期更新规范
- [ ] 指导新团队成员
- [ ] 优化测试流程
- [ ] 改进代码审查流程

---

## 📊 成功指标

### 短期（1-2 周）
- ✅ 所有新 PR 都遵循规范
- ✅ 代码审查时间从 30+ 分钟降低到 10-15 分钟
- ✅ 零规范违规被合并到 main

### 中期（1-2 个月）
- ✅ 集成测试覆盖率 > 90%
- ✅ Bug 发现时间从"部署后"前移到"审查阶段"
- ✅ 团队对规范的理解达成共识

### 长期（3-6 个月）
- ✅ 系统稳定性从 60% 提升到 99%+
- ✅ 开发效率反而提升（因为减少了调试时间）
- ✅ 技术债从积累转为偿还

---

## 📬 反馈和建议

**此文档最后更新于**：2025-11-21

如果你有任何建议或发现了问题，请：
1. 记录下来
2. 在团队讨论中提出
3. 我们会在下个季度的规范评审时讨论

---

**记住**：这些规范不是用来限制你，而是用来保护你和整个项目。  
每一条规则都来自于真实的问题和失败经验。  

**让我们一起构建一个稳定、可维护、高效的系统！** 🚀
