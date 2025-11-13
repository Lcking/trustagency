# 平台数据初始化 - 手动执行指南

由于 zsh 终端连接问题，请按照以下步骤手动执行初始化：

## 方法 1：使用 Python 交互式 Shell（推荐）

```bash
cd /Users/ck/Desktop/Project/trustagency/backend
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine
from app.models import Platform
from sqlalchemy import text, inspect
import json
from datetime import datetime

# 连接数据库
db = SessionLocal()
print("✓ 数据库已连接")

# 检查并添加列
inspector = inspect(engine)
columns = {col['name'] for col in inspector.get_columns('platform')}
new_cols = {'why_choose', 'account_types', 'fee_table', 'trading_tools', 
            'opening_steps', 'safety_info', 'learning_resources', 'overview_intro', 'top_badges'}

for col in new_cols - columns:
    try:
        db.execute(text(f"ALTER TABLE platform ADD COLUMN {col} TEXT"))
        print(f"✓ 添加列: {col}")
    except:
        pass
db.commit()

# 更新平台数据
data = {
    'alpha-leverage': {
        'why_choose': json.dumps([{'icon': '📈', 'title': '最高杠杆比率', 'description': '提供高达1:500的杠杆比率'}], ensure_ascii=False),
        'account_types': json.dumps([{'name': '基础账户', 'leverage': '1:100', 'min_deposit': '$5,000', 'fee': '0.20%'}], ensure_ascii=False),
    },
    'beta-margin': {
        'why_choose': json.dumps([{'icon': '🏢', 'title': '可靠的基础设施', 'description': '99.99%正常运行时间'}], ensure_ascii=False),
    },
    'gamma-trader': {
        'why_choose': json.dumps([{'icon': '📚', 'title': '教育优先', 'description': '提供全面的学习资源'}], ensure_ascii=False),
    }
}

for slug, fields in data.items():
    p = db.query(Platform).filter(Platform.slug == slug).first()
    if p:
        for k, v in fields.items():
            setattr(p, k, v)
        print(f"✓ 更新: {p.name}")

db.commit()
db.close()
print("✓ 完成！")
EOF
```

## 方法 2：直接使用 SQLite CLI

```bash
cd /Users/ck/Desktop/Project/trustagency/backend

# 打开数据库
sqlite3 trustagency.db

# 执行 SQL 命令
ALTER TABLE platform ADD COLUMN why_choose TEXT;
ALTER TABLE platform ADD COLUMN account_types TEXT;
ALTER TABLE platform ADD COLUMN fee_table TEXT;
ALTER TABLE platform ADD COLUMN trading_tools TEXT;
ALTER TABLE platform ADD COLUMN opening_steps TEXT;
ALTER TABLE platform ADD COLUMN safety_info TEXT;
ALTER TABLE platform ADD COLUMN learning_resources TEXT;
ALTER TABLE platform ADD COLUMN overview_intro TEXT;
ALTER TABLE platform ADD COLUMN top_badges TEXT;

# 查询现有平台
SELECT id, name, slug FROM platform;

# 退出
.quit
```

## 方法 3：使用 Python 脚本（如果方法1失败）

创建文件 `/tmp/init.py`：

```python
import sys
import os
sys.path.insert(0, '/Users/ck/Desktop/Project/trustagency/backend')
os.chdir('/Users/ck/Desktop/Project/trustagency/backend')

from app.database import SessionLocal, engine
from app.models import Platform
from sqlalchemy import text, inspect
import json

db = SessionLocal()
inspector = inspect(engine)
columns = {col['name'] for col in inspector.get_columns('platform')}

# 添加缺失的列
for col in ['why_choose', 'account_types', 'fee_table']:
    if col not in columns:
        db.execute(text(f"ALTER TABLE platform ADD COLUMN {col} TEXT"))
        print(f"Added: {col}")

db.commit()
db.close()
print("Done!")
```

然后运行：
```bash
python3 /tmp/init.py
```

---

## 验证数据库更新

运行后端服务时，检查日志或访问 API：

```bash
# 启动后端
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 在另一个终端，查询 API
curl http://localhost:8001/api/admin/platforms/1/edit

# 查看返回的 JSON 是否包含新字段
```

---

## 问题排查

### 错误：database is locked

解决：关闭所有其他连接后端的进程，或使用 `SQLite` 的 WAL 模式

### 错误：column already exists

这是正常的，说明列已存在，可以忽略

### 数据没有更新

确认：
1. 数据库文件位置正确：`/backend/trustagency.db`
2. 平台记录确实存在
3. 查询时使用正确的字段名

---

**推荐使用方法 1（交互式 Shell）- 最简单可靠**
