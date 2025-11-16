#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接使用 SQLite 填充分类 - 绕过 ORM 复杂性
这个脚本更轻量级，不会导致 PTY 卡住
"""
import sys
import sqlite3
from datetime import datetime

DB_PATH = 'trustagency.db'

CATEGORIES_DATA = {
    "faq": [
        "账户问题", "交易问题", "安全问题", "费用问题", "其他问题",
    ],
    "wiki": [
        "基础概念", "交易技巧", "市场分析", "风险管理", "平台对比",
    ],
    "guide": [
        "快速开始", "开户指南", "交易指南", "风险设置", "高级策略",
    ],
    "review": [
        "安全性分析", "交易体验", "费用对比", "客户服务", "综合评分",
    ],
}

SECTION_MAP = {
    "faq": 1,
    "wiki": 2,
    "guide": 3,
    "review": 4,
}

def populate_categories():
    """使用 SQL 直接填充分类"""
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        
        print("连接数据库: " + DB_PATH)
        sys.stdout.flush()
        
        total_added = 0
        now = datetime.now().isoformat()
        
        for section_slug, cat_names in CATEGORIES_DATA.items():
            section_id = SECTION_MAP[section_slug]
            print(f"\n处理栏目: {section_slug} (ID={section_id})")
            
            for sort_order, cat_name in enumerate(cat_names, 1):
                try:
                    cur.execute(
                        """INSERT OR IGNORE INTO categories 
                           (name, section_id, sort_order, is_active, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (cat_name, section_id, sort_order, 1, now, now)
                    )
                    if cur.rowcount > 0:
                        total_added += 1
                        print(f"  添加: {cat_name}")
                    else:
                        print(f"  已存在: {cat_name}")
                    sys.stdout.flush()
                except Exception as e:
                    print(f"  错误: {cat_name} - {str(e)}")
                    sys.stdout.flush()
        
        con.commit()
        sys.stdout.flush()
        
        print(f"\n完成! 共添加 {total_added} 个分类")
        sys.stdout.flush()
        
        # 验证
        print("\n验证结果:")
        cur.execute("""SELECT s.name, COUNT(c.id) FROM sections s 
                       LEFT JOIN categories c ON s.id = c.section_id 
                       GROUP BY s.id""")
        for section_name, count in cur.fetchall():
            print(f"  {section_name}: {count} 个分类")
        sys.stdout.flush()
        
        con.close()
        return True
        
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.stderr.flush()
        return False

if __name__ == "__main__":
    try:
        result = populate_categories()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n已取消", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"未捕获错误: {e}", file=sys.stderr)
        sys.exit(1)
