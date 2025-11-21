#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

# 删除旧数据库
if os.path.exists('trustagency.db'):
    os.remove('trustagency.db')

# 创建新数据库
conn = sqlite3.connect('trustagency.db')
c = conn.cursor()

now = datetime.utcnow().isoformat()

# 创建所有表
c.execute('''CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    requires_platform BOOLEAN DEFAULT 0,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME,
    updated_at DATETIME
)''')

c.execute('''CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    section_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY(section_id) REFERENCES sections(id)
)''')

c.execute('''CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    is_superadmin BOOLEAN DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME
)''')

c.execute('''CREATE TABLE platforms (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    website_url VARCHAR(255),
    rating REAL DEFAULT 0.0,
    rank INTEGER,
    min_leverage REAL,
    max_leverage REAL,
    commission_rate REAL,
    is_regulated BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    is_recommended BOOLEAN DEFAULT 0,
    safety_rating VARCHAR(10),
    founded_year INTEGER,
    fee_rate REAL,
    platform_type VARCHAR(50),
    introduction TEXT,
    main_features TEXT,
    fee_structure TEXT,
    account_opening_link VARCHAR(255),
    created_at DATETIME,
    updated_at DATETIME
)''')

c.execute('''CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    section_id INTEGER,
    category_id INTEGER,
    platform_id INTEGER,
    author_id INTEGER,
    is_published BOOLEAN DEFAULT 1,
    view_count INTEGER DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY(section_id) REFERENCES sections(id),
    FOREIGN KEY(category_id) REFERENCES categories(id),
    FOREIGN KEY(platform_id) REFERENCES platforms(id),
    FOREIGN KEY(author_id) REFERENCES admin_users(id)
)''')

c.execute('''CREATE TABLE ai_configs (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    provider VARCHAR(100),
    model_name VARCHAR(100),
    api_key VARCHAR(255),
    is_active BOOLEAN DEFAULT 0,
    description TEXT,
    temperature INTEGER,
    max_tokens INTEGER,
    top_p INTEGER,
    created_at DATETIME,
    updated_at DATETIME
)''')

# 插入栏目 - 4个
sections = [
    (1, "常见问题", "faq", "常见问题解答", 0, 1, 1, now, now),
    (2, "百科", "wiki", "区块链和加密货币百科", 0, 2, 1, now, now),
    (3, "指南", "guide", "交易和投资指南", 0, 3, 1, now, now),
    (4, "验证", "review", "平台验证和审查记录", 1, 4, 1, now, now),
]
c.executemany('INSERT INTO sections VALUES (?,?,?,?,?,?,?,?,?)', sections)

# 插入分类 - 20个
categories = [
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
]
c.executemany('INSERT INTO categories VALUES (?,?,?,?,?,?,?,?)', categories)

# 插入管理员
admin_data = [
    (1, "admin", "admin@trustagency.com", "Administrator", "$2b$12$N9qo8uLOickgx2ZMRZoXyeIGlMw5YBNR5z7EcKxVx0.3S2KaUDSyO", 1, 1, now, now),
]
c.executemany('INSERT INTO admin_users VALUES (?,?,?,?,?,?,?,?,?)', admin_data)

# 插入平台 - 4个
platforms = [
    (1, "AlphaLeverage", "alphaleverage", "Professional forex trading platform", "https://alphaleverage.com", 4.8, 1, 1.0, 500.0, 0.005, 1, 1, 1, "A", 2015, 0.5, "专业", "AlphaLeverage是一个专业的外汇交易平台", '[{"title":"高杠杆"}]', '[{"type":"手续费"}]', "https://alphaleverage.com/open-account", now, now),
    (2, "BetaMargin", "betamargin", "Advanced trading with margin", "https://betamargin.com", 4.5, 2, 1.0, 300.0, 0.003, 1, 1, 1, "A", 2012, 0.3, "平衡", "BetaMargin是一个全球领先的保证金交易平台", '[{"title":"专业工具"}]', '[{"type":"手续费"}]', "https://betamargin.com/signup", now, now),
    (3, "GammaTrader", "gammatrader", "Professional trading platform", "https://gammatrader.com", 4.6, 3, 1.0, 400.0, 0.004, 1, 1, 0, "B", 2018, 0.4, "新手友好", "GammaTrader是一个创新型的交易平台", '[{"title":"AI助手"}]', '[{"type":"手续费"}]', "https://gammatrader.com/register", now, now),
    (4, "百度", "baidu", "百度推荐平台", "https://baidu.com", 4.7, 4, 1.0, 350.0, 0.0035, 1, 1, 1, "A", 2020, 0.35, "高风险", "百度是一个实际推荐的交易平台", '[{"title":"推荐平台"}]', '[{"type":"手续费"}]', "https://baidu.com/open-account", now, now),
]
c.executemany('INSERT INTO platforms VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', platforms)

# 插入文章
articles = [
    (1, "什么是杠杆交易？", "shen-me-shi-gang-gan-jiao-yi", "杠杆交易是一种使用借来的资金进行更大规模交易的方式。了解杠杆风险对成功交易至关重要。", "杠杆交易基础概念", 1, 1, None, 1, 1, 150, now, now),
    (2, "如何选择交易平台？", "ru-he-xuan-ze-jiao-yi-ping-tai", "选择交易平台时需要考虑安全性、手续费、杠杆比例和用户体验等多个因素。", "平台选择指南", 1, 1, None, 1, 1, 200, now, now),
    (3, "风险管理基础", "feng-xian-guan-li-ji-chu", "良好的风险管理是长期交易成功的基石。学会控制风险比追求高收益更重要。", "风险管理入门", 1, 1, None, 1, 1, 180, now, now),
]
c.executemany('INSERT INTO articles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', articles)

# 插入AI配置
ai_configs = [
    (1, "OpenAI GPT-4", "openai", "gpt-4", "sk-xxxxx", 0, "OpenAI GPT-4 model", 70, 2000, 90, now, now),
    (2, "DeepSeek", "deepseek", "deepseek-chat", "sk-xxxxx", 0, "DeepSeek model", 70, 2000, 90, now, now),
    (3, "中转链接", "midpoint", "gpt-3.5-turbo", "sk-xxxxx", 0, "Midpoint API", 70, 2000, 90, now, now),
]
c.executemany('INSERT INTO ai_configs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', ai_configs)

conn.commit()
conn.close()

# 验证
conn = sqlite3.connect('trustagency.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM sections')
print(f"✅ 栏目: {c.fetchone()[0]}")

c.execute('SELECT COUNT(*) FROM categories')
print(f"✅ 分类: {c.fetchone()[0]}")

c.execute('SELECT COUNT(*) FROM platforms')
print(f"✅ 平台: {c.fetchone()[0]}")

c.execute('SELECT COUNT(*) FROM admin_users')
print(f"✅ 管理员: {c.fetchone()[0]}")

c.execute('SELECT COUNT(*) FROM articles')
print(f"✅ 文章: {c.fetchone()[0]}")

print("\n📊 平台类型:")
c.execute('SELECT id, name, platform_type FROM platforms ORDER BY id')
for row in c.fetchall():
    print(f"   {row[0]}. {row[1]:20} → {row[2]}")

conn.close()
print("\n✅ 数据库生成完成！")
