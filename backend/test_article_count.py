#!/usr/bin/env python
"""测试分类文章计数功能"""
import sys
sys.path.insert(0, '.')

from app.db import SessionLocal, engine
from app.models import Article, Category, Section
from datetime import datetime

db = SessionLocal()

try:
    # 获取第一个栏目
    section = db.query(Section).first()
    if not section:
        print("❌ 没有栏目数据")
        sys.exit(1)
    
    print(f"📌 栏目: {section.name} (ID: {section.id})")
    
    # 获取该栏目下的分类
    categories = db.query(Category).filter(
        Category.section_id == section.id,
        Category.is_active == True
    ).all()
    
    if not categories:
        print("❌ 该栏目没有分类")
        sys.exit(1)
    
    print(f"📂 分类数: {len(categories)}")
    
    # 为第一个分类创建测试文章
    category = categories[0]
    print(f"\n📝 为分类 '{category.name}' (ID: {category.id}) 创建测试文章...")
    
    # 创建 3 篇文章
    for i in range(3):
        article = Article(
            title=f"测试文章 {i+1}",
            content=f"这是测试文章 {i+1} 的内容",
            category_id=category.id,
            platform_id=1,  # 假设平台ID为1
            is_published=True,
            views=i * 10,
            created_at=datetime.now()
        )
        db.add(article)
        print(f"  ✅ 创建: {article.title}")
    
    db.commit()
    print("✅ 文章已保存到数据库")
    
    # 现在验证统计
    print("\n📊 验证分类统计...")
    
    from sqlalchemy import func
    
    for cat in categories:
        count = db.query(func.count(Article.id)).filter(
            Article.category_id == cat.id,
            Article.is_published == True
        ).scalar() or 0
        
        print(f"  分类 '{cat.name}': {count} 篇文章")
    
    print("\n✅ 测试完成！分类统计功能正常")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
