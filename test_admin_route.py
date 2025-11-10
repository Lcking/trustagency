#!/usr/bin/env python3
"""
快速测试脚本 - 检查admin路由
"""
import urllib.request
import urllib.error
import sys

def test_admin_route():
    """测试 /admin/ 路由"""
    print("🔍 测试后端连接...")
    
    try:
        # 先测试简单API
        response = urllib.request.urlopen("http://localhost:8001/api/debug/admin-users", timeout=5)
        if response.status == 200:
            print("✅ API 工作正常")
        else:
            print(f"❌ API 返回 {response.status}")
            
    except Exception as e:
        print(f"❌ 无法连接后端: {e}")
        return False
    
    # 测试 admin 路由
    print("\n🔍 测试 /admin/ 路由...")
    try:
        response = urllib.request.urlopen("http://localhost:8001/admin/", timeout=5)
        
        print(f"   状态码: {response.status}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status == 200:
            html = response.read().decode('utf-8')
            
            # 检查是否是HTML
            if "text/html" in response.headers.get("content-type", ""):
                print("✅ 返回 HTML")
                
                # 检查关键元素
                if 'id="articleEditor"' in html:
                    print("✅ 找到编辑器容器")
                    return True
                else:
                    print("❌ 编辑器容器不存在")
                    print(f"   响应开头: {html[:200]}")
                    return False
            else:
                print("❌ 不是 HTML")
                print(f"   响应: {html[:200]}")
                return False
        else:
            print(f"❌ HTTP {response.status}")
            return False
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}")
        try:
            body = e.read().decode('utf-8')
            print(f"   响应: {body[:200]}")
        except:
            pass
        return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_admin_route()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  已取消")
        sys.exit(1)
