#!/usr/bin/env python3
"""
诊断脚本 - 检查 main.py 中的 StaticFiles 挂载是否正确
"""

import subprocess
import time
import sys
from pathlib import Path

def check_main_py():
    """检查 main.py 的内容"""
    print("\n[1] 检查 main.py 的内容...")
    main_py = Path("/Users/ck/Desktop/Project/trustagency/backend/app/main.py")
    
    if not main_py.exists():
        print("❌ main.py 不存在")
        return False
    
    content = main_py.read_text()
    
    # 检查 StaticFiles 导入
    if "from fastapi.staticfiles import StaticFiles" not in content:
        print("❌ 缺少 StaticFiles 导入")
        return False
    print("✓ StaticFiles 导入正确")
    
    # 检查挂载
    if 'app.mount("/admin"' not in content:
        print("❌ 缺少 app.mount('/admin')")
        return False
    print("✓ StaticFiles 挂载存在")
    
    # 检查顺序 - app.mount 应该在 app.include_router 之前
    mount_pos = content.find('app.mount("/admin"')
    router_pos = content.find('app.include_router')
    
    if mount_pos > router_pos:
        print(f"❌ 挂载位置错误！app.mount 在第 {content[:mount_pos].count(chr(10))+1} 行，"
              f"app.include_router 在第 {content[:router_pos].count(chr(10))+1} 行")
        return False
    
    print(f"✓ 挂载顺序正确 (app.mount 在第 {content[:mount_pos].count(chr(10))+1} 行，"
          f"app.include_router 在第 {content[:router_pos].count(chr(10))+1} 行)")
    
    # 检查 CORS 配置
    if '"http://localhost:80"' not in content and "'http://localhost:80'" not in content:
        print("⚠️  CORS 配置中可能缺少 http://localhost:80")
    else:
        print("✓ CORS 配置包含 localhost:80")
    
    return True

def check_admin_file():
    """检查 admin HTML 文件是否存在"""
    print("\n[2] 检查 admin HTML 文件...")
    admin_file = Path("/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html")
    
    if not admin_file.exists():
        print("❌ admin/index.html 不存在")
        return False
    
    size = admin_file.stat().st_size
    print(f"✓ admin/index.html 存在 ({size} 字节)")
    return True

def check_container_status():
    """检查容器状态"""
    print("\n[3] 检查容器状态...")
    try:
        result = subprocess.run(
            ["docker-compose", "-f", "/Users/ck/Desktop/Project/trustagency/docker-compose.yml", "ps"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(result.stdout)
        
        if "trustagency-backend" in result.stdout and "Up" in result.stdout:
            print("✓ 后端容器运行中")
            return True
        else:
            print("❌ 后端容器未运行")
            return False
    except Exception as e:
        print(f"❌ 无法检查容器状态: {e}")
        return False

def test_endpoint():
    """测试 /admin/ 端点"""
    print("\n[4] 测试 /admin/ 端点...")
    try:
        result = subprocess.run(
            ["curl", "-s", "-i", "http://localhost:8001/admin/"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout
        print(output[:500])
        
        if "200 OK" in output or "200 OK" in output:
            print("✓ 返回 200 OK")
            return True
        elif "404" in output:
            print("❌ 返回 404 Not Found")
            return False
        else:
            print(f"❓ 返回未知状态")
            return False
    except Exception as e:
        print(f"❌ 无法测试端点: {e}")
        return False

def restart_backend():
    """重启后端容器"""
    print("\n[5] 重启后端容器...")
    try:
        subprocess.run(
            ["docker-compose", "-f", "/Users/ck/Desktop/Project/trustagency/docker-compose.yml", "restart", "backend"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print("✓ 已发送重启命令")
        print("等待容器重启... 10 秒")
        time.sleep(10)
        return True
    except Exception as e:
        print(f"❌ 无法重启容器: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  Admin 访问问题 - 深度诊断工具")
    print("="*60)
    
    try:
        # 检查代码
        if not check_main_py():
            print("\n❌ main.py 配置有问题，需要修复！")
            sys.exit(1)
        
        if not check_admin_file():
            print("\n❌ admin 文件不存在！")
            sys.exit(1)
        
        # 检查容器
        if not check_container_status():
            print("\n⚠️  容器不运行，请先启动: docker-compose up -d")
            sys.exit(1)
        
        # 测试端点
        if not test_endpoint():
            print("\n⚠️  端点返回错误，尝试重启容器...")
            if restart_backend():
                print("\n再次测试端点...")
                time.sleep(5)
                test_endpoint()
        
        print("\n" + "="*60)
        print("  诊断完成")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
