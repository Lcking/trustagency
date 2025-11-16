#!/usr/bin/env python3
"""
自动诊断和修复脚本
运行此脚本将自动检查并修复常见问题
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description=""):
    """运行命令并返回结果"""
    try:
        print(f"\n▶️  {description}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}")
            return True, result.stdout
        else:
            print(f"❌ {description}")
            print(f"   错误: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False, str(e)

def main():
    print("=" * 70)
    print("🔍 TrustAgency - 自动诊断和修复系统")
    print("=" * 70)
    
    os.chdir('/Users/ck/Desktop/Project/trustagency/backend')
    
    # 步骤1：检查Python环境
    print("\n1️⃣  检查Python环境...")
    success, output = run_command("python3 --version", "检查Python版本")
    if success:
        print(output.strip())
    else:
        print("❌ Python 3 未安装")
        return False
    
    # 步骤2：检查依赖
    print("\n2️⃣  检查关键依赖...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ 所有关键依赖都已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("   运行: pip install -r requirements.txt")
        return False
    
    # 步骤3：清理缓存
    print("\n3️⃣  清理Python缓存...")
    run_command("find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null", "删除__pycache__")
    run_command("find . -name '*.pyc' -delete 2>/dev/null", "删除.pyc文件")
    print("✅ 缓存已清理")
    
    # 步骤4：检查数据库
    print("\n4️⃣  检查数据库...")
    db_file = Path("trustagency.db")
    if db_file.exists():
        size = db_file.stat().st_size
        if size > 1024:  # > 1KB
            print(f"✅ 数据库文件存在 (大小: {size/1024:.1f}KB)")
        else:
            print(f"⚠️  数据库文件太小 ({size}B)，可能需要重新初始化")
    else:
        print("ℹ️  数据库文件不存在，启动时将自动创建")
    
    # 步骤5：检查关键文件
    print("\n5️⃣  检查关键文件...")
    files = [
        "app/main.py",
        "app/database.py",
        "site/admin/index.html",
        "restore_categories.py",
    ]
    
    for file in files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} 缺失")
    
    # 步骤6：尝试导入主模块
    print("\n6️⃣  尝试导入主模块...")
    sys.path.insert(0, str(Path.cwd()))
    try:
        import app.main
        print("✅ 主模块导入成功")
    except Exception as e:
        print(f"❌ 主模块导入失败: {e}")
        return False
    
    # 步骤7：初始化数据库
    print("\n7️⃣  初始化数据库...")
    try:
        from app.database import init_db
        init_db()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"⚠️  数据库初始化过程中出现错误: {e}")
        # 不一定是失败，可能数据库已存在
    
    # 步骤8：检查分类数据
    print("\n8️⃣  检查分类数据...")
    try:
        from app.database import SessionLocal
        from app.models import Category, Section
        
        db = SessionLocal()
        category_count = db.query(Category).count()
        section_count = db.query(Section).count()
        db.close()
        
        print(f"✅ Sections: {section_count}, Categories: {category_count}")
        
        if category_count == 0 and section_count > 0:
            print("   ⚠️  分类数据为空，建议恢复...")
            print("   运行: python restore_categories.py")
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
    
    print("\n" + "=" * 70)
    print("✅ 诊断完成！")
    print("=" * 70)
    print("\n接下来的步骤:")
    print("1. 如果所有检查都通过，运行:")
    print("   python -m uvicorn app.main:app --reload --port 8000")
    print("\n2. 打开浏览器访问:")
    print("   http://localhost:8000/admin/")
    print("\n3. 如果分类数据为空，运行:")
    print("   python restore_categories.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
