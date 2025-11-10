#!/usr/bin/env python3
"""
Admin 访问修复验证脚本
"""
import subprocess
import time
import requests
import sys

def run_command(cmd, description=""):
    """运行命令"""
    print(f"\n{'='*50}")
    if description:
        print(f"📋 {description}")
    print(f"{'='*50}")
    print(f"$ {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def check_file_exists():
    """检查 admin 文件是否存在"""
    import os
    path = "/Users/ck/Desktop/Project/trustagency/backend/site/admin/index.html"
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✓ Admin 文件存在: {size} 字节")
        return True
    else:
        print(f"✗ Admin 文件不存在: {path}")
        return False

def check_endpoint(url, description=""):
    """检查端点"""
    print(f"\n📝 检查: {description}")
    print(f"URL: {url}\n")
    try:
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 检查是否返回 HTML
            if "<!DOCTYPE" in response.text or "<html" in response.text:
                print("✓ 返回 HTML 内容")
                print(f"前 200 字符:\n{response.text[:200]}...")
                return True
            else:
                print(f"内容: {response.text[:200]}")
                return False
        else:
            print(f"❌ 错误: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║          Admin 访问问题修复 - 完整验证流程               ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # 1. 检查文件
    print("\n[1/5] 检查 admin 文件...")
    if not check_file_exists():
        print("❌ Admin 文件缺失，无法继续")
        return False
    
    # 2. 停止容器
    print("\n[2/5] 停止容器...")
    run_command("cd /Users/ck/Desktop/Project/trustagency && docker-compose down", "停止所有容器")
    time.sleep(2)
    
    # 3. 启动容器
    print("\n[3/5] 启动容器...")
    run_command("cd /Users/ck/Desktop/Project/trustagency && docker-compose up -d", "重新启动容器")
    
    print("\n⏳ 等待容器启动... (10 秒)")
    time.sleep(10)
    
    # 4. 检查容器状态
    print("\n[4/5] 检查容器状态...")
    run_command("docker-compose -f /Users/ck/Desktop/Project/trustagency/docker-compose.yml ps", "查看容器状态")
    
    # 5. 测试端点
    print("\n[5/5] 测试访问端点...")
    
    print("\n" + "="*50)
    print("📊 测试结果总结")
    print("="*50)
    
    tests = [
        ("http://localhost:8001/admin/", "后端 FastAPI - /admin/ 路由"),
        ("http://localhost:8001/api/health", "后端 FastAPI - 健康检查"),
        ("http://localhost/admin/", "前端 Nginx - /admin/ 路由"),
        ("http://localhost/", "前端 Nginx - 首页"),
    ]
    
    results = {}
    for url, desc in tests:
        results[desc] = check_endpoint(url, desc)
        time.sleep(1)
    
    # 总结
    print("\n" + "="*50)
    print("✅ 完整性报告")
    print("="*50)
    
    for desc, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"{status} {desc}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*50)
    if all_passed:
        print("✅ 所有测试通过！Admin 面板应该可以正常访问了。")
        print("\n访问方式:")
        print("  - 前端: http://localhost/admin/")
        print("  - 后端: http://localhost:8001/admin/")
        print("\n默认凭证:")
        print("  - 用户名: admin")
        print("  - 密码: admin123")
    else:
        print("⚠️  某些测试失败。请检查容器日志。")
        print("\n查看日志的命令:")
        print("  docker-compose -f /Users/ck/Desktop/Project/trustagency/docker-compose.yml logs backend")
        print("  docker-compose -f /Users/ck/Desktop/Project/trustagency/docker-compose.yml logs frontend")
    print("="*50)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ 操作被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
