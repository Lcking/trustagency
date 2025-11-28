"""
文件上传 API 路由
支持图片上传（Logo、文章图片等）
"""
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.models import AdminUser
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["upload"])

# 配置
UPLOAD_DIR = Path(__file__).parent.parent.parent / "static" / "uploads"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def ensure_upload_dir(subdir: str = "") -> Path:
    """确保上传目录存在"""
    target_dir = UPLOAD_DIR / subdir if subdir else UPLOAD_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def generate_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    ext = Path(original_filename).suffix.lower()
    if not ext:
        ext = ".png"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{timestamp}_{unique_id}{ext}"


def validate_image(file: UploadFile) -> None:
    """验证图片文件"""
    # 检查文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}。支持: JPEG, PNG, GIF, WebP, SVG"
        )
    
    # 检查文件大小（需要先读取）
    file.file.seek(0, 2)  # 移动到文件末尾
    size = file.file.tell()
    file.file.seek(0)  # 重置到开头
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大: {size / 1024 / 1024:.2f}MB。最大允许: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    category: str = Form(default="general"),
    current_user: AdminUser = Depends(get_current_user),
):
    """
    上传图片
    
    Args:
        file: 图片文件
        category: 分类目录 (logos, articles, general)
    
    Returns:
        {
            "success": true,
            "url": "/static/uploads/logos/20231128_abc123.png",
            "filename": "20231128_abc123.png"
        }
    """
    try:
        # 验证图片
        validate_image(file)
        
        # 确保目录存在
        allowed_categories = {"logos", "articles", "general", "platforms"}
        if category not in allowed_categories:
            category = "general"
        
        upload_dir = ensure_upload_dir(category)
        
        # 生成文件名并保存
        filename = generate_filename(file.filename or "image.png")
        file_path = upload_dir / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 返回可访问的 URL
        relative_url = f"/static/uploads/{category}/{filename}"
        
        return {
            "success": True,
            "url": relative_url,
            "filename": filename,
            "category": category,
            "size": file_path.stat().st_size,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/logo")
async def upload_logo(
    file: UploadFile = File(...),
    current_user: AdminUser = Depends(get_current_user),
):
    """
    上传平台 Logo（便捷接口）
    
    自动保存到 logos 目录
    """
    return await upload_image(file=file, category="logos", current_user=current_user)


@router.delete("/image/{category}/{filename}")
async def delete_image(
    category: str,
    filename: str,
    current_user: AdminUser = Depends(get_current_user),
):
    """
    删除已上传的图片
    """
    allowed_categories = {"logos", "articles", "general", "platforms"}
    if category not in allowed_categories:
        raise HTTPException(status_code=400, detail="无效的分类")
    
    file_path = UPLOAD_DIR / category / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 安全检查：确保文件在上传目录内
    try:
        file_path.resolve().relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的文件路径")
    
    try:
        os.remove(file_path)
        return {"success": True, "message": "文件已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/list/{category}")
async def list_images(
    category: str,
    current_user: AdminUser = Depends(get_current_user),
):
    """
    列出指定分类的所有图片
    """
    allowed_categories = {"logos", "articles", "general", "platforms"}
    if category not in allowed_categories:
        raise HTTPException(status_code=400, detail="无效的分类")
    
    target_dir = UPLOAD_DIR / category
    if not target_dir.exists():
        return {"images": []}
    
    images = []
    for file_path in target_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}:
            images.append({
                "filename": file_path.name,
                "url": f"/static/uploads/{category}/{file_path.name}",
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            })
    
    # 按修改时间倒序
    images.sort(key=lambda x: x["modified"], reverse=True)
    
    return {"images": images, "total": len(images)}
