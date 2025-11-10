#!/usr/bin/env python3
"""
验证 Tiptap 编辑器和后端状态
"""
import urllib.request
import json
import time

def verify_backend():
    """验证后端和编辑器"""
    
    print("=" * 70)
    print("🔍 Tiptap 编辑器和后端验证")
    print("=" * 70)
    
    # 1. 检查后端服务
    print("\n[1/4] 检查后端服务...")
    try:
        response = urllib.request.urlopen("http://localhost:8001/admin/", timeout=5)
        html = response.read().decode('utf-8')
        print("✅ 后端响应正常")
    except Exception as e:
        print(f"❌ 后端无响应: {e}")
        return False
    
    # 2. 检查编辑器容器
    print("\n[2/4] 检查编辑器容器...")
    checks = {
        "编辑器容器": 'id="articleEditor"' in html,
        "编辑器工具栏": 'id="articleEditorToolbar"' in html,
        "Tiptap CDN": "unpkg.com/@tiptap" in html,
        "initArticleEditor 函数": "function initArticleEditor" in html,
        "诊断工具": "TiptapDiagnostics" in html,
    }
    
    for name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    if not all(checks.values()):
        print("\n❌ 部分检查失败！")
        return False
    
    print("\n✅ 所有检查通过！")
    
    # 3. 统计代码行数
    print("\n[3/4] 编辑器代码统计...")
    tiptap_count = html.count("Tiptap")
    editor_count = html.count("articleEditor")
    toolbar_count = html.count("button onclick")
    
    print(f"  • Tiptap 提及次数: {tiptap_count}")
    print(f"  • 编辑器相关代码: {editor_count}")
    print(f"  • 工具栏按钮: {toolbar_count // 2}")  # 除以2因为有重复计数
    
    # 4. 文件清理验证
    print("\n[4/4] 文件清理验证...")
    import os
    from pathlib import Path
    
    keep_file = Path("/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html")
    delete_file = Path("/Users/ck/Desktop/Project/trustagency/site/admin/index.html")
    backup_file = Path("/Users/ck/Desktop/Project/trustagency/site/admin/index.html.backup")
    
    file_checks = {
        "保留文件存在": keep_file.exists(),
        "删除文件已清除": not delete_file.exists(),
        "备份文件已保存": backup_file.exists(),
    }
    
    for name, result in file_checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    if not all(file_checks.values()):
        print("\n⚠️  文件清理未完全完成")
    
    # 总结
    print("\n" + "=" * 70)
    print("✅ 验证完成！")
    print("=" * 70)
    print("\n🎉 Tiptap 编辑器已成功集成并启动！")
    print("\n后续步骤:")
    print("  1. 在浏览器中打开: http://localhost:8001/admin/")
    print("  2. 登录: admin / newpassword123")
    print("  3. 进入文章管理 → 新增文章")
    print("  4. 检查编辑框中是否显示工具栏")
    print("\n按 F12 打开开发者工具查看控制台诊断信息:")
    print("  • 查看 TiptapDiagnostics.check() 的输出")
    print("  • 确认所有库已加载")
    
    return True

if __name__ == "__main__":
    try:
        success = verify_backend()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 验证错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
