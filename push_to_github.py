#!/usr/bin/env python3
"""
上传项目到 GitHub 的脚本
"""
import os
import sys
import subprocess
import json
from datetime import datetime

def run_command(cmd, cwd=None):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    project_dir = "/Users/ck/Desktop/Project/trustagency"
    os.chdir(project_dir)
    
    print("=" * 60)
    print("📦 GitHub 上传脚本")
    print("=" * 60)
    
    # 1. 检查 Git 状态
    print("\n1️⃣ 检查 Git 状态...")
    code, stdout, stderr = run_command("git status", cwd=project_dir)
    if code == 0:
        print("✅ Git 仓库正常")
        print(stdout)
    else:
        print("❌ Git 错误:")
        print(stderr)
        return 1
    
    # 2. 检查远程配置
    print("\n2️⃣ 检查远程仓库...")
    code, stdout, stderr = run_command("git remote -v", cwd=project_dir)
    if stdout:
        print("✅ 远程仓库配置:")
        print(stdout)
    else:
        print("⚠️ 未配置远程仓库")
    
    # 3. 获取当前分支
    print("\n3️⃣ 获取当前分支...")
    code, stdout, stderr = run_command("git branch", cwd=project_dir)
    print(stdout)
    
    # 4. 检查未提交的更改
    print("\n4️⃣ 检查未提交的更改...")
    code, stdout, stderr = run_command("git status --short", cwd=project_dir)
    if stdout:
        print("📝 未提交的文件:")
        print(stdout)
        
        # 5. 添加所有更改
        print("\n5️⃣ 添加所有更改...")
        code, stdout, stderr = run_command("git add -A", cwd=project_dir)
        if code == 0:
            print("✅ 文件已添加")
        else:
            print("❌ 添加失败:", stderr)
            return 1
        
        # 6. 创建提交
        print("\n6️⃣ 创建提交...")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"chore: 完备的程序版本及当前更改 ({timestamp})"
        code, stdout, stderr = run_command(f'git commit -m "{message}"', cwd=project_dir)
        if code == 0:
            print("✅ 提交成功")
            print(stdout)
        else:
            print("❌ 提交失败:", stderr)
            return 1
    else:
        print("✅ 没有未提交的更改")
    
    # 7. 推送到 GitHub
    print("\n7️⃣ 推送到 GitHub...")
    code, stdout, stderr = run_command("git push origin main", cwd=project_dir)
    if code == 0:
        print("✅ 推送成功！")
        print(stdout)
    else:
        # 尝试推送到 master 分支
        print("⚠️ main 分支推送失败，尝试 master 分支...")
        code, stdout, stderr = run_command("git push origin master", cwd=project_dir)
        if code == 0:
            print("✅ 推送到 master 成功！")
            print(stdout)
        else:
            print("❌ 推送失败:", stderr)
            print("\n需要手动配置远程仓库。执行以下命令:")
            print("git remote add origin https://github.com/Lcking/trustagency.git")
            print("git branch -M main")
            print("git push -u origin main")
            return 1
    
    # 8. 显示项目信息
    print("\n8️⃣ 项目信息统计...")
    code, stdout, stderr = run_command("git log --oneline -10", cwd=project_dir)
    print("📊 最近的提交:")
    print(stdout)
    
    # 9. 统计文件
    code, stdout, stderr = run_command("find . -type f -not -path './.git/*' -not -path './node_modules/*' | wc -l", cwd=project_dir)
    file_count = stdout.strip()
    print(f"📁 项目文件数: {file_count}")
    
    print("\n" + "=" * 60)
    print("✅ 上传完成！")
    print("=" * 60)
    print("\n GitHub 仓库: https://github.com/Lcking/trustagency")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
