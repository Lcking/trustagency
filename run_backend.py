#!/usr/bin/env python3
"""
完整的后端启动和验证脚本
"""
import subprocess
import time
import os
import sys
import signal
from pathlib import Path

class BackendManager:
    def __init__(self):
        self.backend_dir = Path("/Users/ck/Desktop/Project/trustagency/backend")
        self.process = None
        
    def kill_existing(self):
        """杀死现有uvicorn进程"""
        print("⏹️  停止现有进程...")
        os.system('pkill -9 -f "uvicorn" 2>/dev/null')
        os.system('pkill -9 python 2>/dev/null')
        time.sleep(2)
    
    def start(self):
        """启动后端"""
        print("🚀 启动后端服务...")
        os.chdir(self.backend_dir)
        
        cmd = [
            f"{self.backend_dir}/venv/bin/python",
            "-m", "uvicorn",
            "app.main:app",
            "--port", "8001",
            "--reload",
            "--log-level", "info"
        ]
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        print(f"✅ 后端进程已启动 (PID: {self.process.pid})")
        time.sleep(3)
        
        return self.process.poll() is None
    
    def verify(self):
        """验证后端和编辑器"""
        print("\n🔍 验证后端...")
        
        try:
            import urllib.request
            
            # 测试admin路由
            print("  [1/3] 测试 /admin/ 路由...")
            try:
                response = urllib.request.urlopen("http://localhost:8001/admin/", timeout=5)
                html = response.read().decode('utf-8')
                
                if 'id="articleEditor"' in html:
                    print("  ✅ 编辑器容器存在")
                    return True
                else:
                    print("  ❌ 编辑器容器不存在")
                    print(f"  响应: {html[:200]}")
                    return False
                    
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(f"  ❌ 404 Not Found")
                    body = e.read().decode('utf-8')
                    print(f"  响应: {body}")
                    return False
                else:
                    print(f"  ❌ HTTP {e.code}")
                    return False
                    
        except Exception as e:
            print(f"  ❌ 验证失败: {e}")
            return False
    
    def run_interactive(self):
        """运行后端（交互模式）"""
        print("\n" + "=" * 70)
        print("🎯 后端运行中")
        print("=" * 70)
        print(f"🌐 访问地址: http://localhost:8001/admin/")
        print(f"👤 用户: admin")
        print(f"🔑 密码: newpassword123")
        print("\n⏹️  按 Ctrl+C 停止服务\n")
        print("=" * 70 + "\n")
        
        try:
            while True:
                time.sleep(1)
                if self.process.poll() is not None:
                    print("\n❌ 后端进程已停止")
                    break
        except KeyboardInterrupt:
            print("\n\n⏹️  停止后端...")
            self.process.terminate()
            self.process.wait(timeout=5)
            print("✅ 后端已停止")

def main():
    manager = BackendManager()
    
    # 停止现有进程
    manager.kill_existing()
    
    # 启动后端
    if not manager.start():
        print("❌ 后端启动失败")
        return False
    
    # 验证
    if manager.verify():
        print("\n✅ 后端验证通过！")
        manager.run_interactive()
        return True
    else:
        print("\n❌ 后端验证失败")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
