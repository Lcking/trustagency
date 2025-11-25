# TrustAgency 代码审查流程

**版本**：1.0  
**发布日期**：2025-11-21  
**维护者**：架构团队

---

## 目录
1. [审查流程概述](#审查流程概述)
2. [PR 提交规范](#pr-提交规范)
3. [审查清单](#审查清单)
4. [常见问题检查](#常见问题检查)
5. [审查反馈模板](#审查反馈模板)
6. [变更日志](#变更日志)

---

## 审查流程概述

### 流程图

```
功能开发 → 本地测试 → 提交 PR → 自动检查 → 审查员审查 → 修改反馈 → 重新审查 → 合并到 dev
    ↓                                              ↓（通过）
所有通过                                      部署到生产
```

### 核心原则

1. **预防优于修复**：通过严格审查防止问题进入主分支
2. **知识分享**：代码审查是团队学习的机会
3. **持续改进**：审查反馈帮助团队改进代码质量
4. **双向尊重**：审查员和被审查员互相尊重

---

## PR 提交规范

### 规则 1.1：PR 标题格式

遵循 Conventional Commits 格式：

```
<type>(<scope>): <subject>
```

**类型**（必需）：
- `feat`：新功能
- `fix`：Bug 修复
- `docs`：文档
- `refactor`：代码重构
- `perf`：性能优化
- `test`：测试
- `chore`：构建、配置等

**示例**：
```
✅ 正确
- feat(admin): add website settings panel
- fix(api): resolve section loading timeout
- docs(readme): update installation instructions

❌ 错误
- update code
- 新增功能
- fixed stuff
- wip
```

---

### 规则 1.2：PR 描述模板

每个 PR 必须包含以下内容：

```markdown
## 功能描述
简述这个 PR 要实现的功能或修复的问题

## 修改内容
- 修改项 1
- 修改项 2
- 修改项 3

## 关联 Issue
Closes #123

## 测试结果
- [x] 本地测试通过
- [x] 集成测试通过
- [x] 没有 console 错误
- [x] 原有功能未被破坏

## 规范检查清单
- [x] 代码遵循编码规范
- [x] 脚本块数量 <= 2
- [x] HTML 标签平衡
- [x] API 使用规范
- [x] 数据库变更记录
- [x] 提交信息格式正确
```

---

### 规则 1.3：PR 创建前检查

在点击"Create Pull Request"前，必须完成：

**代码检查**：
```bash
# 1. 确保代码已 commit
git status  # 应该显示 working tree clean

# 2. 检查脚本块数量（前端）
grep -c "<script>" backend/site/admin/index.html
# 应该输出：2

# 3. 检查 HTML 标签平衡（前端）
echo "Open div: $(grep -o '<div' backend/site/admin/index.html | wc -l)"
echo "Close div: $(grep -o '</div>' backend/site/admin/index.html | wc -l)"
# 应该相同

# 4. 检查 console 错误（前端，需手动在浏览器检查）

# 5. 检查 commit 信息格式
git log --oneline -5  # 验证最后 5 条 commit 信息格式
```

**测试检查**：
```bash
# 运行所有测试
pytest tests/ -m integration -v

# 或手动测试（如果没有自动化测试）
# - 登录功能
# - 所有菜单项
# - 数据加载
# - 没有错误提示
```

**文件检查**：
```bash
# 确保没有遗漏的调试代码
git diff origin/dev  # 查看所有更改

# 查找可能的调试代码
grep -r "console.log" backend/site/admin/index.html
grep -r "print(" backend/app/
grep -r "TODO\|FIXME\|DEBUG" backend/site/admin/index.html
```

---

## 审查清单

### 审查员必须检查的项目

#### 1. 代码规范性（强制）
- [ ] 代码遵循 CODING_STANDARDS.md 规范
- [ ] 命名风格一致（camelCase/snake_case）
- [ ] 缩进和格式规范
- [ ] 没有硬编码的值
- [ ] 没有过长的函数（> 50 行考虑拆分）

**检查命令**：
```bash
# 查看完整的 diff
git diff origin/dev

# 检查特定文件的修改
git show HEAD:backend/site/admin/index.html | wc -l
```

---

#### 2. 脚本块完整性（强制 - 前端）
- [ ] 脚本块数量 <= 2 个
- [ ] 所有 `<script>` 都在 `</body>` 前
- [ ] 没有在 HTML 元素内插入脚本
- [ ] 没有 inline event handlers（onclick 等）

**检查命令**：
```bash
# 查找所有脚本块
grep -n "<script>" backend/site/admin/index.html

# 查找 inline event handlers
grep -n "onclick\|onchange\|onload" backend/site/admin/index.html
```

---

#### 3. HTML 结构完整性（强制 - 前端）
- [ ] div 开闭标签平衡
- [ ] 没有未闭合的标签
- [ ] 没有重复的 id 属性
- [ ] 语义化标签使用正确

**检查命令**：
```bash
# 计数 div 标签
open_div=$(grep -o '<div' backend/site/admin/index.html | wc -l)
close_div=$(grep -o '</div>' backend/site/admin/index.html | wc -l)
if [ "$open_div" -eq "$close_div" ]; then echo "✓ div 标签平衡"; else echo "✗ div 标签不平衡"; fi
```

---

#### 4. API 调用规范（强制）
- [ ] 使用 `authenticatedFetch()` 而非 `fetch()`
- [ ] API URL 使用 `getAPIUrl()` 函数
- [ ] 有适当的错误处理
- [ ] 返回值处理正确

**检查示例**：
```javascript
// ✅ 正确
const response = await authenticatedFetch(`${API_URL}/sections`);

// ❌ 错误
const response = await fetch('http://localhost:8001/api/sections');
```

---

#### 5. 数据库规范（强制 - 后端）
- [ ] 新模型放在 `models/` 目录
- [ ] 已更新 `database.py` 初始化函数
- [ ] 没有硬编码 SQL
- [ ] 使用 ORM 而非原始 SQL
- [ ] 有适当的关系定义

---

#### 6. 错误处理（强制）
- [ ] 所有 API 调用都有错误处理
- [ ] 错误信息有意义（不是通用的"Error"）
- [ ] 没有吞掉异常的 try-catch
- [ ] 有适当的日志记录

**前端示例**：
```javascript
try {
    const response = await authenticatedFetch(`${API_URL}/data`);
    if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
    }
    return await response.json();
} catch (error) {
    console.error('Failed to load data:', error);
    showNotification('数据加载失败，请重试', 'error');
}
```

---

#### 7. 功能完整性（可选）
- [ ] 新功能是否符合需求
- [ ] 是否有边界情况处理
- [ ] 是否有用户反馈（提示、加载状态等）
- [ ] 是否与现有功能冲突

---

#### 8. 测试覆盖（可选）
- [ ] 是否有单元测试
- [ ] 是否有集成测试
- [ ] 测试是否通过
- [ ] 测试覆盖率是否 > 80%

---

#### 9. 文档更新（可选）
- [ ] API 文档是否更新
- [ ] README 是否需要更新
- [ ] 变更是否需要记录在 CHANGELOG

---

#### 10. 性能影响（可选）
- [ ] 是否有性能下降
- [ ] 是否有内存泄漏风险
- [ ] 是否有无限循环或死锁风险
- [ ] 大量数据处理是否有优化

---

## 常见问题检查

### ❌ 常见问题 1：脚本块分割

**问题表现**：
```
ReferenceError: functionName is not defined
```

**检查方法**：
```bash
# 查看脚本块数量和位置
grep -n "<script>" backend/site/admin/index.html

# 如果有超过 2 个脚本块，或位置不对，则有问题
```

**审查反馈**：
```
❌ 脚本块分割问题
当前有 3 个脚本块，应该只有 2 个。
所有业务逻辑都应该在 </body> 前的主脚本块中。
请合并脚本块。

参考：CODING_STANDARDS.md 中的"脚本块管理"部分
```

---

### ❌ 常见问题 2：HTML 标签不平衡

**问题表现**：
```
浏览器渲染错误，页面布局混乱
```

**检查方法**：
```bash
# 数一下 div 标签
grep -o '<div' backend/site/admin/index.html | wc -l
grep -o '</div>' backend/site/admin/index.html | wc -l
# 不相等则有问题
```

**审查反馈**：
```
❌ HTML 标签不平衡
统计结果：
- 开标签：172
- 闭标签：171

缺少 1 个 </div>。请找到未闭合的 div 并修复。
```

---

### ❌ 常见问题 3：Inline Event Handler

**问题表现**：
```html
<button onclick="showSection('categories')">Categories</button>
```

**检查方法**：
```bash
grep -n "onclick\|onchange\|onload\|onsubmit" backend/site/admin/index.html
```

**审查反馈**：
```
❌ 使用了 inline event handler
第 245 行有 onclick="showSection(...)"

根据规范，应该使用事件委托：
- 在 HTML 中添加 data-* 属性
- 在脚本块中用 addEventListener 处理

参考：CODING_STANDARDS.md 中的"事件处理"部分
```

---

### ❌ 常见问题 4：直接 fetch 而非 authenticatedFetch

**问题表现**：
```javascript
fetch('http://localhost:8001/api/sections')  // ❌ 错误
```

**检查方法**：
```bash
grep -n "fetch(" backend/site/admin/index.html | grep -v "authenticatedFetch"
```

**审查反馈**：
```
❌ 直接使用 fetch 而非 authenticatedFetch
第 1234 行直接使用 fetch()。

应该使用 authenticatedFetch() 以便自动添加认证头。
修改为：
  const response = await authenticatedFetch(`${API_URL}/sections`);
```

---

### ❌ 常见问题 5：硬编码 API URL

**问题表现**：
```javascript
const url = 'http://localhost:8001/api/sections';  // ❌ 硬编码
```

**检查方法**：
```bash
grep -n "http://localhost" backend/site/admin/index.html
```

**审查反馈**：
```
❌ 硬编码了 API URL
第 567 行硬编码了 'http://localhost:8001/api/sections'

应该使用 getAPIUrl() 函数：
  const response = await authenticatedFetch(`${API_URL}/sections`);

这样可以根据不同环境自动调整 URL。
```

---

### ⚠️ 潜在问题 1：可能的性能问题

**审查反馈**：
```
⚠️ 潜在性能问题

第 1500-1520 行的循环中，在每次迭代时都调用了 DOM 查询。
可能会导致性能问题。

建议改进：
- 缓存 DOM 查询结果
- 使用事件委托而非为每个元素添加监听器
```

---

### ⚠️ 潜在问题 2：可能的内存泄漏

**审查反馈**：
```
⚠️ 可能的内存泄漏

第 800 行添加了事件监听器，但没有在卸载时移除。
如果多次加载页面，可能导致内存泄漏。

建议改进：
- 在清理函数中使用 removeEventListener()
- 或使用 { once: true } 选项确保只执行一次
```

---

## 审查反馈模板

### 模板 1：批准（APPROVED）

```markdown
✅ 代码审查通过

**优点**：
- 代码逻辑清晰，易于维护
- 测试覆盖完善
- 注释充分

**建议**（非阻止）：
- 可以考虑在第 123 行添加一条注释解释业务逻辑

**结论**：已批准合并
```

---

### 模板 2：请求更改（REQUEST CHANGES）

```markdown
🔴 需要修改后重新审查

**必须修复的问题**：
1. [ ] 脚本块数量超过 2 个（第 10 条规则）
2. [ ] HTML div 标签不平衡（第 10 条规则）
3. [ ] 使用了 inline event handlers（第 15 条规则）

**详细说明**：
- 第一个问题：在第 1500 行和 1600 行各有一个 <script>，应该合并到主脚本块中
- 第二个问题：缺少一个 </div> 标签，请检查第 800-850 行
- 第三个问题：第 245 行的 onclick 属性应该移至 JavaScript 中

**测试状态**：
- 本地测试：❌ 登录后所有菜单无响应
- 集成测试：❌ 未运行

**建议修改步骤**：
1. 合并所有脚本块到 </body> 前的主脚本块
2. 修复 HTML 标签平衡问题
3. 移除 inline event handlers
4. 重新运行测试确保没有问题
5. 回复此评论说明已修复

---

**结论**：拒绝合并，待修改后重新审查
```

---

### 模板 3：评论（COMMENT）

```markdown
💬 一些建议和观察

**建议项**（不阻止合并）：
1. 第 234 行的函数名 `handleClick` 可以改为 `handleSectionClick` 更清晰
2. 第 567 行的错误处理可以添加重试机制

**知识点分享**：
- 这里使用的事件委托模式很好，避免了为大量元素添加监听器

**后续可以考虑的优化**：
- 添加加载状态提示
- 添加错误重试机制

---

**结论**：代码质量不错，这些只是建议，可以考虑后续改进
```

---

## 变更日志

### v1.0 - 初始版本 (2025-11-21)
- 建立代码审查流程
- 定义审查清单
- 建立反馈模板
- 定义常见问题检查项

### 未来计划
- 建立自动化代码审查工具（如 SonarQube）
- 添加性能基准测试
- 建立安全审查清单

---

**签名**：架构团队  
**最后更新**：2025-11-21
