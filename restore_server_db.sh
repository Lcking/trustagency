#!/bin/bash
# 服务器数据库恢复脚本

cd /root/trustagency/backend

# 删除旧数据库
rm -f trustagency.db

# 创建新数据库
python3 << 'PYEOF'
import sqlite3
from datetime import datetime

db = "trustagency.db"
conn = sqlite3.connect(db)
c = conn.cursor()
now = datetime.utcnow().isoformat()

# 创建所有表
c.execute('''CREATE TABLE sections (id INTEGER PRIMARY KEY, name VARCHAR(255) NOT NULL, slug VARCHAR(255) UNIQUE NOT NULL, description TEXT, requires_platform BOOLEAN DEFAULT 0, sort_order INTEGER, is_active BOOLEAN DEFAULT 1, created_at DATETIME, updated_at DATETIME)''')
c.execute('''CREATE TABLE categories (id INTEGER PRIMARY KEY, section_id INTEGER NOT NULL, name VARCHAR(255) NOT NULL, description TEXT, sort_order INTEGER, is_active BOOLEAN DEFAULT 1, created_at DATETIME, updated_at DATETIME, FOREIGN KEY(section_id) REFERENCES sections(id))''')
c.execute('''CREATE TABLE admin_users (id INTEGER PRIMARY KEY, username VARCHAR(255) UNIQUE NOT NULL, email VARCHAR(255), full_name VARCHAR(255), hashed_password VARCHAR(255) NOT NULL, is_active BOOLEAN DEFAULT 1, is_superadmin BOOLEAN DEFAULT 0, created_at DATETIME, updated_at DATETIME)''')
c.execute('''CREATE TABLE platforms (id INTEGER PRIMARY KEY, name VARCHAR(255) NOT NULL UNIQUE, slug VARCHAR(255) UNIQUE NOT NULL, description TEXT, website_url VARCHAR(255), rating REAL DEFAULT 0.0, rank INTEGER, min_leverage REAL, max_leverage REAL, commission_rate REAL, is_regulated BOOLEAN DEFAULT 0, is_active BOOLEAN DEFAULT 1, is_recommended BOOLEAN DEFAULT 0, safety_rating VARCHAR(10), founded_year INTEGER, fee_rate REAL, platform_type VARCHAR(50), introduction TEXT, main_features TEXT, fee_structure TEXT, account_opening_link VARCHAR(255), created_at DATETIME, updated_at DATETIME)''')
c.execute('''CREATE TABLE articles (id INTEGER PRIMARY KEY, title VARCHAR(255) NOT NULL, slug VARCHAR(255) UNIQUE NOT NULL, content TEXT NOT NULL, summary TEXT, section_id INTEGER, category_id INTEGER, platform_id INTEGER, author_id INTEGER, is_published BOOLEAN DEFAULT 1, view_count INTEGER DEFAULT 0, created_at DATETIME, updated_at DATETIME, FOREIGN KEY(section_id) REFERENCES sections(id), FOREIGN KEY(category_id) REFERENCES categories(id), FOREIGN KEY(platform_id) REFERENCES platforms(id), FOREIGN KEY(author_id) REFERENCES admin_users(id))''')
c.execute('''CREATE TABLE ai_configs (id INTEGER PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, provider VARCHAR(100), model_name VARCHAR(100), api_key VARCHAR(255), is_active BOOLEAN DEFAULT 0, description TEXT, temperature INTEGER, max_tokens INTEGER, top_p INTEGER, created_at DATETIME, updated_at DATETIME)''')

# 插入栏目
c.executemany('INSERT INTO sections VALUES (?,?,?,?,?,?,?,?,?)', [
    (1, "常见问题", "faq", "常见问题解答", 0, 1, 1, now, now),
    (2, "百科", "wiki", "区块链和加密货币百科", 0, 2, 1, now, now),
    (3, "指南", "guide", "交易和投资指南", 0, 3, 1, now, now),
    (4, "验证", "review", "平台验证和审查记录", 1, 4, 1, now, now),
])

# 插入分类
c.executemany('INSERT INTO categories VALUES (?,?,?,?,?,?,?,?)', [
    (1, 1, "基础知识", "交易基础知识", 1, 1, now, now),
    (2, 1, "账户管理", "账户相关问题", 2, 1, now, now),
    (3, 1, "交易问题", "交易相关问题", 3, 1, now, now),
    (4, 1, "安全", "安全相关问题", 4, 1, now, now),
    (5, 1, "其他", "其他常见问题", 5, 1, now, now),
    (6, 2, "基础概念", "区块链基础概念", 1, 1, now, now),
    (7, 2, "交易对", "各类交易对介绍", 2, 1, now, now),
    (8, 2, "技术分析", "技术分析方法", 3, 1, now, now),
    (9, 2, "风险管理", "风险管理策略", 4, 1, now, now),
    (10, 2, "法规", "相关法规和许可", 5, 1, now, now),
    (11, 3, "新手教程", "新手入门教程", 1, 1, now, now),
    (12, 3, "交易策略", "交易策略指南", 2, 1, now, now),
    (13, 3, "风险管理", "风险管理最佳实践", 3, 1, now, now),
    (14, 3, "资金管理", "资金管理技巧", 4, 1, now, now),
    (15, 3, "高级技巧", "高级交易技巧", 5, 1, now, now),
    (16, 4, "安全评估", "平台安全评估", 1, 1, now, now),
    (17, 4, "功能评测", "平台功能评测", 2, 1, now, now),
    (18, 4, "用户评价", "用户反馈评价", 3, 1, now, now),
    (19, 4, "监管许可", "监管许可信息", 4, 1, now, now),
    (20, 4, "服务评分", "综合服务评分", 5, 1, now, now),
])

# 插入管理员
c.executemany('INSERT INTO admin_users VALUES (?,?,?,?,?,?,?,?,?)', [
    (1, "admin", "admin@trustagency.com", "Administrator", "$2b$12$N9qo8uLOickgx2ZMRZoXyeIGlMw5YBNR5z7EcKxVx0.3S2KaUDSyO", 1, 1, now, now),
])

# 插入平台
c.executemany('INSERT INTO platforms VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [
    (1, "AlphaLeverage", "alphaleverage", "Professional forex", "https://alphaleverage.com", 4.8, 1, 1.0, 500.0, 0.005, 1, 1, 1, "A", 2015, 0.5, "专业", "专业平台", '[]', '[]', "https://alphaleverage.com", now, now),
    (2, "BetaMargin", "betamargin", "Advanced margin", "https://betamargin.com", 4.5, 2, 1.0, 300.0, 0.003, 1, 1, 1, "A", 2012, 0.3, "平衡", "平衡平台", '[]', '[]', "https://betamargin.com", now, now),
    (3, "GammaTrader", "gammatrader", "Professional trade", "https://gammatrader.com", 4.6, 3, 1.0, 400.0, 0.004, 1, 1, 0, "B", 2018, 0.4, "新手友好", "新手平台", '[]', '[]', "https://gammatrader.com", now, now),
    (4, "百度", "baidu", "百度平台", "https://baidu.com", 4.7, 4, 1.0, 350.0, 0.0035, 1, 1, 1, "A", 2020, 0.35, "高风险", "高风险平台", '[]', '[]', "https://baidu.com", now, now),
])

# 插入文章
c.executemany('INSERT INTO articles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', [
    (1, "什么是杠杆交易？", "gauge", "杠杆交易内容", "杠杆基础", 1, 1, None, 1, 1, 150, now, now),
    (2, "如何选择平台？", "platform", "平台选择内容", "平台指南", 1, 1, None, 1, 1, 200, now, now),
    (3, "风险管理基础", "risk", "风险管理内容", "风险基础", 1, 1, None, 1, 1, 180, now, now),
])

# 插入AI配置
c.executemany('INSERT INTO ai_configs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', [
    (1, "OpenAI GPT-4", "openai", "gpt-4", "sk-xxx", 0, "GPT4", 70, 2000, 90, now, now),
    (2, "DeepSeek", "deepseek", "chat", "sk-xxx", 0, "DS", 70, 2000, 90, now, now),
    (3, "中转", "midpoint", "gpt35", "sk-xxx", 0, "MP", 70, 2000, 90, now, now),
])

conn.commit()
conn.close()

# 验证
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM platforms")
print(f"✅ 数据库已恢复，平台总数：{c.fetchone()[0]}")
c.execute("SELECT id, name, platform_type FROM platforms ORDER BY id")
print("\n📊 平台类型分类:")
for row in c.fetchall():
    print(f"   {row[0]}. {row[1]:20} → {row[2]}")
conn.close()

PYEOF

echo "✅ 数据库恢复完成！"
ls -lh trustagency.db
