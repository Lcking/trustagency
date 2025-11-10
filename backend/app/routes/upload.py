from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api", tags=["upload"])

# 上传目录 - 相对于项目根目录
UPLOAD_DIR = "static/uploads/images"

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    上传图片
    仅允许已认证用户上传
    """
    
    try:
        # 检查文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型。允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # 读取文件内容并检查大小
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"文件过大，最大允许{MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        # 清理原始文件名中的特殊字符
        clean_filename = "".join(c if c.isalnum() or c in '._- ' else '_' for c in file.filename)
        filename = f"{timestamp}_{clean_filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 返回文件URL（相对路径）
        url = f"/static/uploads/images/{filename}"
        
        return {
            "url": url,
            "filename": filename,
            "size": file_size,
            "message": "上传成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件保存失败: {str(e)}"
        )
