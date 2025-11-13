#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证脚本 - 检查系统是否准备就绪
"""
import sys
import os
from pathlib import Path

# 添加后端目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

def check_imports():
    """检查必要的导入"""
    print("检查导入...")
    try:
        from app.database import SessionLocal, engine
        from app.models import Platform
        print("✓ 导入成功")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def check_database():
    """检查数据库连接"""
    print("\n检查数据库连接...")
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✓ 数据库连接成功")
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def check_platforms():
    """检查平台数据"""
    print("\n检查平台数据...")
    try:
        from app.database import SessionLocal
        from app.models import Platform
        
        db = SessionLocal()
        platforms = db.query(Platform).all()
        
        print(f"✓ 找到 {len(platforms)} 个平台:")
        for p in platforms:
            # 检查新字段
            fields = ['why_choose', 'account_types', 'fee_table']
            has_details = sum(1 for f in fields if getattr(p, f, None))
            print(f"  - {p.name} ({p.slug}): {has_details}/3 详情字段已填充")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_api_routes():
    """检查API路由"""
    print("\n检查API路由...")
    try:
        from app.routes import admin_platforms
        
        # 检查是否有新路由
        routes = [route.path for route in admin_platforms.router.routes]
        print(f"✓ 发现 {len(routes)} 个新API路由:")
        for route in routes:
            print(f"  - {route}")
        
        return True
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("系统验证检查")
    print("=" * 50)
    
    checks = [
        ("导入检查", check_imports),
        ("数据库检查", check_database),
        ("平台数据检查", check_platforms),
        ("API路由检查", check_api_routes),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} 发生异常: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("验证总结")
    print("=" * 50)
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    if passed == total:
        print(f"\n✓ 所有检查都通过了！({passed}/{total})")
        print("\n后续步骤：")
        print("1. 运行初始化脚本: python scripts/init_platform_data.py")
        print("2. 启动后端服务: uvicorn app.main:app --reload")
        print("3. 访问API文档: http://localhost:8001/api/docs")
        return 0
    else:
        print(f"\n✗ 有 {total - passed} 个检查失败，需要修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
