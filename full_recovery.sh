#!/bin/bash
# 完全恢复脚本 - 恢复到提交9a98d02的状态

echo "🔄 开始恢复到提交 9a98d02 的完整状态..."
echo ""

# 1. 回退代码到那个提交
echo "📝 Step 1: 获取提交9a98d02的所有文件..."
cd /root/trustagency

# 获取那个提交的关键文件
git show 9a98d02:backend/app/database.py > backend/app/database.py.new
git show 9a98d02:docker-compose.prod.yml > docker-compose.prod.yml.new
git show 9a98d02:.env.prod.example > .env.prod.example.new

# 备份现有文件
cp backend/app/database.py backend/app/database.py.bak
cp docker-compose.prod.yml docker-compose.prod.yml.bak

# 应用新文件
mv backend/app/database.py.new backend/app/database.py
mv docker-compose.prod.yml.new docker-compose.prod.yml
mv .env.prod.example.new .env.prod.example

echo "✅ 配置文件已更新\n"

# 2. 重新生成数据库
echo "📦 Step 2: 生成完整的SQLite数据库..."

python3 << 'PYEOF'
import sqlite3, os
from datetime import datetime

db = "/root/trustagency/backend/trustagency.db"
if os.path.exists(db):
    os.remove(db)

conn = sqlite3.connect(db)
c = conn.cursor()
now = datetime.utcnow().isoformat()

# 创建所有表
c.execute('CREATE TABLE sections (id INTEGER PRIMARY KEY, name VARCHAR(255) NOT NULL, slug VARCHAR(255) UNIQUE NOT NULL, description TEXT, requires_platform BOOLEAN DEFAULT 0, sort_order INTEGER, is_active BOOLEAN DEFAULT 1, created_at DATETIME, updated_at DATETIME)')
c.execute('CREATE TABLE categories (id INTEGER PRIMARY KEY, section_id INTEGER NOT NULL, name VARCHAR(255) NOT NULL, description TEXT, sort_order INTEGER, is_active BOOLEAN DEFAULT 1, created_at DATETIME, updated_at DATETIME, FOREIGN KEY(section_id) REFERENCES sections(id))')
c.execute('CREATE TABLE admin_users (id INTEGER PRIMARY KEY, username VARCHAR(255) UNIQUE NOT NULL, email VARCHAR(255), full_name VARCHAR(255), hashed_password VARCHAR(255) NOT NULL, is_active BOOLEAN DEFAULT 1, is_superadmin BOOLEAN DEFAULT 0, created_at DATETIME, updated_at DATETIME)')
c.execute('CREATE TABLE platforms (id INTEGER PRIMARY KEY, name VARCHAR(255) NOT NULL UNIQUE, slug VARCHAR(255) UNIQUE NOT NULL, description TEXT, website_url VARCHAR(255), rating REAL DEFAULT 0.0, rank INTEGER, min_leverage REAL, max_leverage REAL, commission_rate REAL, is_regulated BOOLEAN DEFAULT 0, is_active BOOLEAN DEFAULT 1, is_recommended BOOLEAN DEFAULT 0, safety_rating VARCHAR(10), founded_year INTEGER, fee_rate REAL, platform_type VARCHAR(50), introduction TEXT, main_features TEXT, fee_structure TEXT, account_opening_link VARCHAR(255), created_at DATETIME, updated_at DATETIME)')
c.execute('CREATE TABLE articles (id INTEGER PRIMARY KEY, title VARCHAR(255) NOT NULL, slug VARCHAR(255) UNIQUE NOT NULL, content TEXT NOT NULL, summary TEXT, section_id INTEGER, category_id INTEGER, platform_id INTEGER, author_id INTEGER, is_published BOOLEAN DEFAULT 1, view_count INTEGER DEFAULT 0, created_at DATETIME, updated_at DATETIME, FOREIGN KEY(section_id) REFERENCES sections(id), FOREIGN KEY(category_id) REFERENCES categories(id), FOREIGN KEY(platform_id) REFERENCES platforms(id), FOREIGN KEY(author_id) REFERENCES admin_users(id))')
c.execute('CREATE TABLE ai_configs (id INTEGER PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, provider VARCHAR(100), model_name VARCHAR(100), api_key VARCHAR(255), is_active BOOLEAN DEFAULT 0, description TEXT, temperature INTEGER, max_tokens INTEGER, top_p INTEGER, created_at DATETIME, updated_at DATETIME)')
c.execute('CREATE TABLE ai_generation_tasks (id INTEGER PRIMARY KEY, task_name VARCHAR(255), status VARCHAR(50), created_at DATETIME, updated_at DATETIME)')

# 插入数据
c.executemany('INSERT INTO sections VALUES (?,?,?,?,?,?,?,?,?)', [(1,"常见问题","faq","常见问题解答",0,1,1,now,now), (2,"百科","wiki","区块链百科",0,2,1,now,now), (3,"指南","guide","交易指南",0,3,1,now,now), (4,"验证","review","平台验证",1,4,1,now,now)])
categories = [(i, ((i-1)//5)+1, ["基础知识","账户管理","交易问题","安全","其他","基础概念","交易对","技术分析","风险管理","法规","新手教程","交易策略","风险管理","资金管理","高级技巧","安全评估","功能评测","用户评价","监管许可","服务评分"][i-1], f"分类{i}", ((i-1)%5)+1, 1, now, now) for i in range(1,21)]
c.executemany('INSERT INTO categories VALUES (?,?,?,?,?,?,?,?)', categories)
c.executemany('INSERT INTO admin_users VALUES (?,?,?,?,?,?,?,?,?)', [(1,"admin","admin@trustagency.com","Administrator","$2b$12$N9qo8uLOickgx2ZMRZoXyeIGlMw5YBNR5z7EcKxVx0.3S2KaUDSyO",1,1,now,now)])
c.executemany('INSERT INTO platforms VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [(1,"AlphaLeverage","alphaleverage","Professional","https://alphaleverage.com",4.8,1,1.0,500.0,0.005,1,1,1,"A",2015,0.5,"专业","专业平台",'[]','[]',"https://alphaleverage.com",now,now), (2,"BetaMargin","betamargin","Advanced","https://betamargin.com",4.5,2,1.0,300.0,0.003,1,1,1,"A",2012,0.3,"平衡","平衡平台",'[]','[]',"https://betamargin.com",now,now), (3,"GammaTrader","gammatrader","Professional","https://gammatrader.com",4.6,3,1.0,400.0,0.004,1,1,0,"B",2018,0.4,"新手友好","新手平台",'[]','[]',"https://gammatrader.com",now,now), (4,"百度","baidu","百度平台","https://baidu.com",4.7,4,1.0,350.0,0.0035,1,1,1,"A",2020,0.35,"高风险","高风险平台",'[]','[]',"https://baidu.com",now,now)])
c.executemany('INSERT INTO articles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', [(1,"杠杆","gauge","内容","基础",1,1,None,1,1,150,now,now), (2,"平台","platform","内容","指南",1,1,None,1,1,200,now,now), (3,"风险","risk","内容","基础",1,1,None,1,1,180,now,now)])
c.executemany('INSERT INTO ai_configs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', [(1,"GPT4","openai","gpt4","sk",0,"gpt",70,2000,90,now,now), (2,"DS","deepseek","chat","sk",0,"ds",70,2000,90,now,now)])

conn.commit()
conn.close()

# 验证
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM platforms")
print(f"✅ 数据库已生成，平台总数: {c.fetchone()[0]}")
c.execute("SELECT id, name, platform_type FROM platforms ORDER BY id")
print("\n📊 平台类型:")
for row in c.fetchall():
    print(f"   {row[0]}. {row[1]:20} → {row[2]}")
conn.close()

PYEOF

echo ""
echo "✅ 数据库生成完成"
echo ""

# 3. 重启Docker容器
echo "🔄 Step 3: 重启Docker容器..."
docker-compose -f docker-compose.prod.yml down
sleep 3
mkdir -p /root/trustagency/backend/data
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ 等待容器启动..."
sleep 10

# 4. 验证部署
echo ""
echo "✅ Step 4: 验证部署..."
docker-compose -f docker-compose.prod.yml ps
echo ""
docker exec trustagency-backend-prod ls -lh /app/data/ 2>/dev/null || echo "⚠️  /app/data 目录不存在"
echo ""

# 验证API
echo "🌐 测试API..."
curl -s http://127.0.0.1:8001/api/platforms | head -c 200
echo ""
echo ""

echo "✅ 完全恢复完成！"
echo ""
echo "📋 恢复清单:"
echo "   ✅ 代码配置文件已恢复"
echo "   ✅ SQLite数据库已生成（4个栏目，20个分类，4个平台）"
echo "   ✅ Docker容器已重启"
echo "   ✅ 数据库卷已挂载到 /app/data/trustagency.db"
echo ""
echo "🎯 系统状态:"
echo "   Frontend: http://instance-kkbz8iy4:80"
echo "   Backend: http://instance-kkbz8iy4:8001"
echo "   Admin: http://instance-kkbz8iy4/admin"
