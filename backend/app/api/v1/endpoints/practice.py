from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.models.user import User
from app.utils.comfy_runner import start_comfyui_remote, stop_comfyui_remote

router = APIRouter()

@router.post("/start-practice")
def start_practice(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    启动ComfyUI实训环境

    返回信息包含：
    - url: 教学系统代理URL（用于排队控制）
    - direct_url: GPU服务器直接URL（备用/调试）
    - port: 分配的端口号
    """
    # 1. 检查用户是否有分配端口
    if not current_user.comfyui_port:
        # 查找当前最大的端口号，如果没人用过，就从 8189 开始
        max_port = db.query(func.max(User.comfyui_port)).scalar()
        if max_port is None:
            new_port = 8189
        else:
            new_port = max_port + 1

        current_user.comfyui_port = new_port
        db.add(current_user)
        db.commit()

    port = current_user.comfyui_port
    username = current_user.username

    # 2. 调用 SSH 启动服务
    success = start_comfyui_remote(username, port)

    if success:
        # 返回访问地址
        # url: 开发环境使用Vite代理（需要前端配置）
        # direct_url: GPU服务器直接访问（备用）
        return {
            "status": "success",
            "url": f"/comfyui-direct/{port}/",  # Vite代理路径
            "direct_url": f"http://192.168.150.2:{port}",  # 直接访问（备用）
            "port": port,
            "message": "实训环境启动成功"
        }
    else:
        raise HTTPException(status_code=500, detail="无法连接到算力服务器")


@router.post("/stop-practice")
def stop_practice(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not current_user.comfyui_port:
        return {"message": "用户未分配端口，无需关闭"}
    
    # 调用 SSH 关闭
    stop_comfyui_remote(current_user.username, current_user.comfyui_port)
    
    return {"message": "实训环境已关闭"}