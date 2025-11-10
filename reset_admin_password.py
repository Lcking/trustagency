#!/usr/bin/env python3
"""
重置管理员密码脚本
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import AdminUser
from app.utils.security import hash_password
from datetime import datetime

def reset_admin_password():
    db = SessionLocal()
    try:
        # 查找admin用户
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        
        if not admin:
            print("❌ 管理员用户不存在")
            return False
        
        # 重置密码为 admin123
        admin.hashed_password = hash_password("admin123")
        db.commit()
        
        print(f"✅ 管理员密码已重置为: admin123")
        print(f"   用户ID: {admin.id}")
        print(f"   用户名: {admin.username}")
        print(f"   邮箱: {admin.email}")
        return True
        
    except Exception as e:
        print(f"❌ 出错: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
