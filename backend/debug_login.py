#!/usr/bin/env python3
"""
调试登录问题 - 检查密码验证和数据库
"""
import sqlite3
import sys
from pathlib import Path

# 设置路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.utils.security import pwd_context, verify_password, hash_password

print("=" * 60)
print("🔍 登录调试工具")
print("=" * 60)

# 检查密码哈希
print("\n1️⃣  测试密码哈希生成...")
test_password = "admin123"
hashed = pwd_context.hash(test_password)
print(f"   原始密码: {test_password}")
print(f"   哈希值: {hashed[:50]}...")
print(f"   验证结果: {verify_password(test_password, hashed)}")

# 检查数据库
print("\n2️⃣  检查数据库中的管理员用户...")
db_path = backend_dir / "trustagency.db"
if not db_path.exists():
    print(f"   ❌ 数据库不存在: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    cursor.execute("SELECT username, hashed_password, is_active FROM admin_users WHERE username='admin'")
    row = cursor.fetchone()
    
    if not row:
        print("   ❌ 未找到 admin 用户")
        sys.exit(1)
    
    username, db_hashed, is_active = row
    print(f"   用户名: {username}")
    print(f"   活跃: {is_active}")
    print(f"   数据库中的哈希值: {db_hashed[:50]}...")
    
    # 验证密码
    print("\n3️⃣  验证密码...")
    try:
        verify_result = verify_password(test_password, db_hashed)
        print(f"   验证结果: {verify_result}")
        if verify_result:
            print("   ✅ 密码正确！")
        else:
            print("   ❌ 密码不匹配！")
    except Exception as e:
        print(f"   ❌ 验证失败: {e}")
    
finally:
    conn.close()

print("\n" + "=" * 60)
print("✅ 调试完成")
print("=" * 60)
