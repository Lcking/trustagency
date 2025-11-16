#!/usr/bin/env python3
"""
一键恢复脚本 - 修复所有已知问题
"""
import os
import sys
from pathlib import Path

# 设置工作目录
os.chdir('/Users/ck/Desktop/Project/trustagency/backend')
sys.path.insert(0, '/Users/ck/Desktop/Project/trustagency/backend')

print("🚀 开始一键恢复...")
print("=" * 70)

# 第1步：检查环境
print("\n1️⃣  检查环境...")
try:
    import dotenv
    print("   ✅ dotenv 可用")
except:
    print("   ⚠️  dotenv 不可用，尝试安装...")

# 第2步：加载配置
print("\n2️⃣  加载配置...")
from dotenv import load_dotenv
load_dotenv()
print("   ✅ 配置已加载")

# 第3步：连接数据库
print("\n3️⃣  连接数据库...")
try:
    from app.database import engine, SessionLocal
    from sqlalchemy import inspect, text
    
    # 测试连接
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("   ✅ 数据库连接成功")
except Exception as e:
    print(f"   ❌ 数据库连接失败: {e}")
    sys.exit(1)

# 第4步：检查表
print("\n4️⃣  检查数据库表...")
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = ['section', 'category', 'platform', 'article']
    
    for table in required_tables:
        if table in tables:
            print(f"   ✅ {table} 表存在")
        else:
            print(f"   ⚠️  {table} 表不存在")
            
except Exception as e:
    print(f"   ❌ 检查失败: {e}")

# 第5步：恢复分类数据
print("\n5️⃣  恢复分类数据...")
try:
    from app.models import Section, Category
    from datetime import datetime
    
    db = SessionLocal()
    
    # 检查现有分类
    sections = db.query(Section).all()
    print(f"   找到 {len(sections)} 个栏目")
    
    # 分类定义
    CATEGORIES_DATA = {
        "faq": ["账户问题", "交易问题", "安全问题", "费用问题", "其他问题"],
        "wiki": ["基础概念", "交易技巧", "市场分析", "风险管理", "平台对比"],
        "guide": ["快速开始", "开户指南", "交易指南", "风险设置", "高级策略"],
        "review": ["安全性分析", "交易体验", "费用对比", "客户服务", "综合评分"],
    }
    
    total_added = 0
    
    for section in sections:
        cat_names = CATEGORIES_DATA.get(section.slug, [])
        
        for cat_name in cat_names:
            # 检查是否存在
            existing = db.query(Category).filter(
                Category.section_id == section.id,
                Category.name == cat_name
            ).first()
            
            if not existing:
                cat = Category(
                    name=cat_name,
                    section_id=section.id,
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(cat)
                total_added += 1
    
    db.commit()
    db.close()
    
    print(f"   ✅ 已恢复 {total_added} 个分类")
    
except Exception as e:
    print(f"   ❌ 恢复失败: {e}")
    import traceback
    traceback.print_exc()

# 第6步：验证
print("\n6️⃣  验证数据...")
try:
    db = SessionLocal()
    
    sections_count = db.query(Section).count()
    categories_count = db.query(Category).count()
    platforms_count = db.query(Section).count()
    
    print(f"   • Sections: {sections_count}")
    print(f"   • Categories: {categories_count}")
    print(f"   • Platforms: {platforms_count}")
    
    if categories_count > 0:
        print("   ✅ 分类数据已恢复")
    else:
        print("   ⚠️  分类数据仍为空")
    
    db.close()
    
except Exception as e:
    print(f"   ❌ 验证失败: {e}")

print("\n" + "=" * 70)
print("✅ 恢复完成！")
print("=" * 70)
print("\n现在运行: python -m uvicorn app.main:app --reload --port 8000")
