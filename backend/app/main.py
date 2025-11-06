"""
FastAPI 应用主文件
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建 FastAPI 应用
app = FastAPI(
    title=os.getenv("API_TITLE", "TrustAgency API"),
    description=os.getenv("API_DESCRIPTION", "Admin CMS with AI Content Generation"),
    version=os.getenv("API_VERSION", "1.0.0"),
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS 配置
cors_origins = os.getenv("CORS_ORIGINS", '["http://localhost:8000", "http://localhost:8001"]')
if isinstance(cors_origins, str):
    import json
    cors_origins = json.loads(cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查端点
@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "message": "TrustAgency Backend is running"
    }

# 根路由
@app.get("/")
async def root():
    """根路由"""
    return {
        "name": "TrustAgency API",
        "version": os.getenv("API_VERSION", "1.0.0"),
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=os.getenv("DEBUG", "True") == "True"
    )
