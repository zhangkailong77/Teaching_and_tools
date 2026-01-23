# ComfyUI工作流排队代理实施计划

> **For Claude:** REQUIRED SUB-SILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 实现ComfyUI工作流执行的排队控制机制，最多10个并发，超过10个请求排队等待

**架构:**
- 学生通过教学系统Nginx代理访问ComfyUI（而非直接访问GPU服务器）
- 每个学生仍有独立的ComfyUI实例和端口（通过SSH启动，保持不变）
- URL格式: `/comfyui/{username}/{port}` - Nginx从URL直接获取端口
- 教学系统后端提供ComfyUI代理API，实现Redis队列管理
- Nginx在ComfyUI页面注入脚本，拦截`/prompt`请求转发到后端
- 后端控制并发数（测试2个，生产10个），超过限制返回排队信息

**技术栈:**
- Nginx (反向代理 + Lua/脚本注入)
- FastAPI (后端代理API)
- Redis (队列管理)
- Python httpx (异步HTTP请求)

---

## 系统架构图

```
原来: 学生 → http://192.168.150.2:8189 (直接访问，无法控制)

改为: 学生 → 教学系统Nginx → GPU服务器ComfyUI
                                    ↓
                            注入脚本拦截 /prompt
                                    ↓
                            转发到后端代理API
                                    ↓
                            Redis队列控制并发
                                    ↓
                            后端调用GPU服务器 /prompt
```

---

## 相关配置

**环境变量 (.env):**
```env
# ComfyUI队列配置
COMFY_MAX_CONCURRENT=2        # 测试环境最大并发
COMFY_MAX_CONCURRENT_PROD=10  # 生产环境最大并发
COMFY_GPU_HOST=192.168.150.2
COMFY_PROXY_BASE_URL=http://192.168.150.2
```

**Nginx配置:**
- 学生访问 `http://教学系统/comfyui/:username`
- Nginx转发到GPU服务器对应端口
- 同时注入脚本拦截`/prompt`请求

---

## Task 1: 扩展Redis模块，添加队列相关方法

**Files:**
- Modify: `backend/app/core/redis.py`

**Step 1: 添加队列相关的Redis操作函数**

```python
# 在 backend/app/core/redis.py 中添加以下函数

def enqueue_to_comfy_queue(username: str, prompt_data: dict, port: int) -> str:
    """将工作流任务加入队列"""
    task_id = f"comfy:task:{username}:{int(time.time()*1000)}"
    task_data = {
        "task_id": task_id,
        "username": username,
        "port": port,
        "prompt_data": prompt_data,
        "status": "queued",
        "created_at": datetime.now().isoformat()
    }
    redis_client.rpush("comfy:queue", json.dumps(task_data))
    redis_client.set(f"comfy:task:{task_id}", json.dumps(task_data), ex=3600)
    return task_id

def get_comfy_queue_position(task_id: str) -> int:
    """获取任务在队列中的位置"""
    # 队列长度 - (当前任务在队列中的索引 + 1)
    pass

def get_comfy_task_status(task_id: str) -> dict:
    """获取任务状态"""
    data = redis_client.get(f"comfy:task:{task_id}")
    if data:
        return json.loads(data)
    return None

def get_comfy_processing_count() -> int:
    """获取当前正在处理的任务数"""
    count = redis_client.get("comfy:processing_count")
    return int(count) if count else 0

def incr_comfy_processing_count() -> int:
    """增加处理中的任务数"""
    return redis_client.incr("comfy:processing_count")

def decr_comfy_processing_count() -> int:
    """减少处理中的任务数"""
    new_count = redis_client.decr("comfy:processing_count")
    return max(0, new_count)

def get_comfy_max_concurrent() -> int:
    """获取最大并发数"""
    import os
    if os.getenv("ENV") == "development":
        return int(os.getenv("COMFY_MAX_CONCURRENT", 2))
    return int(os.getenv("COMFY_MAX_CONCURRENT_PROD", 10))
```

**Step 2: 运行测试确保Redis模块正常**

```bash
cd backend
python -c "from app.core.redis import enqueue_to_comfy_queue; print('OK')"
```

---

## Task 2: 创建ComfyUI代理API

**Files:**
- Create: `backend/app/api/v1/endpoints/comfy_proxy.py`
- Modify: `backend/app/core/config.py` (添加ComfyUI相关配置)

**Step 1: 更新配置文件**

在 `backend/app/core/config.py` 中添加:

```python
# ComfyUI代理配置
COMFY_GPU_HOST: str = "192.168.150.2"
COMFY_MAX_CONCURRENT: int = 2  # 测试环境
COMFY_MAX_CONCURRENT_PROD: int = 10  # 生产环境
```

**Step 2: 创建ComfyUI代理API端点**

创建 `backend/app/api/v1/endpoints/comfy_proxy.py`:

```python
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.core.redis import (
    enqueue_to_comfy_queue,
    get_comfy_queue_position,
    get_comfy_task_status,
    get_comfy_processing_count,
    incr_comfy_processing_count,
    decr_comfy_processing_count,
    get_comfy_max_concurrent
)
import httpx
import asyncio

router = APIRouter()

@router.post("/execute/{username}")
async def execute_workflow(
    username: str,
    prompt_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
):
    """代理执行ComfyUI工作流，实现排队控制"""

    # 权限检查
    if current_user.username != username and current_user.role != "teacher":
        raise HTTPException(403, "无权访问")

    # 获取用户的ComfyUI端口
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.comfyui_port:
        raise HTTPException(404, "用户ComfyUI未启动")

    port = user.comfyui_port
    comfy_url = f"http://{settings.COMFY_GPU_HOST}:{port}/prompt"

    max_concurrent = get_comfy_max_concurrent()
    processing_count = get_comfy_processing_count()

    # 检查是否超过并发限制
    if processing_count >= max_concurrent:
        # 加入队列
        task_id = enqueue_to_comfy_queue(username, prompt_data, port)
        queue_position = get_comfy_queue_position(task_id)

        return {
            "status": "queued",
            "task_id": task_id,
            "position": queue_position,
            "max_concurrent": max_concurrent,
            "processing_count": processing_count,
            "message": f"系统繁忙，前方还有 {queue_position} 人排队"
        }

    # 执行工作流
    try:
        incr_comfy_processing_count()

        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(comfy_url, json=prompt_data)
            response.raise_for_status()
            result = response.json()

            return {
                "status": "completed",
                "result": result
            }
    except Exception as e:
        raise HTTPException(500, f"执行失败: {str(e)}")
    finally:
        decr_comfy_processing_count()
        # 尝试处理队列中的下一个任务
        asyncio.create_task(process_next_task())

@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    """查询任务状态"""
    status = get_comfy_task_status(task_id)
    if not status:
        raise HTTPException(404, "任务不存在")
    return status

async def process_next_task():
    """处理队列中的下一个任务"""
    max_concurrent = get_comfy_max_concurrent()
    processing_count = get_comfy_processing_count()

    if processing_count >= max_concurrent:
        return  # 还是没有空位

    # 从队列取出一个任务
    import json
    from app.core.redis import redis_client

    task_json = redis_client.lpop("comfy:queue")
    if not task_json:
        return  # 队列为空

    task = json.loads(task_json)

    # 执行任务（在后台异步执行）
    # 实际实现需要调用GPU服务器的/prompt接口
    # 这里简化处理，实际需要完整实现
```

**Step 3: 注册路由到主router**

在 `backend/app/api/v1/__init__.py` 或相应位置添加:

```python
from app.api.v1.endpoints import comfy_proxy
api_router.include_router(comfy_proxy.router, tags=["comfy_proxy"])
```

---

## Task 3: 修改ComfyUI启动API，返回代理URL而非直接URL

**Files:**
- Modify: `backend/app/api/v1/endpoints/practice.py`

**Step 1: 修改启动接口返回代理URL**

```python
# 修改 start_practice 函数
@router.post("/start-practice")
def start_practice(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # ... 端口分配逻辑保持不变 ...

    port = current_user.comfyui_port
    username = current_user.username

    # 调用 SSH 启动服务
    success = start_comfyui_remote(username, port)

    if success:
        # 返回教学系统代理URL（不再是直接URL）
        return {
            "status": "success",
            "url": f"/comfyui/{username}",  # 教学系统代理路径
            "direct_url": f"http://192.168.150.2:{port}",  # 调试用
            "message": "实训环境启动成功"
        }
    else:
        raise HTTPException(status_code=500, detail="无法连接到算力服务器")
```

---

## Task 4: 配置Nginx反向代理

**Files:**
- Create: `nginx/comfyui-proxy.conf` (或项目根目录的nginx配置)

**Step 1: 创建Nginx配置文件**

创建 `nginx/comfyui_proxy.conf`:

```nginx
# ComfyUI代理配置
location /comfyui/:username {
    # 根据username获取用户端口（需要后端API支持）
    # 暂时使用固定方式，实际需要动态解析

    # 代理到GPU服务器
    # 这里需要后端API来获取用户端口，暂时简化处理
    # 实际应该先请求后端API获取端口，然后proxy_pass

    # 方案1: 使用nginx变量需要后端API
    # 方案2: 使用固定端口范围映射 (8189 → /comfyui/18250636865)

    # 临时方案：使用iframe嵌入方式，在响应中注入脚本
    # 这里先创建基础配置

    # 返回注入脚本的ComfyUI页面
    proxy_pass http://192.168.150.2:$1;  # $1 从后端API获取
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    # 注入排队脚本
    sub_filter '</head>'
    '<script src="/static/js/comfyui-queue.js"></script></head>';

    sub_filter_once on;
    sub_filter_types text/html;

    # WebSocket支持
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

**注意**: Nginx需要安装 `ngx_http_sub_filter_module`

**Step 2: 更新前端nginx配置或开发环境配置**

如果使用Vite开发服务器，在 `vite.config.ts` 中配置代理:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/comfyui': {
        target: 'http://192.168.150.2',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/comfyui\/[^/]+/, '/'),
        // 需要动态获取端口的逻辑
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyOpts, req, res) => {
            // 调用后端API获取用户端口
            // 这里需要实现动态端口获取
          });
        }
      }
    }
  }
});
```

---

## Task 5: 创建ComfyUI队列脚本注入

**Files:**
- Create: `frontend/src/static/js/comfyui-queue.js`

**Step 1: 创建脚本拦截fetch请求**

创建 `frontend/src/static/js/comfyui-queue.js`:

```javascript
(function() {
    'use strict';

    const MAX_RETRIES = 3;
    const POLL_INTERVAL = 2000;

    // 保存原始fetch
    const originalFetch = window.fetch;

    // 拦截fetch请求
    window.fetch = function(url, options) {
        // 只拦截 /prompt POST 请求
        if (typeof url === 'string' &&
            url.endsWith('/prompt') &&
            options &&
            options.method === 'POST') {

            console.log('[ComfyUI Queue] 拦截到工作流执行请求');

            // 获取当前用户名（从URL路径或cookie）
            const currentUsername = getCurrentUsername();

            // 转发到教学系统代理API
            const proxyUrl = `/api/v1/comfy_proxy/execute/${currentUsername}`;

            return originalFetch(proxyUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: options.body
            })
            .then(response => response.json())
            .then(data => {
                console.log('[ComfyUI Queue] 代理响应:', data);

                if (data.status === 'queued') {
                    // 显示排队提示
                    showQueueNotification(data);

                    // 轮询等待执行
                    return pollAndExecute(proxyUrl, options.body, data.task_id);
                } else if (data.status === 'completed') {
                    // 执行完成，刷新页面获取结果
                    setTimeout(() => location.reload(), 1000);
                }

                return data;
            })
            .catch(error => {
                console.error('[ComfyUI Queue] 请求失败:', error);

                // 失败时尝试原始请求（降级处理）
                return originalFetch(url, options);
            });
        }

        // 其他请求正常处理
        return originalFetch(url, options);
    };

    // 获取当前用户名
    function getCurrentUsername() {
        // 从URL路径获取: /comfyui/18250636865
        const match = window.location.pathname.match(/\/comfyui\/([^\/]+)/);
        if (match) {
            return match[1];
        }

        // 从cookie获取
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'username') return value;
        }

        return null;
    }

    // 轮询并执行
    async function pollAndExecute(proxyUrl, body, taskId) {
        let retries = 0;

        while (retries < MAX_RETRIES) {
            try {
                // 检查任务状态
                const statusResp = await originalFetch(`/api/v1/comfy_proxy/status/${taskId}`);
                const statusData = await statusResp.json();

                if (statusData.status === 'processing') {
                    hideQueueNotification();
                    showProcessingNotification();
                    return;
                }

                if (statusData.status === 'completed') {
                    hideQueueNotification();
                    showCompletedNotification();
                    setTimeout(() => location.reload(), 1000);
                    return;
                }

                if (statusData.status === 'failed') {
                    hideQueueNotification();
                    showErrorNotification(statusData.error);
                    return;
                }

                // 继续轮询
                await sleep(POLL_INTERVAL);
                retries++;

            } catch (error) {
                console.error('[ComfyUI Queue] 轮询失败:', error);
                await sleep(POLL_INTERVAL);
                retries++;
            }
        }
    }

    // 通知显示函数
    function showQueueNotification(data) {
        const existing = document.getElementById('comfyui-queue-notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.id = 'comfyui-queue-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff9800;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 99999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            font-family: system-ui, sans-serif;
        `;
        notification.innerHTML = `
            <div style="font-size: 16px; margin-bottom: 8px;">⏳ 系统繁忙</div>
            <div style="font-size: 14px;">
                前方还有 <strong>${data.position}</strong> 人排队<br>
                最多支持 ${data.max_concurrent} 人同时执行
            </div>
        `;
        document.body.appendChild(notification);
    }

    function showProcessingNotification() {
        // 显示处理中提示
    }

    function showCompletedNotification() {
        // 显示完成提示
    }

    function showErrorNotification(error) {
        // 显示错误提示
    }

    function hideQueueNotification() {
        const notification = document.getElementById('comfy-queue-notification');
        if (notification) notification.remove();
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
})();
```

---

## Task 6: 更新前端ComfyUI入口

**Files:**
- Modify: `frontend/src/views/dashboard/student/practice/index.vue` (或相应入口组件)

**Step 1: 修改启动ComfyUI的跳转逻辑**

找到学生点击"启动ComfyUI"按钮的地方，修改跳转URL:

```javascript
// 原来: window.open(data.url, '_blank')
// 改为: window.open(`/comfyui/${currentUsername}`, '_blank')

// 或使用iframe嵌入
// <iframe :src="`/comfyui/${currentUsername}`"></iframe>
```

**Step 2: 添加队列脚本引入**

确保ComfyUI页面加载队列脚本（通过Nginx注入或在模板中引入）。

---

## Task 7: 添加环境配置

**Files:**
- Modify: `backend/.env`
- Modify: `backend/.env.development`

**Step 1: 更新后端环境变量**

```bash
# ComfyUI队列配置
COMFY_MAX_CONCURRENT=2
COMFY_MAX_CONCURRENT_PROD=10
COMFY_GPU_HOST=192.168.150.2
COMFY_PROXY_BASE_URL=http://192.168.150.2
```

---

## Task 8: 测试排队功能

**Files:**
- Test: 手动测试

**Step 1: 测试单用户执行**

1. 启动教学系统后端
2. 学生A登录，启动ComfyUI
3. 在ComfyUI中点击"运行工作流"
4. 验证：工作流正常执行，直接返回结果

**Step 2: 测试排队功能（需要2个学生账号）**

1. 学生A启动ComfyUI，执行工作流
2. 学生B立即启动ComfyUI，执行工作流
3. 验证：学生B收到排队提示，显示"前方还有1人排队"

**Step 3: 测试队列释放**

1. 等待学生A的工作流执行完成
2. 验证：学生B的请求自动开始执行

**Step 4: 测试错误处理**

1. ComfyUI服务未启动时访问
2. 验证：显示友好错误提示

---

## Task 9: 添加队列监控API（可选）

**Files:**
- Create: `backend/app/api/v1/endpoints/comfy_proxy.py`

**Step 1: 添加队列状态查询API**

```python
@router.get("/queue/status")
def get_queue_status():
    """获取当前队列状态"""
    from app.core.redis import redis_client

    queue_len = redis_client.llen("comfy:queue")
    processing_count = get_comfy_processing_count()
    max_concurrent = get_comfy_max_concurrent()

    return {
        "queue_length": queue_len,
        "processing_count": processing_count,
        "max_concurrent": max_concurrent,
        "available_slots": max_concurrent - processing_count
    }
```

---

## 任务依赖关系

```
Task 1 (扩展Redis) ───────┐
                            │
Task 2 (创建代理API) ◄──────┤
                            │
Task 3 (修改启动API) ───────┤
                            │
Task 4 (Nginx配置) ◄────────┤
                            │
Task 5 (队列脚本) ─────────┤
                            ├──────── Task 6 (更新前端入口)
                            │
                            ├──────── Task 7 (环境配置)
                            │
                            └──────── Task 8 (测试)
                                         │
                                         └──────── Task 9 (监控API)
```

---

## 预计开发时间

| Task | 预计时间 |
|------|---------|
| Task 1: 扩展Redis模块 | 30分钟 |
| Task 2: 创建代理API | 2小时 |
| Task 3: 修改启动API | 30分钟 |
| Task 4: 配置Nginx | 1-2小时 |
| Task 5: 队列脚本 | 1小时 |
| Task 6: 更新前端入口 | 30分钟 |
| Task 7: 环境配置 | 15分钟 |
| Task 8: 测试 | 1小时 |
| Task 9: 监控API | 30分钟 |
| **总计** | **6-7小时** |

---

## 注意事项

1. **Nginx模块要求**: 需要安装 `ngx_http_sub_filter_module` 用于脚本注入
2. **ComfyUI版本兼容性**: 脚本注入需要兼容ComfyUI的HTML结构
3. **跨域问题**: 确保教学系统与GPU服务器之间的网络连通性
4. **测试环境**: 本地测试时可以设置并发数为2，便于验证排队逻辑
5. **日志记录**: 添加详细的日志输出，方便调试

---

## 执行顺序建议

1. 先完成Task 1-3（后端基础功能）
2. 然后完成Task 7（环境配置）
3. 进行简单测试（验证代理功能）
4. 再完成Task 4-6（Nginx和脚本注入）
5. 最后完成Task 8-9（测试和监控）
