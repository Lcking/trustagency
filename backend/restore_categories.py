#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
恢复分类数据 - 修复 oldbug001
将所有分类从无恢复到正常状态
"""
import sys
import os

# 提前导入验证
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import DATABASE_URL, Base, engine
    from app.models.category import Category
    from app.models.section import Section
    from datetime import datetime
    sys.stdout.flush()
except ImportError as e:
    print(f"❌ 导入失败: {e}", file=sys.stderr)
    sys.exit(1)

print("当前数据库文件:", engine.url.database)
sys.stdout.flush()

# 分类数据定义
CATEGORIES_DATA = {
    "faq": [  # 常见问题
        {"name": "账户问题"},
        {"name": "交易问题"},
        {"name": "安全问题"},
        {"name": "费用问题"},
        {"name": "其他问题"},
    ],
    "wiki": [  # 百科
        {"name": "基础概念"},
        {"name": "交易技巧"},
        {"name": "市场分析"},
        {"name": "风险管理"},
        {"name": "平台对比"},
    ],
    "guide": [  # 指南
        {"name": "快速开始"},
        {"name": "开户指南"},
        {"name": "交易指南"},
        {"name": "风险设置"},
        {"name": "高级策略"},
    ],
    "review": [  # 平台评测
        {"name": "安全性分析"},
        {"name": "交易体验"},
        {"name": "费用对比"},
        {"name": "客户服务"},
        {"name": "综合评分"},
    ],
}

def restore_categories():
    """恢复所有分类数据"""
    
    db_engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=db_engine)
    db = Session()
    
    try:
        # 获取所有栏目
        sections = db.query(Section).all()
        section_map = {s.slug: s for s in sections}
        
        print("=" * 60)
        print("开始恢复分类数据...")
        print("=" * 60)
        sys.stdout.flush()
        
        total_added = 0
        
        for section_slug, categories in CATEGORIES_DATA.items():
            section = section_map.get(section_slug)
            
            if not section:
                print(f"栏目 {section_slug} 不存在，跳过")
                sys.stdout.flush()
                continue
            
            print(f"\n栏目: {section.name}")
            
            for cat_data in categories:
                # 检查分类是否已存在
                existing = db.query(Category).filter(
                    Category.section_id == section.id,
                    Category.name == cat_data["name"]
                ).first()
                
                if existing:
                    print(f"  分类已存在: {cat_data['name']}")
                    continue
                
                # 创建新分类
                category = Category(
                    name=cat_data["name"],
                    section_id=section.id,
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(category)
                total_added += 1
                print(f"  添加分类: {cat_data['name']}")
                sys.stdout.flush()
        
        # 提交更改
        db.commit()
        sys.stdout.flush()
        
        print("\n" + "=" * 60)
        print(f"恢复完成! 共添加 {total_added} 个分类")
        print("=" * 60)
        sys.stdout.flush()
        
        # 验证
        print("\n验证结果:")
        for section in sections:
            count = db.query(Category).filter(Category.section_id == section.id).count()
            print(f"  {section.name}: {count} 个分类")
        sys.stdout.flush()
        
        return True
        
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.stderr.flush()
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    try:
        result = restore_categories()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n操作已取消", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"未捕获的错误: {e}", file=sys.stderr)
        sys.exit(1)
