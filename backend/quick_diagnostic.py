#!/usr/bin/env python3
"""
快速诊断脚本 - 检查系统状态
"""
import sys
import os

# 添加后端路径
sys.path.insert(0, '/Users/ck/Desktop/Project/trustagency/backend')

print("=" * 70)
print("🔍 系统诊断报告")
print("=" * 70)

# 1. 检查数据库
print("\n1️⃣  检查数据库...")
try:
    from app.database import engine, SessionLocal
    from app.models import Section, Category, Platform, Article
    
    # 尝试连接
    db = SessionLocal()
    
    sections = db.query(Section).count()
    categories = db.query(Category).count()
    platforms = db.query(Platform).count()
    articles = db.query(Article).count()
    
    print(f"   ✅ 数据库连接成功")
    print(f"   • Sections: {sections}")
    print(f"   • Categories: {categories}")
    print(f"   • Platforms: {platforms}")
    print(f"   • Articles: {articles}")
    
    db.close()
except Exception as e:
    print(f"   ❌ 数据库连接失败: {e}")
    sys.exit(1)

# 2. 检查关键文件
print("\n2️⃣  检查关键文件...")
files_to_check = [
    '/Users/ck/Desktop/Project/trustagency/backend/app/main.py',
    '/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html',
    '/Users/ck/Desktop/Project/trustagency/backend/app/schemas/platform_admin.py',
]

for file_path in files_to_check:
    exists = "✅" if os.path.exists(file_path) else "❌"
    print(f"   {exists} {os.path.basename(file_path)}")

# 3. 检查关键修复
print("\n3️⃣  检查关键修复...")
try:
    with open('/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html', 'r') as f:
        content = f.read()
        
    if "const method = currentPlatformId ? 'POST' : 'POST'" in content:
        print("   ✅ HTTP方法修复已应用")
    else:
        print("   ⚠️  HTTP方法修复可能缺失")
        
    if "renderDynamicPlatformForm(formDefinition, existingData = null)" in content:
        print("   ✅ 表单渲染函数已更新")
    else:
        print("   ⚠️  表单渲染函数可能未更新")
except Exception as e:
    print(f"   ❌ 检查失败: {e}")

# 4. 检查Schema
print("\n4️⃣  检查Schema...")
try:
    with open('/Users/ck/Desktop/Project/trustagency/backend/app/schemas/platform_admin.py', 'r') as f:
        content = f.read()
        
    if 'commission_rate: Optional[float] = Field(None, ge=0.0, le=1.0' in content:
        print("   ✅ commission_rate验证已修复")
    else:
        print("   ⚠️  commission_rate验证可能缺失")
        
except Exception as e:
    print(f"   ❌ 检查失败: {e}")

print("\n" + "=" * 70)
print("诊断完成！")
print("=" * 70)
