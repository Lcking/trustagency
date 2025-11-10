#!/usr/bin/env python3
"""
后端自动启动和验证脚本 - 支持后台模式
"""
import subprocess
import time
import os
import signal
import sys
from pathlib import Path

class BackendAutoStart:
    def __init__(self):
        self.backend_dir = Path("/Users/ck/Desktop/Project/trustagency/backend")
        self.log_file = Path("/Users/ck/Desktop/Project/trustagency/backend_startup.log")
        
    def log(self, msg):
        """记录日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")
    
    def clean_old_processes(self):
        """清理旧进程"""
        self.log("清理旧进程...")
        os.system('pkill -9 -f "uvicorn" 2>/dev/null')
        time.sleep(1)
    
    def start_backend(self):
        """启动后端服务"""
        self.log("启动后端服务...")
        
        cmd = [
            f"{self.backend_dir}/venv/bin/python",
            "-m", "uvicorn",
            "app.main:app",
            "--port", "8001",
            "--reload"
        ]
        
        # 后台启动
        process = subprocess.Popen(
            cmd,
            stdout=open(self.log_file, "a"),
            stderr=subprocess.STDOUT,
            cwd=str(self.backend_dir)
        )
        
        self.log(f"后端进程已启动 (PID: {process.pid})")
        return process
    
    def wait_for_ready(self, timeout=10):
        """等待后端就绪"""
        self.log(f"等待后端就绪 (最多 {timeout}秒)...")
        
        import urllib.request
        import urllib.error
        
        start = time.time()
        while time.time() - start < timeout:
            try:
                response = urllib.request.urlopen("http://localhost:8001/api/debug/admin-users", timeout=2)
                if response.status == 200:
                    self.log("✅ 后端已就绪")
                    return True
            except (urllib.error.URLError, urllib.error.HTTPError):
                pass
            
            time.sleep(0.5)
        
        self.log("❌ 后端启动超时")
        return False
    
    def verify_admin_page(self):
        """验证admin页面"""
        self.log("验证admin页面...")
        
        import urllib.request
        import urllib.error
        
        try:
            response = urllib.request.urlopen("http://localhost:8001/admin/", timeout=5)
            html = response.read().decode('utf-8')
            
            if response.status == 200 and 'id="articleEditor"' in html:
                self.log("✅ admin页面验证通过")
                return True
            else:
                self.log(f"❌ admin页面验证失败 (状态: {response.status})")
                return False
                
        except Exception as e:
            self.log(f"❌ admin页面验证失败: {e}")
            return False
    
    def run(self):
        """运行启动流程"""
        self.log("=" * 70)
        self.log("后端自动启动脚本 - 开始")
        self.log("=" * 70)
        
        # 清理
        self.clean_old_processes()
        time.sleep(1)
        
        # 启动
        self.start_backend()
        time.sleep(2)
        
        # 等待就绪
        if not self.wait_for_ready(timeout=15):
            self.log("后端启动失败，请检查日志")
            return False
        
        # 验证
        if not self.verify_admin_page():
            self.log("页面验证失败，请检查配置")
            return False
        
        # 成功
        self.log("=" * 70)
        self.log("✅ 后端启动成功！")
        self.log("=" * 70)
        self.log(f"📝 日志文件: {self.log_file}")
        self.log("🌐 访问地址: http://localhost:8001/admin/")
        self.log("👤 用户: admin")
        self.log("🔑 密码: newpassword123")
        self.log("⏹️  停止服务: pkill -f 'uvicorn'")
        
        return True

if __name__ == "__main__":
    try:
        starter = BackendAutoStart()
        success = starter.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
