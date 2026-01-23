"""
ComfyUI工作流排队代理API

实现ComfyUI工作流执行的排队控制机制：
- 最多2个并发（测试环境），生产环境10个
- 超过限制的请求自动排队
- 后台自动处理队列中的任务
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
import httpx
import asyncio
import logging

from app.api import deps
from app.models.user import User
from app.core.config import settings
from app.core.redis import (
    enqueue_to_comfy_queue,
    get_comfy_queue_position,
    get_comfy_task_status,
    update_comfy_task_status,
    get_comfy_processing_count,
    incr_comfy_processing_count,
    decr_comfy_processing_count,
    get_comfy_max_concurrent,
    get_comfy_queue_length,
    pop_comfy_queue,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/execute")
async def execute_workflow(
    prompt_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    代理执行ComfyUI工作流，实现排队控制

    - 如果未达到并发限制：直接执行
    - 如果达到并发限制：加入队列返回排队信息

    注意：使用当前登录用户的信息，不需要在URL中传递username
    """

    username = current_user.username

    # 获取用户的ComfyUI端口
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.comfyui_port:
        raise HTTPException(status_code=404, detail="用户ComfyUI未启动，请先启动实训环境")

    port = user.comfyui_port
    comfy_url = f"http://{settings.comfy_gpu_host}:{port}/prompt"

    max_concurrent = get_comfy_max_concurrent()
    processing_count = get_comfy_processing_count()

    logger.info(f"[ComfyUI Queue] 用户 {username} 请求执行工作流，当前并发: {processing_count}/{max_concurrent}")

    # 检查是否超过并发限制
    if processing_count >= max_concurrent:
        # 加入队列
        task_id = enqueue_to_comfy_queue(username, prompt_data, port)
        queue_position = get_comfy_queue_position(task_id)
        queue_length = get_comfy_queue_length()

        logger.info(f"[ComfyUI Queue] 用户 {username} 进入队列，位置: {queue_position}，队列长度: {queue_length}")

        return {
            "status": "queued",
            "task_id": task_id,
            "position": queue_position,
            "queue_length": queue_length,
            "max_concurrent": max_concurrent,
            "processing_count": processing_count,
            "message": f"系统繁忙，前方还有 {queue_position} 人排队"
        }

    # 执行工作流
    return await execute_workflow_direct(comfy_url, prompt_data, username)


async def execute_workflow_direct(
    comfy_url: str,
    prompt_data: Dict[str, Any],
    username: str,
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    直接执行ComfyUI工作流
    """
    try:
        incr_comfy_processing_count()
        logger.info(f"[ComfyUI Queue] 开始执行工作流: {username}, URL: {comfy_url}")

        # 设置超时为10分钟（ComfyUI工作流可能执行较长时间）
        timeout = httpx.Timeout(600.0, connect=30.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(comfy_url, json=prompt_data)
            response.raise_for_status()
            result = response.json()

            logger.info(f"[ComfyUI Queue] 工作流执行完成: {username}")

            # 更新任务状态
            if task_id:
                update_comfy_task_status(task_id, "completed", result)

            return {
                "status": "completed",
                "result": result,
                "prompt_id": result.get("prompt_id"),
                "number": result.get("number"),
            }

    except httpx.TimeoutException:
        logger.error(f"[ComfyUI Queue] 工作流执行超时: {username}")
        if task_id:
            update_comfy_task_status(task_id, "failed", {"error": "执行超时"})
        raise HTTPException(status_code=504, detail="工作流执行超时")
    except httpx.HTTPStatusError as e:
        logger.error(f"[ComfyUI Queue] 工作流执行失败: {username}, 错误: {e}")
        if task_id:
            update_comfy_task_status(task_id, "failed", {"error": str(e)})
        raise HTTPException(status_code=e.response.status_code, detail=f"执行失败: {e}")
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 工作流执行异常: {username}, 错误: {e}")
        if task_id:
            update_comfy_task_status(task_id, "failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")
    finally:
        decr_comfy_processing_count()
        # 尝试处理队列中的下一个任务
        asyncio.create_task(process_next_task())


async def process_next_task():
    """
    处理队列中的下一个任务（后台异步执行）
    """
    max_concurrent = get_comfy_max_concurrent()
    processing_count = get_comfy_processing_count()

    if processing_count >= max_concurrent:
        return  # 还是没有空位

    # 从队列取出一个任务
    task = pop_comfy_queue()
    if not task:
        return  # 队列为空

    task_id = task.get("task_id")
    username = task.get("username")
    port = task.get("port")
    prompt_data = task.get("prompt_data")

    logger.info(f"[ComfyUI Queue] 从队列取出任务: {task_id}, 用户: {username}")

    # 更新任务状态为处理中
    update_comfy_task_status(task_id, "processing")

    # 构造ComfyUI URL
    comfy_url = f"http://{settings.comfy_gpu_host}:{port}/prompt"

    # 执行任务（在后台异步执行）
    try:
        await execute_workflow_direct(comfy_url, prompt_data, username, task_id)
    except Exception as e:
        logger.error(f"[ComfyUI Queue] 队列任务执行失败: {task_id}, 错误: {e}")
        update_comfy_task_status(task_id, "failed", {"error": str(e)})


@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    """
    查询任务状态

    返回任务的状态信息：
    - queued: 排队中
    - processing: 处理中
    - completed: 已完成
    - failed: 失败
    """
    status = get_comfy_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")
    return status


@router.get("/queue/status")
def get_queue_status():
    """
    获取当前队列状态

    返回队列的统计信息
    """
    queue_length = get_comfy_queue_length()
    processing_count = get_comfy_processing_count()
    max_concurrent = get_comfy_max_concurrent()

    return {
        "queue_length": queue_length,
        "processing_count": processing_count,
        "max_concurrent": max_concurrent,
        "available_slots": max_concurrent - processing_count
    }


@router.post("/test/execute")
async def test_execute_workflow(
    mock_delay: int = 5,  # 模拟执行时间（秒）
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    测试用：模拟执行ComfyUI工作流（不实际调用ComfyUI）

    用于验证排队逻辑：
    - 前两次请求会"执行"指定秒数
    - 第三次请求会进入排队
    """
    username = current_user.username

    # 获取用户的ComfyUI端口（仅验证）
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.comfyui_port:
        raise HTTPException(status_code=404, detail="用户ComfyUI未启动，请先启动实训环境")

    max_concurrent = get_comfy_max_concurrent()
    processing_count = get_comfy_processing_count()

    logger.info(f"[ComfyUI Queue TEST] 用户 {username} 请求执行，当前并发: {processing_count}/{max_concurrent}")

    # 检查是否超过并发限制
    if processing_count >= max_concurrent:
        # 加入队列
        task_id = enqueue_to_comfy_queue(username, {"test": True}, user.comfyui_port)
        queue_position = get_comfy_queue_position(task_id)
        queue_length = get_comfy_queue_length()

        logger.info(f"[ComfyUI Queue TEST] 用户 {username} 进入队列，位置: {queue_position}")

        return {
            "status": "queued",
            "task_id": task_id,
            "position": queue_position,
            "queue_length": queue_length,
            "max_concurrent": max_concurrent,
            "processing_count": processing_count,
            "message": f"系统繁忙，前方还有 {queue_position} 人排队"
        }

    # 模拟执行（在后台异步进行）
    incr_comfy_processing_count()

    async def mock_execution():
        try:
            logger.info(f"[ComfyUI Queue TEST] 开始模拟执行，用户: {username}, 延迟: {mock_delay}秒")
            await asyncio.sleep(mock_delay)
            logger.info(f"[ComfyUI Queue TEST] 模拟执行完成，用户: {username}")
        finally:
            decr_comfy_processing_count()
            # 尝试处理队列中的下一个任务
            await process_next_task()

    # 启动后台任务
    asyncio.create_task(mock_execution())

    return {
        "status": "processing",
        "message": f"开始模拟执行，将在 {mock_delay} 秒后完成",
        "mock_delay": mock_delay,
        "processing_count": processing_count + 1,
        "max_concurrent": max_concurrent
    }


@router.post("/test/reset")
def test_reset_queue(current_user: User = Depends(deps.get_current_user)):
    """
    测试用：重置队列状态（清空队列和计数）
    """
    from app.core.redis import redis_client
    redis_client.delete("comfy:queue")
    redis_client.delete("comfy:processing_count")
    return {"message": "队列已重置"}


@router.api_route("/proxy/{username}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def comfy_proxy(
    username: str,
    path: str,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    ComfyUI通用代理：将前端请求转发到GPU服务器

    使用场景：
    - 前端通过 /api/v1/comfy_proxy/proxy/{username}/prompt 访问ComfyUI API
    - 教学系统会转发请求到 http://192.168.150.2:{port}/{path}

    注意：这解决了跨域问题，让队列脚本可以正常工作
    """
    # 权限检查
    if current_user.username != username and current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="无权访问")

    # 获取用户端口
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.comfyui_port:
        raise HTTPException(status_code=404, detail="用户ComfyUI未启动")

    port = user.comfyui_port
    target_url = f"http://{settings.comfy_gpu_host}:{port}/{path}"

    # 转发请求到GPU服务器
    try:
        # 获取请求体
        body = await request.body()

        # 获取请求头（过滤掉一些不需要转发的）
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
    except Exception as e:
        logger.error(f"[ComfyUI Proxy] 转发失败: {e}")
        raise HTTPException(status_code=500, detail=f"代理请求失败: {str(e)}")


@router.get("/view/{username}")
async def get_comfyui_page(
    username: str,
    token: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_optional),
):
    """
    获取ComfyUI页面并注入队列脚本

    用于iframe内嵌ComfyUI，实现自动排队功能
    支持通过token参数认证（用于iframe跨域请求）
    """
    from jose import jwt
    from app.core.security import ALGORITHM
    from fastapi.responses import HTMLResponse

    # 权限检查：优先使用token参数，其次使用登录用户
    user = None

    if token:
        # 通过token获取用户
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.warning(f"[ComfyUI Proxy] Token验证失败: {e}")

    if not user and current_user:
        user = current_user

    if not user or user.username != username:
        raise HTTPException(status_code=403, detail="无权访问")

    # 获取用户端口
    if not user.comfyui_port:
        raise HTTPException(status_code=404, detail="用户ComfyUI未启动")

    port = user.comfyui_port
    comfy_url = f"http://{settings.comfy_gpu_host}:{port}/"

    # 获取ComfyUI首页HTML
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(comfy_url)
            response.raise_for_status()
            html_content = response.text

        # 重写ComfyUI HTML中的绝对路径为相对路径
        # 这样可以配合base标签让所有请求都通过后端代理

        import re

        # 重写CSS链接：href="/xxx.css" -> href="xxx.css"
        html_content = re.sub(r'href="(/[^"]+\.css)"', r'href="\1"', html_content)

        # 重写JS链接：src="/xxx.js" -> src="xxx.js"
        html_content = re.sub(r'src="(/[^"]+\.js)"', r'src="\1"', html_content)

        # 重写其他可能的绝对路径引用
        html_content = re.sub(r'"(/api/)', r'"\1', html_content)
        html_content = re.sub(r'"(/extensions/)', r'"\1', html_content)
        html_content = re.sub(r'"(/embed/)', r'"\1', html_content)
        html_content = re.sub(r'"(/user)', r'"\1', html_content)

        logger.info(f"[ComfyUI Proxy] HTML绝对路径已重写为相对路径")
        logger.info(f"[ComfyUI Proxy] HTML绝对路径已重写为相对路径")

        # 注入fetch和XHR拦截脚本，为所有API请求添加token
        # 使用字符串拼接避免 f-string 的 {{}} 转义问题
        fetch_interceptor = '''
<script>
(function() {
    window.COMFY_AUTH_TOKEN = "''' + (token or '').replace('"', '\\"') + '''";
    window.COMFY_USERNAME = "''' + username.replace('"', '\\"') + '''";

    (function() {
        var originalFetch = window.fetch;
        window.fetch = function(url, options) {
            if (typeof url === "string" && (url.indexOf("/api/") === 0 || url.indexOf("/view/api/") === 0 || url.indexOf("/comfy_proxy/view/api/") !== -1)) {
                var authToken = window.COMFY_AUTH_TOKEN || localStorage.getItem("token");
                if (authToken && (!options || !options.headers || !options.headers.Authorization)) {
                    options = options || {};
                    options.headers = options.headers || {};
                    options.headers.Authorization = "Bearer " + authToken;
                }
            }
            return originalFetch(url, options);
        };
    })();

    (function() {
        var originalOpen = XMLHttpRequest.prototype.open;
        var originalSend = XMLHttpRequest.prototype.send;

        XMLHttpRequest.prototype.open = function(method, url) {
            this._comfyUrl = url;
            return originalOpen.apply(this, arguments);
        };

        XMLHttpRequest.prototype.send = function(body) {
            var url = this._comfyUrl;
            if (typeof url === "string" && (url.indexOf("/api/") === 0 || url.indexOf("/view/api/") === 0 || url.indexOf("/comfy_proxy/view/api/") !== -1)) {
                var authToken = window.COMFY_AUTH_TOKEN || localStorage.getItem("token");
                if (authToken && !this.getRequestHeader("Authorization")) {
                    this.setRequestHeader("Authorization", "Bearer " + authToken);
                }
            }
            return originalSend.apply(this, arguments);
        };
    })();
})();
</script>
'''
        html_content = html_content.replace("</head>", fetch_interceptor + "</head>")

        # 添加base标签，让ComfyUI的相对资源通过后端代理加载
        base_tag = f'<base href="/api/v1/comfy_proxy/view/{username}/">'

        # 在<head>后添加base标签
        html_content = html_content.replace("<head>", "<head>" + base_tag)

        logger.info(f"[ComfyUI Proxy] 返回ComfyUI HTML（base标签指向后端代理）")

        # 返回HTML
        return HTMLResponse(content=html_content)

    except httpx.HTTPStatusError as e:
        logger.error(f"[ComfyUI Proxy] 获取ComfyUI页面失败: {e}")
        raise HTTPException(status_code=e.response.status_code, detail="无法获取ComfyUI页面")
    except Exception as e:
        html_content = html_content.replace("</head>", fetch_interceptor + "</head>")

        # 添加base标签，让ComfyUI的相对资源通过后端代理加载
        base_tag = f'<base href="/api/v1/comfy_proxy/view/{username}/">'

        # 在<head>后添加base标签
        html_content = html_content.replace("<head>", "<head>" + base_tag)

        logger.info(f"[ComfyUI Proxy] 返回ComfyUI HTML（base标签指向后端代理）")

        # 返回HTML
        return HTMLResponse(content=html_content)

    except httpx.HTTPStatusError as e:
        logger.error(f"[ComfyUI Proxy] 获取ComfyUI页面失败: {e}")
        raise HTTPException(status_code=e.response.status_code, detail="无法获取ComfyUI页面")
    except Exception as e:
        logger.error(f"[ComfyUI Proxy] 获取ComfyUI页面异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取ComfyUI页面失败: {str(e)}")


@router.api_route("/view/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_comfyui_api_fallback(
    path: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    处理ComfyUI的API请求（没有username的情况）

    当ComfyUI的JS代码发起绝对路径请求时（如 /api/i18n），
    会匹配这个路由。通过token或session获取username，然后转发到正确的路径。

    注意：这个路由会匹配 /api/v1/comfy_proxy/view/api/* 路径
    """
    from jose import jwt
    from app.core.security import ALGORITHM

    # 尝试从多个来源获取token和用户信息
    username = None
    port = None

    # 1. 首先从 Authorization header 获取
    auth_header = request.headers.get("Authorization", "")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    username = user.username
                    port = user.comfyui_port
                    logger.debug(f"[ComfyUI Proxy] API Fallback: 通过Authorization header获取用户: {username}")
        except Exception as e:
            logger.debug(f"[ComfyUI Proxy] Token解码失败: {e}")

    # 2. 如果没有找到，尝试从请求查询参数或cookie获取token
    if not username:
        # 尝试从 cookie 获取 token
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            # cookie 格式可能是 "Bearer xxx" 或直接是 token
            if cookie_token.startswith("Bearer "):
                cookie_token = cookie_token[7:]
            try:
                payload = jwt.decode(cookie_token, settings.secret_key, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                if user_id:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        username = user.username
                        port = user.comfyui_port
                        logger.debug(f"[ComfyUI Proxy] API Fallback: 通过cookie获取用户: {username}")
            except Exception as e:
                logger.debug(f"[ComfyUI Proxy] Cookie token解码失败: {e}")

    # 3. 如果还是没有，尝试从 URL 中的 token 参数获取
    if not username:
        query_params = request.query_params
        url_token = query_params.get("token") or query_params.get("comfy_token")
        if url_token:
            try:
                payload = jwt.decode(url_token, settings.secret_key, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                if user_id:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        username = user.username
                        port = user.comfyui_port
                        logger.debug(f"[ComfyUI Proxy] API Fallback: 通过URL token获取用户: {username}")
            except Exception as e:
                logger.debug(f"[ComfyUI Proxy] URL token解码失败: {e}")

    # 如果没有找到username，返回401
    if not username:
        logger.warning(f"[ComfyUI Proxy] API Fallback: 无法获取用户信息")
        raise HTTPException(status_code=401, detail="需要认证")

    # 获取用户端口（如果前面没获取到）
    if not port:
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.comfyui_port:
            raise HTTPException(status_code=404, detail="用户ComfyUI未启动")
        port = user.comfyui_port

    target_url = f"http://{settings.comfy_gpu_host}:{port}/api/{path}"

    logger.info(f"[ComfyUI Proxy] API Fallback: /api/{path} -> {target_url} (用户: {username})")

    # 转发请求到GPU服务器
    try:
        body = await request.body()
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        timeout = httpx.Timeout(60.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )

        response_headers = dict(response.headers)
        response_headers.pop("content-encoding", None)
        response_headers.pop("transfer-encoding", None)

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
        )
    except Exception as e:
        logger.error(f"[ComfyUI Proxy] API Fallback失败: {e}")
        raise HTTPException(status_code=500, detail=f"代理请求失败: {str(e)}")


@router.api_route("/view/{username}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_comfyui_resource(
    username: str,
    path: str,
    request: Request,
    token: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user_optional),
):
    """
    代理ComfyUI静态资源和API请求

    用于处理iframe内嵌ComfyUI时的资源加载：
    - CSS文件: /view/{username}/assets/*.css
    - JS文件: /view/{username}/assets/*.js
    - API请求: /view/{username}/api/*
    - 其他静态资源

    支持通过token参数认证（用于iframe跨域请求）

    注意：ComfyUI有自己的 /api/* 路径，当请求 /view/xxx/api/yyy 时
    实际上应该把username当作真实用户，path是 "api/yyy"
    """
    from jose import jwt
    from app.core.security import ALGORITHM

    # 检查是否是ComfyUI的API路径
    # 如果username是 'api'，说明请求的是 /view/api/*，应该由 /view/api/{path} 路由处理
    # 由于路由顺序问题，这里需要兼容处理
    if username == 'api':
        logger.warning(f"[ComfyUI Proxy] /view/api/* 请求被路由到这里: {path}")
        # 转发到正确的API fallback路由
        port = None
        comfy_username = None

        # 尝试从多个来源获取token和用户信息
        # 1. 首先从 Authorization header 获取
        auth_header = request.headers.get("Authorization", "")
        if auth_header and auth_header.startswith("Bearer "):
            token_val = auth_header[7:]
            try:
                payload = jwt.decode(token_val, settings.secret_key, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                if user_id:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        port = user.comfyui_port
                        comfy_username = user.username
                        logger.debug(f"[ComfyUI Proxy] 通过Authorization header获取用户: {comfy_username}")
            except Exception as e:
                logger.debug(f"[ComfyUI Proxy] Token解码失败: {e}")

        # 2. 如果没有找到，尝试从 cookie 获取 token
        if not port:
            cookie_token = request.cookies.get("access_token")
            if cookie_token:
                if cookie_token.startswith("Bearer "):
                    cookie_token = cookie_token[7:]
                try:
                    payload = jwt.decode(cookie_token, settings.secret_key, algorithms=[ALGORITHM])
                    user_id = payload.get("sub")
                    if user_id:
                        user = db.query(User).filter(User.id == user_id).first()
                        if user:
                            port = user.comfyui_port
                            comfy_username = user.username
                            logger.debug(f"[ComfyUI Proxy] 通过cookie获取用户: {comfy_username}")
                except Exception as e:
                    logger.debug(f"[ComfyUI Proxy] Cookie token解码失败: {e}")

        # 3. 如果还是没有，尝试从 URL 中的 token 参数获取
        if not port:
            query_params = request.query_params
            url_token = query_params.get("token") or query_params.get("comfy_token")
            if url_token:
                try:
                    payload = jwt.decode(url_token, settings.secret_key, algorithms=[ALGORITHM])
                    user_id = payload.get("sub")
                    if user_id:
                        user = db.query(User).filter(User.id == user_id).first()
                        if user:
                            port = user.comfyui_port
                            comfy_username = user.username
                            logger.debug(f"[ComfyUI Proxy] 通过URL token获取用户: {comfy_username}")
                except Exception as e:
                    logger.debug(f"[ComfyUI Proxy] URL token解码失败: {e}")

        if not port:
            raise HTTPException(status_code=401, detail="需要认证")

        target_url = f"http://{settings.comfy_gpu_host}:{port}/api/{path}"
        logger.info(f"[ComfyUI Proxy] API fallback代理: {path} -> {target_url} (用户: {comfy_username})")

        try:
            body = await request.body()
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)

            timeout = httpx.Timeout(60.0, connect=10.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                )

            response_headers = dict(response.headers)
            response_headers.pop("content-encoding", None)
            response_headers.pop("transfer-encoding", None)

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
            )
        except Exception as e:
            logger.error(f"[ComfyUI Proxy] API fallback失败: {e}")
            raise HTTPException(status_code=500, detail=f"代理请求失败: {str(e)}")

    # 检查是否是其他ComfyUI内部路径
    if username in ('extensions', 'embed', 'user', 'upload', 'socket.io', 'prompt'):
        logger.warning(f"[ComfyUI Proxy] 收到ComfyUI内部路径作为username: {username}/{path}")
        raise HTTPException(status_code=404, detail="无效的路径")

    # 权限检查：优先使用token参数，其次使用登录用户，最后直接查询username
    user = None

    if token:
        # 通过token获取用户
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.debug(f"[ComfyUI Proxy] Token验证失败: {e}")

    if not user and current_user:
        user = current_user

    # 对于资源请求，如果还是没有用户，直接根据username查询
    # 因为iframe内的资源请求不会自动携带认证信息
    if not user:
        user = db.query(User).filter(User.username == username).first()
        if user:
            logger.debug(f"[ComfyUI Proxy] 资源请求通过username获取用户: {username}")

    if not user or user.username != username:
        logger.warning(f"[ComfyUI Proxy] 权限拒绝: request_user={user.username if user else None}, target_user={username}")
        raise HTTPException(status_code=403, detail="无权访问")

    # 获取用户端口
    if not user.comfyui_port:
        raise HTTPException(status_code=404, detail="用户ComfyUI未启动")

    port = user.comfyui_port
    target_url = f"http://{settings.comfy_gpu_host}:{port}/{path}"

    logger.info(f"[ComfyUI Proxy] 资源代理: {path} -> {target_url}")

    # 转发请求到GPU服务器
    try:
        # 获取请求体
        body = await request.body()

        # 获取请求头（过滤掉一些不需要转发的）
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        # 对于资源请求，设置适当的超时时间
        timeout = httpx.Timeout(60.0, connect=10.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )

            # 构造响应头
            response_headers = dict(response.headers)
            # 移除一些不需要转发的响应头
            response_headers.pop("content-encoding", None)
            response_headers.pop("transfer-encoding", None)

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"[ComfyUI Proxy] 资源代理失败: {path}, 错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"资源加载失败")
    except Exception as e:
        logger.error(f"[ComfyUI Proxy] 资源代理异常: {path}, 错误: {e}")
        raise HTTPException(status_code=500, detail=f"资源代理失败: {str(e)}")

