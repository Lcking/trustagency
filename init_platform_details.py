#!/usr/bin/env python3
"""
平台详情数据初始化脚本
将结构化的平台详情数据插入到数据库
"""
import sqlite3
import json
from pathlib import Path
from platform_details_template import PLATFORM_DETAILS_MAP

db_path = Path("/Users/ck/Desktop/Project/trustagency/backend/trustagency.db")

def init_platform_details():
    """初始化平台详情数据"""
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("📝 开始初始化平台详情数据...")
        print("-" * 70)
        
        for slug, (platform_id, details) in PLATFORM_DETAILS_MAP.items():
            print(f"\n  → 更新平台: {slug} (ID: {platform_id})")
            
            # 构建UPDATE SQL语句
            update_sql = """
                UPDATE platforms 
                SET 
                    why_choose = ?,
                    trading_conditions = ?,
                    fee_advantages = ?,
                    account_types = ?,
                    trading_tools = ?,
                    opening_steps = ?,
                    security_measures = ?,
                    customer_support = ?,
                    learning_resources = ?,
                    platform_type = ?,
                    platform_badges = ?
                WHERE id = ?
            """
            
            # 准备数据
            data = (
                details.get("why_choose"),
                details.get("trading_conditions"),
                details.get("fee_advantages"),
                details.get("account_types"),
                details.get("trading_tools"),
                details.get("opening_steps"),
                details.get("security_measures"),
                details.get("customer_support"),
                details.get("learning_resources"),
                details.get("platform_type"),
                details.get("platform_badges"),
                platform_id
            )
            
            cursor.execute(update_sql, data)
            print(f"    ✅ 数据更新成功")
        
        # 提交更改
        conn.commit()
        
        # 验证数据
        print(f"\n" + "=" * 70)
        print("📋 数据验证:")
        print("-" * 70)
        
        for slug, (platform_id, _) in PLATFORM_DETAILS_MAP.items():
            cursor.execute("""
                SELECT id, name, platform_type, 
                       CASE WHEN account_types IS NOT NULL THEN 'Yes' ELSE 'No' END as has_accounts,
                       CASE WHEN opening_steps IS NOT NULL THEN 'Yes' ELSE 'No' END as has_steps
                FROM platforms 
                WHERE id = ?
            """, (platform_id,))
            
            row = cursor.fetchone()
            if row:
                pid, name, ptype, has_accounts, has_steps = row
                print(f"  ✅ {name}")
                print(f"     - 类型: {ptype}")
                print(f"     - 账户类型: {'已配置' if has_accounts == 'Yes' else '未配置'}")
                print(f"     - 开户步骤: {'已配置' if has_steps == 'Yes' else '未配置'}")
        
        conn.close()
        print(f"\n✅ 平台详情数据初始化完成！")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = init_platform_details()
    sys.exit(0 if success else 1)
