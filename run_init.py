#!/usr/bin/env python3
"""
独立运行初始化脚本，避免后端 watch 干扰
"""
import sys
import os

# 添加后端路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# 现在导入初始化函数
from init_integration_data import init_integration_data

if __name__ == "__main__":
    print("🚀 从独立进程运行初始化脚本...\n")
    init_integration_data()
