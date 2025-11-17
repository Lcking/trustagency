#!/usr/bin/env python3
"""
将根目录的 MD/TXT 文件整理到 kanban/archives 目录
按任务、会话、Bug修复等分类
"""

import os
import shutil
from pathlib import Path

REPO_ROOT = Path("/Users/ck/Desktop/Project/trustagency")
KANBAN_DIR = REPO_ROOT / "kanban" / "archives"

# 定义分类规则
CATEGORIES = {
    "tasks": [
        # TASK_* 开头的文件
        lambda f: f.startswith("TASK_"),
    ],
    "sessions": [
        # 会话总结
        lambda f: "SESSION" in f.upper(),
        lambda f: "PROGRESS" in f.upper() and "2025" in f,
        lambda f: "STATUS" in f.upper() and "2025" in f,
        lambda f: f.startswith("A") and len(f) > 1 and f[1].isdigit() and "COMPLETION" in f,  # A2_COMPLETION 等
        lambda f: f.startswith("A") and len(f) > 1 and f[1].isdigit() and "SUMMARY" in f,
        lambda f: f.startswith("A") and len(f) > 1 and f[1].isdigit() and "REPORT" in f,
    ],
    "bug_fixes": [
        lambda f: "BUG" in f.upper(),
        lambda f: "FIX" in f.upper(),
    ],
    "deployments": [
        lambda f: "DEPLOY" in f.upper(),
        lambda f: "DOCKER" in f.upper(),
        lambda f: "PORT" in f.upper(),
        lambda f: "PRODUCTION" in f.upper(),
        lambda f: "RESOURCE_ASSESSMENT" in f,
    ],
    "verification": [
        lambda f: "ACCEPTANCE" in f.upper(),
        lambda f: "VERIFICATION" in f.upper(),
        lambda f: "VERIFY" in f.upper(),
        lambda f: "CODE_REVIEW" in f.upper(),
        lambda f: "ACCEPTANCE_TEST" in f.upper(),
    ],
    "frontend": [
        lambda f: "FRONTEND" in f.upper(),
        lambda f: "API_INTEGRATION" in f.upper(),
        lambda f: "SEO" in f.upper(),
        lambda f: "QUALITY_ISSUE" in f.upper(),
        lambda f: "QUALITY_FIX" in f.upper(),
        lambda f: "PLATFORM_LOADING" in f.upper(),
    ],
    "backend": [
        lambda f: "INTEGRATION" in f.upper() and "BACKEND" in f.upper(),
        lambda f: "SCHEMA" in f.upper(),
        lambda f: "BACKEND" in f.upper() and "INTEGRATION" in f.upper(),
    ],
    "completion": [
        lambda f: "COMPLETION" in f.upper(),
        lambda f: "COMPLETE" in f.upper() and "FINAL" in f.upper(),
        lambda f: "DELIVERY" in f.upper(),
        lambda f: "CERTIFICATE" in f.upper(),
        lambda f: "PROJECT_FINAL" in f.upper(),
        lambda f: "RELEASE_CHECKLIST" in f.upper(),
    ],
}

def categorize_file(filename):
    """根据文件名分类"""
    for category, rules in CATEGORIES.items():
        for rule in rules:
            if rule(filename):
                return category
    return "misc"

def main():
    os.chdir(REPO_ROOT)
    
    # 收集所有 .md 和 .txt 文件
    md_files = list(REPO_ROOT.glob("*.md"))
    txt_files = list(REPO_ROOT.glob("*.txt"))
    
    moved_count = {}
    for category in CATEGORIES.keys():
        moved_count[category] = 0
    moved_count["misc"] = 0
    
    print("=" * 60)
    print("开始整理文档文件...")
    print("=" * 60)
    
    # 移动 MD 文件
    for file_path in md_files:
        filename = file_path.name
        category = categorize_file(filename)
        target_dir = KANBAN_DIR / category
        
        # 确保目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / filename
        
        # 如果目标文件已存在，跳过
        if target_path.exists():
            print(f"⚠️  跳过 (已存在): {filename}")
            continue
        
        # 移动文件
        try:
            shutil.move(str(file_path), str(target_path))
            print(f"✓ 已移动: {filename:50s} → {category}/")
            moved_count[category] += 1
        except Exception as e:
            print(f"✗ 失败: {filename} ({str(e)})")
    
    # 移动 TXT 文件
    for file_path in txt_files:
        filename = file_path.name
        # 对 TXT 文件进行特殊分类
        if "COMPLETION" in filename.upper() or "CERTIFICATE" in filename.upper():
            category = "completion"
        elif "TASK" in filename.upper():
            category = "tasks"
        elif "README" in filename.upper():
            category = "misc"
        else:
            continue  # 跳过其他 TXT 文件
        
        target_dir = KANBAN_DIR / category
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename
        
        if target_path.exists():
            print(f"⚠️  跳过 (已存在): {filename}")
            continue
        
        try:
            shutil.move(str(file_path), str(target_path))
            print(f"✓ 已移动: {filename:50s} → {category}/")
            moved_count[category] += 1
        except Exception as e:
            print(f"✗ 失败: {filename} ({str(e)})")
    
    print("\n" + "=" * 60)
    print("✅ 整理完成！")
    print("=" * 60)
    print("\n统计：")
    total = 0
    for category in ["tasks", "sessions", "bug_fixes", "deployments", "verification", 
                     "frontend", "backend", "completion", "misc"]:
        count = moved_count.get(category, 0)
        if count > 0:
            print(f"  {category:20s}: {count:3d} 个文件")
            total += count
    
    print(f"\n总计：{total} 个文件已移动到 kanban/archives/")
    print(f"\n📂 新的目录结构：")
    print(f"   kanban/")
    print(f"   ├── archives/")
    print(f"   │   ├── tasks/")
    print(f"   │   ├── sessions/")
    print(f"   │   ├── bug_fixes/")
    print(f"   │   ├── deployments/")
    print(f"   │   ├── verification/")
    print(f"   │   ├── frontend/")
    print(f"   │   ├── backend/")
    print(f"   │   ├── completion/")
    print(f"   │   └── misc/")
    print(f"   ├── agentwork/")
    print(f"   └── issues/")

if __name__ == "__main__":
    main()
