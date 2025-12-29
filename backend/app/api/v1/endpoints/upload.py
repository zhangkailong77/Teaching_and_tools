from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.uploader import save_file_locally

router = APIRouter()

@router.post("/image")
async def upload_image_endpoint(
    file: UploadFile = File(...),
    type: str = "common" # 允许前端传参数指定类型：avatar / course
):
    # 1. 安全校验：只允许图片
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持上传图片文件")
    
    # 2. 限制大小 (可选，这里假设 Nginx 或 uvicorn 层已做限制，或者读取 file.size)
    
    # 3. 确定子目录
    # 为了安全，只允许特定的子目录，防止路径遍历攻击
    allowed_folders = ["avatars", "courses", "common"]
    folder = type if type in allowed_folders else "common"
    
    # 4. 调用工具类保存 (以后换 OSS 只需要改这里调用的函数)
    try:
        file_url = await save_file_locally(file, folder=folder)
        return {"url": file_url}
    except Exception:
        raise HTTPException(status_code=500, detail="文件上传失败")