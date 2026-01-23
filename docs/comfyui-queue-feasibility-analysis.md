# ComfyUI工作流排队机制 - 可行性分析

> **文档日期**: 2026-01-21
> **方案名称**: 轻量级代理方案
> **目标**: 实现ComfyUI工作流执行的并发控制与排队机制

---

## 一、方案概述

### 系统架构

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  学生浏览器   │ ───► │  教学系统后端  │ ───► │  Redis队列  │
│ (ComfyUI界面) │      │  (代理API)    │      │            │
└─────────────┘      └──────────────┘      └─────────────┘
       │                                         │
       │ 注入脚本拦截fetch                    │
       ▼                                         ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  教学系统API  │ ◄─── │   后端Worker  │ ◄─── │  队列处理器  │
│  轮询结果    │      │  (执行工作流)  │      │  (Semaphore) │
└─────────────┘      └──────────────┘      └─────────────┘
                                                      │
                                                      ▼
                                              ┌───────────────┐
                                              │  ComfyUI API   │
                                              │  (实际执行)    │
                                              └───────────────┘
```

### 核心思路

1. **脚本注入**：在ComfyUI页面注入JavaScript，拦截`fetch`请求
2. **请求转发**：将执行工作流的请求转发到教学系统后端
3. **队列管理**：使用Redis队列管理任务，最大10个并发
4. **异步执行**：后端Worker调用ComfyUI API执行工作流
5. **状态轮询**：前端轮询获取执行状态和结果

---

## 二、技术可行性评估

| 技术点 | 可行性 | 说明 |
|-------|--------|------|
| Redis队列 | ✅ 高 | 系统已有Redis基础设施，直接复用 |
| 脚本注入 | ✅ 高 | 标准HTML处理技术，无特殊依赖 |
| Fetch拦截 | ✅ 高 | JavaScript原生支持，无需额外库 |
| ComfyUI API调用 | ✅ 高 | ComfyUI有标准的REST API |
| 后台任务 | ⚠️ 中 | 需要实现worker机制（Celery或简单线程）|

---

## 三、潜在风险与问题

### 风险1：ComfyUI升级后注入失效

**问题**：ComfyUI更新后HTML结构变化，注入脚本可能失效

**概率**：⭐⭐ 中等（ComfyUI更新较频繁）

**缓解方案**：
- 使用稳定的ComfyUI版本（固定版本号）
- 定期测试注入脚本是否有效
- 或者：使用浏览器扩展方式（学生安装插件）

---

### 风险2：WebSocket连接问题

**问题**：ComfyUI使用WebSocket实时显示执行进度，代理后可能断连

**概率**：⭐⭐⭐ 较高

**缓解方案**：
- 只拦截`/prompt`请求，不拦截WebSocket
- WebSocket直接连接原ComfyUI服务
- 或者完全禁用实时进度，用轮询替代

---

### 风险3：工作流执行超时处理

**问题**：工作流执行卡死，槽位永久占用

**概率**：⭐⭐ 中等

**缓解方案**：
```python
# 设置任务超时（如10分钟）
@timeout(600)  # 10分钟超时
def execute_workflow_task(task_id, task_data):
    try:
        # 执行逻辑
    except TimeoutError:
        # 清理槽位
        redis_client.decr(PROCESSING_KEY)
        # 标记任务失败
```

---

### 风险4：资源清理

**问题**：学生关闭浏览器，任务状态无法更新

**概率**：⭐ 低（后端自主执行，不依赖前端）

**说明**：后端自主执行，不依赖前端保持连接

---

## 四、未确认的问题

### 问题1：ComfyUI中如何调用"执行"？

**现状**：学生点击ComfyUI界面中的运行按钮

**需要确认**：
- ComfyUI是每个学生独立实例吗？
- 各实例的`/prompt`接口是独立的吗？
- 并发限制是全局的还是每个实例的？

**可能的方案**：
- **全局限制**：10个并发指整个系统最多10个工作流同时执行
- **单实例限制**：每个ComfyUI实例内部限制（需要修改ComfyUI源码）

---

### 问题2：如何拦截"运行"按钮？

**需要确认**：
- ComfyUI的"运行"按钮调用的是 `/prompt` API吗？
- 是否还有其他API需要拦截（如`/queue`）？

**验证方法**：
```bash
# 在ComfyUI界面打开开发者工具
# 点击"运行"，观察Network面板
# 查看调用了什么API，发送了什么数据
```

---

## 五、实现难度评估

| 模块 | 难度 | 预估时间 | 风险 |
|-----|------|---------|------|
| 脚本注入 | ⭐⭐ | 4小时 | ComfyUI升级可能失效 |
| 队列API | ⭐⭐ | 4小时 | 低 |
| Worker执行器 | ⭐⭐⭐ | 6小时 | 超时处理复杂 |
| 前端轮询 | ⭐⭐ | 3小时 | 低 |
| 测试调试 | ⭐⭐⭐ | 4小时 | ComfyUI环境需远程 |
| **总计** | - | **约21小时** | - |

---

## 六、新增文件清单

| 文件 | 操作 | 说明 |
|-----|------|------|
| `backend/app/api/v1/endpoints/comfy.py` | 新建 | 代理API、队列管理 |
| `backend/app/api/v1/endpoints/comfy_queue.py` | 新建 | 队列处理器（可选分离）|
| `backend/app/core/queue.py` | 新建 | 队列工具类 |
| `backend/app/utils/comfy_worker.py` | 新建 | Worker执行器 |
| `backend/app/core/redis.py` | 修改 | 添加队列相关方法 |

---

## 七、核心代码示例

### 7.1 脚本注入

```python
@router.get("/proxy/{username}")
def get_comfyui_proxy(username: str, current_user: User = Depends(deps.get_current_user)):
    """返回注入了排队脚本的ComfyUI页面"""

    # 获取用户的ComfyUI端口
    port = get_user_comfyui_port(username)
    comfy_url = f"http://{GPU_HOST}:{port}"

    # 获取ComfyUI原始HTML
    response = requests.get(f"{comfy_url}/index.html")
    html = response.text

    # 注入排队脚本
    inject_script = f"""
    <script>
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {{
        if (url.endsWith('/prompt')) {{
            const proxyUrl = '/api/v1/comfy/queue/execute';
            return originalFetch(proxyUrl, {{
                method: 'POST',
                headers: options.headers,
                body: options.body,
                credentials: 'include'
            }});
        }}
        return originalFetch(url, options);
    }};
    </script>
    """

    html = html.replace('</head>', inject_script + '</head>')
    return HTMLResponse(content=html)
```

### 7.2 队列执行API

```python
QUEUE_KEY = "comfy:queue"
PROCESSING_KEY = "comfy:processing"
MAX_CONCURRENT = 10  # 生产环境
MAX_CONCURRENT_TEST = 2  # 测试环境

@router.post("/queue/execute")
def enqueue_workflow(workflow: dict, current_user: User = Depends(deps.get_current_user)):
    """将工作流加入执行队列"""

    # 检查并发限制
    processing_count = int(redis_client.get(PROCESSING_KEY) or 0)
    max_concurrent = MAX_CONCURRENT_TEST if os.getenv("ENV") == "development" else MAX_CONCURRENT

    task_id = f"task_{current_user.id}_{int(time.time() * 1000)}"

    if processing_count < max_concurrent:
        # 直接执行
        redis_client.incr(PROCESSING_KEY)
        execute_workflow_task(task_id, workflow)
        return {"task_id": task_id, "status": "processing", "position": 0}
    else:
        # 加入排队
        task_data = {"task_id": task_id, "user_id": current_user.id, "workflow": workflow, "status": "queued"}
        redis_client.rpush(QUEUE_KEY, json.dumps(task_data))
        queue_len = redis_client.llen(QUEUE_KEY)
        return {"task_id": task_id, "status": "queued", "position": queue_len}
```

---

## 八、测试配置

### 环境变量

```env
# ComfyUI队列配置
COMFY_MAX_CONCURRENT=10        # 生产环境最大并发
COMFY_MAX_CONCURRENT_TEST=2    # 测试环境最大并发
COMFY_QUEUE_POLL_INTERVAL=2    # 轮询间隔(秒)
```

---

## 九、可行性结论

| 方面 | 结论 |
|-----|------|
| **技术可行性** | ✅ 可行，但需要先验证ComfyUI API |
| **实施复杂度** | ⭐⭐⭐ 中等复杂度 |
| **维护成本** | ⭐⭐⭐ 中等（脚本注入需要维护）|
| **整体推荐度** | ⭐⭐⭐⭐ 推荐（在验证API后）|

---

## 十、下一步行动

### 必须完成的验证（技术确认）

**步骤1：验证ComfyUI API**

1. 打开ComfyUI界面
2. 打开浏览器开发者工具（F12）
3. 切换到 Network 标签
4. 点击"运行"按钮
5. 查看请求记录：
   - API路径是什么？（如`/prompt`、`/queue`等）
   - 请求方法？（POST/GET）
   - 请求体格式？
   - 响应格式？

### 需要确认的信息

1. **ComfyUI版本**：你使用的是哪个版本的ComfyUI？
2. **API路径**：执行工作流调用的是哪个API？
3. **并发范围**：10个并发是全局限制，还是每个实例限制？
4. **部署方式**：ComfyUI是Docker部署还是直接运行？
5. **测试环境**：能否提供一个ComfyUI测试环境验证？

---

## 附录：替代方案对比

| 方案 | 难度 | 维护成本 | 用户体验 | 推荐度 |
|-----|------|---------|---------|-------|
| A. 修改ComfyUI源码 | ⭐⭐⭐⭐ | 高 | ⭐⭐⭐⭐⭐ | ❌ |
| B. Nginx限流 | ⭐⭐ | 低 | ⭐⭐ | ❌ |
| C. 自建前端后端 | ⭐⭐⭐⭐⭐ | 中 | ⭐⭐⭐ | ❌ |
| **D. 轻量级代理** | ⭐⭐⭐ | 中 | ⭐⭐⭐⭐ | ✅ |
