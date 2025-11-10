#!/usr/bin/env python3
"""
清理重复的 admin 页面文件脚本
"""
import os
import shutil
from pathlib import Path

def cleanup_duplicate_admin():
    """删除重复的 admin 页面文件"""
    
    print("=" * 70)
    print("🧹 TrustAgency Admin 页面清理工具")
    print("=" * 70)
    
    # 要删除的文件
    redundant_file = Path("/Users/ck/Desktop/Project/trustagency/site/admin/index.html")
    keep_file = Path("/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html")
    
    print("\n📋 清理计划:")
    print(f"  ❌ 删除: {redundant_file}")
    print(f"  ✅ 保留: {keep_file}")
    
    # 验证文件存在
    print("\n✓ 验证文件状态...")
    
    if not keep_file.exists():
        print(f"❌ 错误: 保留的文件不存在！{keep_file}")
        return False
    
    print(f"  ✅ 保留文件存在: {keep_file.stat().st_size} 字节")
    
    if not redundant_file.exists():
        print(f"  ℹ️  冗余文件已不存在: {redundant_file}")
        return True
    
    print(f"  ⚠️  冗余文件存在: {redundant_file.stat().st_size} 字节")
    
    # 验证两个文件是否相同
    print("\n✓ 比较文件内容...")
    keep_content = keep_file.read_text(encoding='utf-8')
    redundant_content = redundant_file.read_text(encoding='utf-8')
    
    if keep_content == redundant_content:
        print("  ✅ 两个文件内容完全相同")
    else:
        print("  ❌ 两个文件内容不同！")
        print(f"     保留: {len(keep_content)} 字节")
        print(f"     冗余: {len(redundant_content)} 字节")
        print("     不建议继续删除！")
        return False
    
    # 备份（可选）
    backup_file = redundant_file.with_suffix('.html.backup')
    print(f"\n✓ 创建备份...")
    shutil.copy2(redundant_file, backup_file)
    print(f"  ✅ 备份已创建: {backup_file}")
    
    # 删除冗余文件
    print(f"\n✓ 删除冗余文件...")
    try:
        redundant_file.unlink()
        print(f"  ✅ 文件已删除: {redundant_file}")
    except Exception as e:
        print(f"  ❌ 删除失败: {e}")
        return False
    
    # 验证删除
    if redundant_file.exists():
        print(f"  ❌ 验证失败：文件仍然存在")
        return False
    
    print(f"  ✅ 验证通过：文件已成功删除")
    
    # 检查后端配置
    print("\n✓ 验证后端配置...")
    main_py = Path("/Users/ck/Desktop/Project/trustagency/backend/app/main.py")
    main_content = main_py.read_text()
    
    if 'backend/site/admin' in main_content or '"site" / "admin"' in main_content:
        print(f"  ✅ 后端挂载正确使用 backend/site/admin")
    else:
        print(f"  ⚠️  无法确认后端挂载路径")
    
    # 总结
    print("\n" + "=" * 70)
    print("✅ 清理完成！")
    print("=" * 70)
    print("\n📊 总结:")
    print("  ✅ 已删除: site/admin/index.html")
    print("  ✅ 保留: backend/site/admin/index.html（唯一有效版本）")
    print("  ✅ 已备份: site/admin/index.html.backup")
    print("  ✅ 脚本已更新: verify_admin_fix.py, diagnose.py")
    
    print("\n🚀 后续步骤:")
    print("  1. 重启后端服务: pkill -f 'uvicorn app.main:app'")
    print("  2. 重启后端: cd /Users/ck/Desktop/Project/trustagency/backend")
    print("              python -m uvicorn app.main:app --port 8001 --reload")
    print("  3. 验证功能: http://localhost:8001/admin/")
    print("  4. 测试编辑器: 新增文章 -> 检查工具栏是否显示")
    
    return True

if __name__ == "__main__":
    try:
        success = cleanup_duplicate_admin()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  操作被中断")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ 出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
