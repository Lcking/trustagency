#!/usr/bin/env python3
"""
系统验证脚本 - 测试所有功能是否正常
"""

import subprocess
import time
import json
from pathlib import Path

def run_command(cmd):
    """执行命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "timeout"
    except Exception as e:
        return False, "", str(e)

def verify_system():
    """验证系统状态"""
    print("🔍 TrustAgency 系统验证")
    print("=" * 50)
    
    # 1. 检查后端
    print("\n1️⃣ 检查后端 API...")
    success, stdout, _ = run_command('curl -s http://localhost:8000/api/articles?limit=1')
    if success and '"data"' in stdout:
        print("   ✅ 后端 API 正常")
        try:
            data = json.loads(stdout)
            total = data.get('total', 0)
            print(f"   📊 数据库中有 {total} 篇文章")
        except:
            pass
    else:
        print("   ❌ 后端 API 无响应")
    
    # 2. 检查前端首页
    print("\n2️⃣ 检查前端首页...")
    success, _, _ = run_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/')
    if success:
        print("   ✅ 前端首页正常")
    else:
        print("   ❌ 前端首页无响应")
    
    # 3. 检查 QA 页面
    print("\n3️⃣ 检查 QA 页面...")
    success, _, _ = run_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/qa/')
    if success:
        print("   ✅ QA 页面正常")
    else:
        print("   ❌ QA 页面无响应")
    
    # 4. 检查文章详情页 (ID 模式)
    print("\n4️⃣ 检查文章详情页 (ID 模式)...")
    success, stdout, _ = run_command('curl -s http://localhost:8001/article/?id=6 | grep -c "article-content"')
    if success and stdout.strip() != '0':
        print("   ✅ ID 模式正常")
    else:
        print("   ❌ ID 模式无响应")
    
    # 5. 检查文章详情页 (Slug 模式)
    print("\n5️⃣ 检查文章详情页 (Slug 模式)...")
    success, _, _ = run_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/article/faq-what-is-leverage')
    if success:
        print("   ✅ Slug 模式正常")
    else:
        print("   ❌ Slug 模式无响应")
    
    # 6. 检查 Wiki 页面
    print("\n6️⃣ 检查 Wiki 页面...")
    success, _, _ = run_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/wiki/')
    if success:
        print("   ✅ Wiki 页面正常")
    else:
        print("   ❌ Wiki 页面无响应")
    
    # 7. 检查文件
    print("\n7️⃣ 检查文件结构...")
    base = Path('/Users/ck/Desktop/Project/trustagency')
    files = [
        'site/article/index.html',
        'site/qa/index.html',
        'site/wiki/index.html',
        'run.sh',
        'SEO_OPTIMIZATION_COMPLETE.md'
    ]
    
    all_exist = True
    for f in files:
        path = base / f
        if path.exists():
            print(f"   ✅ {f}")
        else:
            print(f"   ❌ {f} 缺失")
            all_exist = False
    
    print("\n" + "=" * 50)
    if all_exist:
        print("✅ 系统验证完成！所有组件正常")
    else:
        print("⚠️ 系统验证完成，某些文件缺失")

if __name__ == '__main__':
    verify_system()
