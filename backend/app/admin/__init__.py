"""
FastAPI Admin 管理后台模块
基于 SQLAlchemy 的管理界面
"""

__all__ = [
    "setup_admin_routes"
]


def setup_admin_routes(app) -> None:
    """
    设置管理后台路由
    
    Args:
        app: FastAPI 应用实例
    """
    # 导入管理路由
    from app.routes.admin import admin_router
    
    # 注册管理后台路由
    app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
