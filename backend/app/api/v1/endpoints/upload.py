from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.utils.uploader import save_file_locally, save_file_to_minio

router = APIRouter()


def _is_pdf(file: UploadFile) -> bool:
    content_type = (file.content_type or "").lower()
    filename = (file.filename or "").lower()
    return content_type in ("application/pdf", "application/x-pdf") or filename.endswith(".pdf")


@router.post("/image")
async def upload_image_endpoint(
    file: UploadFile = File(...),
    type: str = "common"  # 允许前端传参数指定类型：avatar / course
):
    # 1. 安全校验：头像/通用只允许图片；homework/materials 支持图片和 PDF
    raw_type = (type or "common").strip().lower()
    is_image = (file.content_type or "").startswith("image/")
    if not is_image:
        if raw_type in ("homework", "materials") and _is_pdf(file):
            pass
        else:
            raise HTTPException(status_code=400, detail="仅支持上传图片文件")

    # 2. 限制大小 (可选，这里假设 Nginx 或 uvicorn 层已做限制，或者读取 file.size)

    # 3. 确定子目录（白名单防路径遍历）
    allowed_folders = ["avatars", "courses", "common", "materials", "homework"]
    folder = raw_type if raw_type in allowed_folders else "common"

    # 4. 保存逻辑：按类型分流到 MinIO（可开关），未开启则走本地
    try:
        if folder == "avatars" and settings.minio_avatar_enabled:
            file_url = await save_file_to_minio(file, folder=settings.minio_avatar_prefix or "avatars")
        elif folder == "common" and settings.minio_common_enabled:
            file_url = await save_file_to_minio(file, folder=settings.minio_common_prefix or "common")
        elif folder == "homework" and settings.minio_homework_enabled:
            file_url = await save_file_to_minio(file, folder=settings.minio_homework_prefix or "homework")
        else:
            file_url = await save_file_locally(file, folder=folder)

        return {"url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
