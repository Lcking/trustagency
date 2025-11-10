#!/usr/bin/env python3
"""
快速验证脚本 - 检查清理是否成功
"""
from pathlib import Path

print("\n" + "=" * 80)
print("🔍 快速验证 Admin 清理状态")
print("=" * 80 + "\n")

# 检查文件
keep_file = Path("/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html")
deleted_dir = Path("/Users/ck/Desktop/Project/trustagency/site/admin")

print("📋 文件状态检查:\n")

# 1. 检查后端文件
if keep_file.exists():
    size = keep_file.stat().st_size
    lines = len(keep_file.read_text().split('\n'))
    print(f"✅ backend/site/admin/index.html")
    print(f"   📊 大小: {size:,} 字节")
    print(f"   📝 行数: {lines} 行\n")
else:
    print(f"❌ backend/site/admin/index.html - 文件丢失!\n")

# 2. 检查冗余目录
if not deleted_dir.exists():
    print(f"✅ site/admin/ 目录已删除\n")
else:
    print(f"❌ site/admin/ 目录仍然存在\n")

# 3. 检查关键功能
if keep_file.exists():
    content = keep_file.read_text()
    print("🔧 功能检查:\n")
    checks = [
        ("Tiptap CDN", "unpkg.com/@tiptap/core" in content),
        ("编辑器容器", 'id="articleEditor"' in content),
        ("初始化函数", "initArticleEditor" in content),
        ("诊断工具", "TiptapDiagnostics" in content),
    ]
    
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    print()

# 总结
print("=" * 80)
all_ok = keep_file.exists() and not deleted_dir.exists()
if all_ok:
    print("✅ 清理验证成功！系统已准备好。\n")
    print("🚀 下一步:")
    print("   1. 启动后端: python -m uvicorn app.main:app --port 8001")
    print("   2. 访问: http://localhost:8001/admin/")
    print("   3. 测试编辑器功能\n")
else:
    print("❌ 清理验证失败！请检查上述项目。\n")

print("=" * 80 + "\n")
