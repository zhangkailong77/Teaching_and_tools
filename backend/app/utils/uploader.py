import os
import uuid
import shutil
from fastapi import UploadFile

# 配置本地存储根路径
UPLOAD_DIR = "static/uploads"
# 配置访问域名前缀 (本地开发用 localhost，上线改服务器IP)
BASE_URL = "http://127.0.0.1:8000"

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
    url_path = f"{BASE_URL}/{UPLOAD_DIR}/{folder}/{unique_filename}".replace("\\", "/")
    
    return url_path

# --- 预留接口：未来切换 OSS 时，只需解开注释并实现这个函数 ---
# async def save_file_to_oss(file: UploadFile, folder: str) -> str:
#     # 调用阿里云 SDK 上传
#     # return "https://oss.aliyun.com/..."
#     pass