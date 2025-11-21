import sqlite3
db = '/Users/ck/Desktop/Project/trustagency/backend/trustagency.db'
try:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM platforms")
    count = c.fetchone()[0]
    if count == 4:
        print("✅ 数据库有效，平台总数: 4")
        c.execute("SELECT id, name, platform_type FROM platforms ORDER BY id")
        for row in c.fetchall():
            print(f"   {row[0]}. {row[1]:20} → {row[2]}")
    else:
        print(f"❌ 平台数不对，当前: {count}")
    conn.close()
except Exception as e:
    print(f"❌ 错误: {e}")
