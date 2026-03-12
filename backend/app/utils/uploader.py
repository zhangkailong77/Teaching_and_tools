import os
import uuid
import shutil
import io
from urllib.parse import urlparse
from fastapi import UploadFile
from app.core.config import settings

try:
    from minio import Minio
except ImportError:
    Minio = None

# 配置本地存储根路径
UPLOAD_DIR = "static/uploads"

async def save_file_locally(file: UploadFile, folder: str = "common") -> str:
    """
    通用文件保存函数
    :param file: 上传的文件对象
    :param folder: 子目录 (例如 'avatars', 'courses')
    :return: 完整的访问 URL
    """
    # 1. 生成唯一文件名 (uuid + 原后缀)
    file_ext = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    
    # 2. 拼接保存路径
    # 物理路径: static/uploads/avatars/xxx.jpg
    save_path = os.path.join(UPLOAD_DIR, folder, unique_filename)
    
    # 3. 写入硬盘
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print(f"文件保存失败: {e}")
        raise e
        
    # 4. 生成访问 URL
    # URL路径: http://127.0.0.1:8000/static/uploads/avatars/xxx.jpg
    # 注意：这里把反斜杠替换为正斜杠，兼容 Windows
    url_path = f"/{UPLOAD_DIR}/{folder}/{unique_filename}".replace("\\", "/")
    
    return url_path

def _normalize_minio_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme and parsed.netloc:
        return parsed.netloc
    return endpoint.replace("http://", "").replace("https://", "")


def _build_public_url(domain: str, object_name: str) -> str:
    base = (domain or "").rstrip("/")
    if not base:
        return object_name
    return f"{base}/{object_name}"


async def save_file_to_minio(file: UploadFile, folder: str = "common") -> str:
    """
    MinIO 文件上传函数
    :param file: 上传的文件对象
    :param folder: 子目录（用于对象名前缀）
    :return: 可访问 URL
    """
    if Minio is None:
        raise RuntimeError("MinIO SDK 未安装，请先安装 minio 包")

    required = {
        "minio_endpoint": settings.minio_endpoint,
        "minio_bucket": settings.minio_bucket,
        "minio_access_key": settings.minio_access_key,
        "minio_access_secret": settings.minio_access_secret,
        "minio_domain": settings.minio_domain,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise RuntimeError(f"MinIO 配置缺失: {', '.join(missing)}")

    file_ext = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    object_name = f"{folder.strip('/')}/{unique_filename}"

    endpoint = _normalize_minio_endpoint(settings.minio_endpoint)
    client = Minio(
        endpoint=endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_access_secret,
        secure=settings.minio_use_ssl,
    )

    data = await file.read()
    file.file.seek(0)
    client.put_object(
        bucket_name=settings.minio_bucket,
        object_name=object_name,
        data=io.BytesIO(data),
        length=len(data),
        content_type=file.content_type or "application/octet-stream",
    )

    return _build_public_url(settings.minio_domain, object_name)
