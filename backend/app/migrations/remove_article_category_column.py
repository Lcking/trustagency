"""
删除 articles 表的 category 列
执行此脚本前请确保所有代码已更新为使用 category_id
"""
import sqlite3
import sys
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / "trustagency.db"


def remove_category_column():
    """删除 articles 表的 category 列"""
    print(f"📍 数据库路径: {DB_PATH}")
    
    if not DB_PATH.exists():
        print("❌ 数据库文件不存在!")
        sys.exit(1)
    
    # 连接数据库
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # 检查 category 列是否存在
        cursor.execute("PRAGMA table_info(articles)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'category' not in column_names:
            print("✅ category 列已经不存在,无需删除")
            return
        
        print("📋 当前 articles 表结构:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # SQLite 不支持 ALTER TABLE DROP COLUMN (需要 SQLite 3.35.0+)
        # 我们需要重建表
        print("\n🔧 开始重建表...")
        
        # 1. 创建新表 (不包含 category 列)
        cursor.execute("""
            CREATE TABLE articles_new (
                id INTEGER PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                slug VARCHAR(300) UNIQUE NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                section_id INTEGER NOT NULL,
                category_id INTEGER,
                tags VARCHAR(500),
                author_id INTEGER NOT NULL,
                platform_id INTEGER,
                is_published BOOLEAN DEFAULT 0,
                is_featured BOOLEAN DEFAULT 0,
                meta_description VARCHAR(160),
                meta_keywords VARCHAR(500),
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                created_at DATETIME,
                updated_at DATETIME,
                published_at DATETIME,
                FOREIGN KEY(section_id) REFERENCES sections(id),
                FOREIGN KEY(category_id) REFERENCES categories(id),
                FOREIGN KEY(author_id) REFERENCES admin_users(id),
                FOREIGN KEY(platform_id) REFERENCES platforms(id)
            )
        """)
        print("   ✅ 创建新表 articles_new")
        
        # 2. 复制数据 (排除 category 列)
        cursor.execute("""
            INSERT INTO articles_new 
            SELECT 
                id, title, slug, content, summary, section_id, category_id, tags,
                author_id, platform_id, is_published, is_featured, meta_description,
                meta_keywords, view_count, like_count, created_at, updated_at, published_at
            FROM articles
        """)
        print("   ✅ 复制数据到新表")
        
        # 3. 删除旧表
        cursor.execute("DROP TABLE articles")
        print("   ✅ 删除旧表")
        
        # 4. 重命名新表
        cursor.execute("ALTER TABLE articles_new RENAME TO articles")
        print("   ✅ 重命名新表为 articles")
        
        # 5. 重建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_section_id ON articles(section_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_category_id ON articles(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_title ON articles(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_is_published ON articles(is_published)")
        print("   ✅ 重建索引")
        
        # 提交事务
        conn.commit()
        
        print("\n✅ 成功删除 category 列!")
        
        # 验证新表结构
        cursor.execute("PRAGMA table_info(articles)")
        new_columns = cursor.fetchall()
        print("\n📋 新的 articles 表结构:")
        for col in new_columns:
            print(f"   - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🗑️  删除 articles 表的 category 列")
    print("=" * 60)
    
    # 确认操作
    response = input("\n⚠️  此操作将删除 category 列,确定继续? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ 操作已取消")
        sys.exit(0)
    
    remove_category_column()
    print("\n✅ 迁移完成!")
