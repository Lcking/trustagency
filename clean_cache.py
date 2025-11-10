#!/usr/bin/env python3
"""
清理 Python 缓存并重新启动后端
"""
import os
import subprocess
import shutil
import sys

def clean_pycache():
    """清理所有 __pycache__ 目录"""
    backend_path = "/Users/ck/Desktop/Project/trustagency/backend"
    count = 0
    
    for root, dirs, files in os.walk(backend_path):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            print(f"删除: {cache_dir}")
            shutil.rmtree(cache_dir)
            count += 1
    
    print(f"✅ 已清理 {count} 个缓存目录")

def clean_pyc():
    """清理所有 .pyc 文件"""
    backend_path = "/Users/ck/Desktop/Project/trustagency/backend"
    count = 0
    
    for root, dirs, files in os.walk(backend_path):
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                print(f"删除: {file_path}")
                os.remove(file_path)
                count += 1
    
    print(f"✅ 已清理 {count} 个 .pyc 文件")

def main():
    print("🧹 清理 Python 缓存...")
    clean_pycache()
    clean_pyc()
    print("\n✅ 缓存清理完毕！")
    print("现在可以启动后端了")

if __name__ == "__main__":
    main()
