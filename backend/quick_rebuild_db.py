#!/usr/bin/env python3
"""
快速数据库重新生成脚本
直接在Python3中运行，无需终端
"""
import os
import sys

# 切换到后端目录
os.chdir('/Users/ck/Desktop/Project/trustagency/backend')

# 删除旧数据库
if os.path.exists('trustagency.db'):
    os.remove('trustagency.db')
    print("✅ 旧数据库已删除")

# 运行restore_db脚本
print("\n开始生成新数据库...\n")
os.system('python3 restore_db.py trustagency.db')

print("\n✅ 完成！现在可以重新启动后端服务了")
print("执行: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
