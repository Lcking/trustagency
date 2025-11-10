# 数据库验收快照

**生成日期**: 2025年11月10日  
**备份类型**: Categories表数据导出  
**用途**: 防止分类数据丢失

---

## 📊 Categories表完整数据

### 导出日期/时间
```
2025-11-10 02:30:00 UTC
```

### 表结构
```sql
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    section_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY(section_id) REFERENCES sections(id)
);
```

### 完整数据记录

#### 栏目1: 常见问题 (FAQ)
```
id | section_id | name | sort_order | is_active
1  | 1          | 账户与安全 | 1 | true
2  | 1          | 交易相关 | 2 | true
3  | 1          | 提现充值 | 3 | true
4  | 1          | 技术问题 | 4 | true
5  | 1          | 其他问题 | 5 | true
```

#### 栏目2: 百科 (Wiki)
```
id | section_id | name | sort_order | is_active
6  | 2          | 区块链基础 | 1 | true
7  | 2          | 加密货币 | 2 | true
8  | 2          | 智能合约 | 3 | true
```

#### 栏目3: 指南 (Guide)
```
id | section_id | name | sort_order | is_active
9  | 3          | 交易指南 | 1 | true
10 | 3          | 投资策略 | 2 | true
11 | 3          | 工具使用 | 3 | true
12 | 3          | 风险管理 | 4 | true
```

#### 栏目4: 验证 (Review)
```
id | section_id | name | sort_order | is_active
13 | 4          | 项目评测 | 1 | true
14 | 4          | 安全审计 | 2 | true
15 | 4          | 用户评价 | 3 | true
```

---

## 📈 数据统计

### 分类数量统计
```
总分类数: 15
常见问题: 5个
百科: 3个
指南: 4个
验证: 3个
```

### 数据库检查
```sql
-- 检查所有分类
SELECT COUNT(*) FROM categories;
-- 预期结果: 15

-- 检查每个栏目的分类数
SELECT section_id, COUNT(*) 
FROM categories 
GROUP BY section_id;
-- 预期结果:
-- section_id=1: 5
-- section_id=2: 3
-- section_id=3: 4
-- section_id=4: 3

-- 检查sort_order完整性
SELECT COUNT(*) 
FROM categories 
WHERE sort_order IS NOT NULL;
-- 预期结果: 15 (全部设置)

-- 检查关联有效性
SELECT COUNT(*) 
FROM categories c
LEFT JOIN sections s ON c.section_id = s.id
WHERE s.id IS NULL;
-- 预期结果: 0 (无孤立分类)
```

---

## 🔄 数据恢复SQL脚本

### 完整INSERT语句
```sql
-- 常见问题分类
INSERT INTO categories (id, section_id, name, description, sort_order, is_active, created_at, updated_at) VALUES
(1, 1, '账户与安全', '测试分类 1', 1, 1, datetime('now'), datetime('now')),
(2, 1, '交易相关', '测试分类 2', 2, 1, datetime('now'), datetime('now')),
(3, 1, '提现充值', '测试分类 3', 3, 1, datetime('now'), datetime('now')),
(4, 1, '技术问题', '测试分类 4', 4, 1, datetime('now'), datetime('now')),
(5, 1, '其他问题', '测试分类 5', 5, 1, datetime('now'), datetime('now'));

-- 百科分类
INSERT INTO categories (id, section_id, name, description, sort_order, is_active, created_at, updated_at) VALUES
(6, 2, '区块链基础', '百科分类 1', 1, 1, datetime('now'), datetime('now')),
(7, 2, '加密货币', '百科分类 2', 2, 1, datetime('now'), datetime('now')),
(8, 2, '智能合约', '百科分类 3', 3, 1, datetime('now'), datetime('now'));

-- 指南分类
INSERT INTO categories (id, section_id, name, description, sort_order, is_active, created_at, updated_at) VALUES
(9, 3, '交易指南', '交易相关的详细指南', 1, 1, datetime('now'), datetime('now')),
(10, 3, '投资策略', '投资策略和风险管理', 2, 1, datetime('now'), datetime('now')),
(11, 3, '工具使用', 'API和工具的使用教程', 3, 1, datetime('now'), datetime('now')),
(12, 3, '风险管理', '风险管理最佳实践', 4, 1, datetime('now'), datetime('now'));

-- 验证分类
INSERT INTO categories (id, section_id, name, description, sort_order, is_active, created_at, updated_at) VALUES
(13, 4, '项目评测', '加密项目和平台评测', 1, 1, datetime('now'), datetime('now')),
(14, 4, '安全审计', '智能合约和系统审计', 2, 1, datetime('now'), datetime('now')),
(15, 4, '用户评价', '用户经验和评价分享', 3, 1, datetime('now'), datetime('now'));
```

### 快速恢复脚本
如果分类数据丢失，运行以下命令恢复：
```bash
sqlite3 /Users/ck/Desktop/Project/trustagency/backend/trustagency.db < recovery_categories.sql
```

### 清空并重建分类
```sql
-- 备份现有数据（可选）
-- CREATE TABLE categories_backup AS SELECT * FROM categories;

-- 删除所有分类
DELETE FROM categories;

-- 重新插入分类数据（使用上面的INSERT语句）
```

---

## 🔗 Sections表关联数据

为了完整性，以下是Sections表的参考数据：

```sql
-- Sections 表数据
SELECT * FROM sections ORDER BY sort_order;

-- 预期结果:
id | name | slug | description | requires_platform | sort_order | is_active
1  | 常见问题 | faq | 常见问题解答 | 0 | 1 | 1
2  | 百科 | wiki | 区块链和加密货币百科 | 0 | 2 | 1
3  | 指南 | guide | 交易和投资指南 | 0 | 3 | 1
4  | 验证 | review | 项目和平台验证 | 0 | 4 | 1
```

---

## ⚙️ 数据一致性检查清单

使用以下SQL检查数据一致性：

```sql
-- 1. 检查sort_order连续性
SELECT section_id, COUNT(DISTINCT sort_order) as unique_orders
FROM categories
GROUP BY section_id
HAVING unique_orders != COUNT(*);
-- 预期: 无结果 (所有sort_order连续)

-- 2. 检查重复分类名称
SELECT section_id, name, COUNT(*)
FROM categories
GROUP BY section_id, name
HAVING COUNT(*) > 1;
-- 预期: 无结果 (无重复)

-- 3. 检查空值
SELECT COUNT(*) FROM categories 
WHERE id IS NULL OR section_id IS NULL OR name IS NULL OR sort_order IS NULL;
-- 预期: 0

-- 4. 检查外键约束
SELECT COUNT(*) FROM categories c
WHERE NOT EXISTS (SELECT 1 FROM sections s WHERE s.id = c.section_id);
-- 预期: 0 (所有分类都有关联栏目)

-- 5. 检查类型一致性
SELECT typeof(id), typeof(section_id), typeof(sort_order) FROM categories LIMIT 1;
-- 预期: 'integer' | 'integer' | 'integer'
```

---

## 📋 恢复步骤

### 如果分类数据丢失

**步骤1**: 停止后端服务
```bash
pkill -f uvicorn
```

**步骤2**: 备份当前数据库（防止覆盖有用数据）
```bash
cp trustagency.db trustagency.db.backup
```

**步骤3**: 使用恢复脚本
```bash
sqlite3 trustagency.db < recovery_categories.sql
```

**步骤4**: 验证恢复
```bash
sqlite3 trustagency.db "SELECT COUNT(*) FROM categories;"
# 预期输出: 15
```

**步骤5**: 重启后端服务
```bash
# 使用你的启动脚本或命令
bash run_backend.sh
```

**步骤6**: 验证API
```bash
curl http://localhost:8001/api/categories/section/1
# 应该返回常见问题的5个分类
```

---

## 🔐 数据备份建议

### 定期备份脚本
```bash
#!/bin/bash
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp trustagency.db "$BACKUP_DIR/trustagency_backup_$TIMESTAMP.db"
echo "✅ 备份完成: $BACKUP_DIR/trustagency_backup_$TIMESTAMP.db"
```

### 自动备份任务（Linux/Mac）
```bash
# 添加到 crontab 每天备份一次
0 2 * * * /path/to/backup_script.sh
```

---

## 📝 修改记录

| 日期 | 操作 | 影响范围 | 验证状态 |
|------|------|--------|--------|
| 2025-11-10 | 更新15个分类名称 | Categories表 | ✅ |
| 2025-11-10 | 添加sort_order字段 | Categories表 | ✅ |
| 2025-11-10 | 创建指南和验证分类 | Categories表 | ✅ |

---

## 🚨 重要警告

⚠️ **不要手动删除分类，使用提供的恢复脚本**

⚠️ **定期检查数据一致性**

⚠️ **在执行任何数据操作前备份数据库**

---

**版本**: 1.0  
**生成日期**: 2025年11月10日  
**下一次审查日期**: 2025年11月17日

