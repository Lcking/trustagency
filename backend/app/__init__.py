# 应用初始化
# 当应用模块被导入时，自动初始化数据库
try:
    from app.database import init_db
    init_db()
except Exception as e:
    print(f"⚠️ 应用初始化警告: {e}")
