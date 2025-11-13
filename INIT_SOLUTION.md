# 🔧 平台数据初始化 - 常见问题解决方案

## 问题：ModuleNotFoundError: No module named 'app'

### 原因
从 `backend/scripts/` 目录运行 Python 脚本时，Python 无法找到 `app` 模块。

### 解决方案

#### ✅ 推荐方案 1：从 backend 目录运行（最简单）

```bash
cd /Users/ck/Desktop/Project/trustagency/backend

# 使用 Python 交互式解释器运行初始化代码
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal, engine
from app.models import Platform
from sqlalchemy import text, inspect
import json
from datetime import datetime

# 1. 连接数据库
db = SessionLocal()
print("✓ 数据库连接成功")

# 2. 检查并添加列
inspector = inspect(engine)
columns = {col['name'] for col in inspector.get_columns('platform')}
new_cols = {
    'why_choose', 'account_types', 'fee_table', 'trading_tools',
    'opening_steps', 'safety_info', 'learning_resources', 'overview_intro', 'top_badges'
}

missing = new_cols - columns
if missing:
    print(f"\n添加 {len(missing)} 个新列...")
    for col in missing:
        try:
            db.execute(text(f"ALTER TABLE platform ADD COLUMN {col} TEXT"))
            print(f"  ✓ {col}")
        except Exception as e:
            if "already exists" not in str(e):
                print(f"  ⚠ {col}: {e}")
    db.commit()
    print("✓ 列添加完成")

# 3. 初始化平台数据
print("\n初始化平台数据...")

platforms_info = {
    'alpha-leverage': {
        'name': 'AlphaLeverage',
        'data': {
            'overview_intro': 'AlphaLeverage是一个专为专业交易者设计的高杠杆交易平台',
            'why_choose': json.dumps([
                {'icon': '📈', 'title': '最高杠杆比率', 'description': '提供高达1:500的杠杆比率'},
                {'icon': '💰', 'title': '最低交易费用', 'description': '行业内最低的佣金费率'},
                {'icon': '🛠️', 'title': '高级交易工具', 'description': '专业级的图表分析工具'},
                {'icon': '🌙', 'title': '24/7专业支持', 'description': '全天候多语言客户支持'}
            ], ensure_ascii=False),
            'account_types': json.dumps([
                {'name': '基础账户', 'leverage': '1:100', 'min_deposit': '$5,000'},
                {'name': 'VIP账户', 'leverage': '1:500', 'min_deposit': '$50,000'}
            ], ensure_ascii=False),
            'fee_table': json.dumps([
                {'type': '交易手续费', 'basic': '0.20%', 'vip': '0.10%'},
                {'type': '借款利息', 'basic': '6-8%', 'vip': '4-6%'}
            ], ensure_ascii=False),
            'top_badges': json.dumps(['推荐平台', '专业级交易'], ensure_ascii=False)
        }
    },
    'beta-margin': {
        'name': 'BetaMargin',
        'data': {
            'overview_intro': 'BetaMargin是一个平衡专业性和易用性的交易平台',
            'why_choose': json.dumps([
                {'icon': '🏢', 'title': '可靠基础设施', 'description': '99.99%运行时间'},
                {'icon': '⚖️', 'title': '公平费率', 'description': '透明的费用体系'}
            ], ensure_ascii=False),
            'top_badges': json.dumps(['成熟稳定', '平衡型'], ensure_ascii=False)
        }
    },
    'gamma-trader': {
        'name': 'GammaTrader',
        'data': {
            'overview_intro': 'GammaTrader是专为初学者设计的教育导向型交易平台',
            'why_choose': json.dumps([
                {'icon': '📚', 'title': '教育优先', 'description': '提供全面的学习资源'},
                {'icon': '🔒', 'title': '安全优先', 'description': '低杠杆设置'}
            ], ensure_ascii=False),
            'top_badges': json.dumps(['新手友好', '教育平台'], ensure_ascii=False)
        }
    }
}

for slug, info in platforms_info.items():
    try:
        p = db.query(Platform).filter(Platform.slug == slug).first()
        if not p:
            print(f"  ⚠ 平台未找到: {slug}")
            continue
        
        for field, value in info['data'].items():
            setattr(p, field, value)
        
        p.updated_at = datetime.utcnow()
        db.commit()
        print(f"  ✓ 更新: {info['name']}")
    except Exception as e:
        print(f"  ✗ 失败 {slug}: {e}")
        db.rollback()

db.close()
print("\n✅ 初始化完成！")
EOF
```

#### ✅ 推荐方案 2：修改脚本的导入（永久修复）

编辑 `/backend/scripts/init_platform_data.py`，将开头改为：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# 获取backend目录（脚本的父级父级目录）
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# 现在可以导入app模块
from app.database import SessionLocal, engine
from app.models import Platform
# ... 其余代码
```

然后运行：
```bash
cd /Users/ck/Desktop/Project/trustagency/backend
python scripts/init_platform_data.py
```

---

## 如果遇到 zsh 连接问题

### 问题表现
```
Command exited with code 130
```

### 解决方案

#### 方法 A：启动新的 zsh 会话

```bash
# 退出当前终端，打开新终端
exec zsh

# 或者
cd /Users/ck/Desktop/Project/trustagency/backend
```

#### 方法 B：使用 SQLite CLI 直接修改数据库

```bash
cd /Users/ck/Desktop/Project/trustagency/backend

# 打开数据库
sqlite3 trustagency.db

# 检查现有列
.schema platform

# 添加缺失的列（如果还未添加）
ALTER TABLE platform ADD COLUMN why_choose TEXT;
ALTER TABLE platform ADD COLUMN account_types TEXT;
ALTER TABLE platform ADD COLUMN fee_table TEXT;
ALTER TABLE platform ADD COLUMN trading_tools TEXT;
ALTER TABLE platform ADD COLUMN opening_steps TEXT;
ALTER TABLE platform ADD COLUMN safety_info TEXT;
ALTER TABLE platform ADD COLUMN learning_resources TEXT;
ALTER TABLE platform ADD COLUMN overview_intro TEXT;
ALTER TABLE platform ADD COLUMN top_badges TEXT;

# 更新数据（使用 JSON）
UPDATE platform 
SET overview_intro = 'AlphaLeverage 是专业级交易平台'
WHERE slug = 'alpha-leverage';

# 验证
SELECT slug, length(overview_intro) FROM platform;

# 退出
.quit
```

---

## 验证初始化成功

初始化后，验证数据是否正确保存：

```bash
# 1. 查看数据库
sqlite3 /Users/ck/Desktop/Project/trustagency/backend/trustagency.db
SELECT id, name, slug, length(why_choose) as why_len FROM platform;
.quit

# 2. 启动后端服务
cd /Users/ck/Desktop/Project/trustagency/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 3. 在另一个终端测试 API
curl http://localhost:8001/api/admin/platforms/1/edit | python -m json.tool

# 应该看到新字段已填充：
# {
#   "id": 1,
#   "name": "AlphaLeverage",
#   "slug": "alpha-leverage",
#   "why_choose": "[{\"icon\": \"📈\", ...}]",
#   ...
# }
```

---

## 如果仍然遇到问题

### 调试步骤

1. **检查 Python 环境**
   ```bash
   which python3
   python3 --version
   pip3 list | grep sqlalchemy
   ```

2. **检查数据库文件**
   ```bash
   ls -la /Users/ck/Desktop/Project/trustagency/backend/
   # 应该看到 trustagency.db 或 app.db
   ```

3. **检查平台记录**
   ```bash
   sqlite3 /Users/ck/Desktop/Project/trustagency/backend/trustagency.db
   SELECT * FROM platform LIMIT 3;
   ```

4. **查看后端日志**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   # 观察启动日志中是否有错误
   ```

---

## 快速参考

| 任务 | 命令 |
|------|------|
| 进入后端目录 | `cd /Users/ck/Desktop/Project/trustagency/backend` |
| 运行初始化 | `python3 << 'EOF'` + 上述代码块 + `EOF` |
| 验证列 | `sqlite3 trustagency.db ".schema platform"` |
| 启动服务 | `python -m uvicorn app.main:app --reload` |
| 测试 API | `curl http://localhost:8001/api/admin/platforms/1/edit` |

---

**选择推荐方案 1 最快最简单！**
