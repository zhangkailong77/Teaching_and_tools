/**
 * ComfyUI工作流排队代理脚本
 *
 * 功能：
 * 1. 拦截ComfyUI的 /prompt POST请求
 * 2. 转发到教学系统后端排队API
 * 3. 显示排队状态通知
 * 4. 轮询等待执行结果
 * 5. 重写所有API请求路径到代理
 *
 * 使用方式：
 * 1. 通过Nginx sub_filter注入到ComfyUI页面
 * 2. 或在代理页面中手动加载
 */

(function() {
    'use strict';

    // ==================== 配置 ====================
    const CONFIG = {
        API_BASE_URL: window.COMFY_PROXY_BASE_URL || '/api/v1',
        POLL_INTERVAL: 2000,  // 轮询间隔（毫秒）
        MAX_POLL_RETRIES: 300,  // 最大轮询次数（10分钟）
        NOTIFICATION_DURATION: 5000,  // 通知显示时长
        PROXY_USERNAME: window.COMFY_PROXY_USERNAME || null,
    };

    // ==================== 状态 ====================
    let currentTaskId = null;
    let pollTimer = null;
    let pollCount = 0;
    let isPageRefreshing = false; // 标记：页面是否刚刚刷新（禁用拦截）

    // ==================== 从URL获取用户名 ====================
    function getUsernameFromUrl() {
        // URL格式: /comfyui/{username}/{port}/
        const match = window.location.pathname.match(/^\/comfyui\/([^\/]+)\/\d+\/?/);
        return match ? match[1] : null;
    }

    // ==================== URL重写函数 ====================
    function rewriteUrl(url) {
        if (typeof url !== 'string') return url;

        // 如果已经是代理路径，不再重写
        if (url.includes('/comfy_proxy/view/')) {
            return url;
        }

        // 如果是相对路径（不以/开头），不需要重写
        if (!url.startsWith('/')) {
            return url;
        }

        // 绝对路径重写：/api/xxx -> /api/v1/comfy_proxy/view/{username}/api/xxx
        // 优先级：CONFIG.PROXY_USERNAME > window.COMFY_USERNAME > URL路径
        let username = CONFIG.PROXY_USERNAME || window.COMFY_USERNAME;
        if (!username) {
            username = getUsernameFromUrl();
        }
        if (!username) {
            console.warn('[ComfyUI Queue] 未找到用户名，无法重写URL');
            return url;
        }

        const proxyPath = `${CONFIG.API_BASE_URL}/comfy_proxy/view/${username}`;

        // ComfyUI的API路径
        if (url.startsWith('/api/') || url.startsWith('/extensions/') ||
            url.startsWith('/embed/') || url.startsWith('/user')) {
            return proxyPath + url;
        }

        // 其他绝对路径保持不变（可能是assets等已经正确配置的路径）
        return url;
    }

    // ==================== 拦截fetch请求 ====================
    const originalFetch = window.fetch;

    window.fetch = function(url, options) {
        // 只拦截 POST /prompt 请求（工作流执行）
        const isPromptRequest =
            typeof url === 'string' &&
            (url.endsWith('/prompt') || url === '/prompt') &&
            options &&
            options.method === 'POST';

        // 如果是 POST /prompt 请求（用户主动点击），重置刷新标记
        if (isPromptRequest) {
            isPageRefreshing = false;
        }

        if (!isPromptRequest) {
            // 非 /prompt 请求，直接发送原始请求（走 Nginx 代理）
            return originalFetch(url, options);
        }

        // 重写URL - 只对 /prompt 请求做处理
        const rewrittenUrl = rewriteUrl(url);

        console.log('[ComfyUI Queue] 拦截到工作流执行请求');

        // 获取当前用户信息
        const userInfo = getCurrentUserInfo();
        if (!userInfo.username) {
            console.error('[ComfyUI Queue] 无法获取用户信息');
            return originalFetch(url, options);
        }

        // 转发到教学系统后端代理API（不需要username，从token获取）
        const proxyUrl = `${CONFIG.API_BASE_URL}/comfy_proxy/execute`;

        showNotification('info', '正在提交工作流...');

        return originalFetch(proxyUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders(),
            },
            body: options.body
        })
        .then(async response => {
            const data = await response.json();

            if (data.status === 'queued') {
                // 进入排队
                console.log('%c[ComfyUI Queue] ════════════════════════════════', 'color: #f59e0b; font-weight: bold');
                console.log('%c[ComfyUI Queue] 📋 进入排队队列', 'color: #f59e0b; font-size: 14px');
                console.log('%c[ComfyUI Queue] ─────────────────────────────────', 'color: #f59e0b');
                console.log(`%c[ComfyUI Queue] 👤 用户: ${userInfo.username}`, 'color: #3b82f6');
                console.log(`%c[ComfyUI Queue] 🆔 任务ID: ${data.task_id}`, 'color: #3b82f6');
                console.log(`%c[ComfyUI Queue] 🔢 排队位置: 前方还有 ${data.position} 人`, 'color: #10b981; font-size: 16px; font-weight: bold');
                console.log(`%c[ComfyUI Queue] 💻 最大并发: ${data.max_concurrent} 人`, 'color: #6366f1');
                console.log('%c[ComfyUI Queue] ════════════════════════════════', 'color: #f59e0b; font-weight: bold');
                console.log('%c[ComfyUI Queue] ⏳ 等待执行中...', 'color: #f59e0b');
                console.log('');

                showQueueNotification(data);
                currentTaskId = data.task_id;
                startPolling(data.task_id);
                // 返回 Response 对象，避免 u.json is not a function 错误
                return new Response(JSON.stringify({
                    prompt_id: `queue_${data.task_id}`,
                    number: Math.floor(Math.random() * 1000000),
                    queue_info: data
                }), {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                });
            } else if (data.status === 'completed') {
                // 直接执行完成
                console.log('[ComfyUI Queue] 执行完成:', data);
                showNotification('success', '工作流执行完成！');
                hideQueueNotification();
                // 返回 ComfyUI 格式的 Response 对象
                return new Response(JSON.stringify({
                    prompt_id: data.result?.prompt_id || `completed_${Date.now()}`,
                    number: data.result?.number || 0
                }), {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                });
            } else {
                // 其他状态
                return new Response(JSON.stringify(data), {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                });
            }
        })
        .catch(error => {
            console.error('[ComfyUI Queue] 请求失败:', error);
            showNotification('error', '请求失败: ' + error.message);

            // 失败时降级到原始请求（直接访问ComfyUI）
            return originalFetch(url, options);
        });
    };

    // ==================== 辅助函数 ====================

    /**
     * 获取当前用户信息
     */
    function getCurrentUserInfo() {
        // 从localStorage获取（教学系统存储的用户信息）
        try {
            const userStr = localStorage.getItem('user');
            if (userStr) {
                const user = JSON.parse(userStr);
                return { username: user.username };
            }
        } catch (e) {
            console.warn('[ComfyUI Queue] 无法从localStorage读取用户信息');
        }

        // 从URL路径获取（格式: /comfyui-direct/{port}/ 或 /comfyui/{username}/{port}）
        const pathMatch1 = window.location.pathname.match(/\/comfyui-direct\/(\d+)\//);
        const pathMatch2 = window.location.pathname.match(/\/comfyui\/([^\/]+)\/(\d+)/);
        if (pathMatch2) {
            return { username: pathMatch2[1], port: pathMatch2[2] };
        }

        // 从window全局变量获取（如果通过代理页面设置）
        if (window.COMFY_USERNAME) {
            return { username: window.COMFY_USERNAME };
        }

        return {};
    }

    /**
     * 获取认证头
     */
    function getAuthHeaders() {
        try {
            // 优先使用后端注入的token
            if (window.COMFY_AUTH_TOKEN) {
                return { 'Authorization': `Bearer ${window.COMFY_AUTH_TOKEN}` };
            }
            // 其次从localStorage获取
            const token = localStorage.getItem('token');
            if (token) {
                return { 'Authorization': `Bearer ${token}` };
            }
        } catch (e) {}
        return {};
    }

    /**
     * 模拟ComfyUI的响应格式
     */
    function mockComfyUIResponse(queueData) {
        // 返回一个模拟的prompt_id，让ComfyUI暂时接受响应
        // 实际结果会在轮询完成后处理
        return {
            prompt_id: `queue_${queueData.task_id}`,
            number: Math.floor(Math.random() * 1000000),
            queue_info: queueData
        };
    }

    // ==================== 轮询队列状态 ====================

    /**
     * 开始轮询任务状态
     */
    function startPolling(taskId) {
        stopPolling();
        pollCount = 0;

        pollTimer = setInterval(() => {
            pollTaskStatus(taskId);
        }, CONFIG.POLL_INTERVAL);
    }

    /**
     * 停止轮询
     */
    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    /**
     * 轮询任务状态
     */
    async function pollTaskStatus(taskId) {
        pollCount++;

        if (pollCount > CONFIG.MAX_POLL_RETRIES) {
            stopPolling();
            console.log('%c[ComfyUI Queue] ❌ 等待超时', 'color: #ef4444; font-weight: bold');
            showNotification('error', '等待超时，请刷新页面查看结果');
            hideQueueNotification();
            return;
        }

        try {
            const response = await originalFetch(`${CONFIG.API_BASE_URL}/comfy_proxy/status/${taskId}`);
            const data = await response.json();

            console.log('[ComfyUI Queue] 轮询状态:', data.status);

            // 调试：检查状态值
            if (data.status === 'queued') {
                console.log('[ComfyUI Queue] 进入 queued 分支');
                // 仍在排队
                console.log(`%c[ComfyUI Queue] 🔄 轮询 #${pollCount} - 等待中... 前方还有 ${data.position} 人`, 'color: #6b7280');
            } else if (data.status === 'processing') {
                console.log('[ComfyUI Queue] 进入 processing 分支');
                // 开始处理
                console.log('');
                console.log('%c[ComfyUI Queue] ════════════════════════════════', 'color: #10b981; font-weight: bold');
                console.log('%c[ComfyUI Queue] ✅ 开始执行工作流！', 'color: #10b981; font-size: 14px; font-weight: bold');
                console.log('%c[ComfyUI Queue] ─────────────────────────────────', 'color: #10b981');
                console.log(`%c[ComfyUI Queue] ⏱️ 等待时间: ${pollCount * 2} 秒`, 'color: #3b82f6');
                console.log('%c[ComfyUI Queue] ════════════════════════════════', 'color: #10b981; font-weight: bold');
                console.log('');

                hideQueueNotification();
                showProcessingNotification();
            } else if (data.status === 'completed') {
                console.log('[ComfyUI Queue] 进入 completed 分支');
                // 完成
                stopPolling();
                console.log('');
                console.log('%c[ComfyUI Queue] ════════════════════════════════', 'color: #10b981; font-weight: bold');
                console.log('%c[ComfyUI Queue] 🎉 执行完成！', 'color: #10b981; font-size: 16px; font-weight: bold');
                console.log('%c[ComfyUI Queue] ─────────────────────────────────', 'color: #10b981');
                console.log(`%c[ComfyUI Queue] 🆔 prompt_id: ${data.result?.prompt_id}`, 'color: #6366f1');
                console.log(`%c[ComfyUI Queue] 🔢 任务序号: ${data.result?.number}`, 'color: #6366f1');
                console.log(`%c[ComfyUI Queue] ⏱️ 总耗时: ${pollCount * 2} 秒`, 'color: #3b82f6');
                console.log('%c[ComfyUI Queue] ════════════════════════════════', 'color: #10b981; font-weight: bold');
                console.log('');

                // 关闭所有通知
                console.log('[ComfyUI Queue] 准备关闭通知');
                console.log('[ComfyUI Queue] 查找 queue-notification:', document.getElementById('comfyui-queue-notification'));
                console.log('[ComfyUI Queue] 查找 processing-notification:', document.getElementById('comfyui-processing-notification'));
                hideQueueNotification();
                hideProcessingNotification();
                console.log('[ComfyUI Queue] 关闭通知完成');
                // 显示执行完成通知
                showNotification('success', '工作流执行完成！');
                // 不刷新页面，让用户自己查看结果
            } else if (data.status === 'failed') {
                console.log('[ComfyUI Queue] 进入 failed 分支');
                // 失败
                stopPolling();
                console.log('');
                console.log('%c[ComfyUI Queue] ════════════════════════════════', 'color: #ef4444; font-weight: bold');
                console.log('%c[ComfyUI Queue] ❌ 执行失败', 'color: #ef4444; font-size: 14px; font-weight: bold');
                console.log('%c[ComfyUI Queue] ─────────────────────────────────', 'color: #ef4444');
                console.log(`%c[ComfyUI Queue] 错误: ${data.result?.error || '未知错误'}`, 'color: #ef4444');
                console.log('%c[ComfyUI Queue] ════════════════════════════════', 'color: #ef4444; font-weight: bold');
                console.log('');

                hideAllNotifications();
                showNotification('error', '执行失败: ' + (data.result?.error || '未知错误'));
            } else {
                console.log('[ComfyUI Queue] 进入未知分支, status:', data.status);
            }
        } catch (error) {
            console.error('[ComfyUI Queue] 轮询失败:', error);
        }
    }

    // ==================== 通知显示 ====================

    /**
     * 显示排队通知
     */
    function showQueueNotification(data) {
        const notification = createElement('div', 'comfyui-queue-notification', {
            innerHTML: `
                <div class="comfyui-notification-header">⏳ 系统繁忙</div>
                <div class="comfyui-notification-body">
                    前方还有 <strong>${data.position}</strong> 人排队<br>
                    最多支持 ${data.max_concurrent} 人同时执行
                </div>
                <div class="comfyui-notification-progress">
                    <div class="comfyui-progress-bar" style="width: ${Math.min(100, (data.position / data.max_concurrent) * 100)}%"></div>
                </div>
            `
        });
        document.body.appendChild(notification);
    }

    /**
     * 显示处理中通知
     */
    function showProcessingNotification() {
        // 【核心修复】如果已经存在提示框，直接返回，不要再创建新的
        if (document.getElementById('comfyui-processing-notification')) {
            return;
        }

        const notification = createElement('div', 'comfyui-processing-notification', {
            innerHTML: `
                <div class="comfyui-notification-header">🔄 正在执行</div>
                <div class="comfyui-notification-body">
                    工作流正在执行中，请稍候...
                </div>
                <div class="comfyui-spinner"></div>
            `
        });
        document.body.appendChild(notification);
    }

    /**
     * 显示通用通知
     */
    function showNotification(type, message) {
        const icons = {
            info: 'ℹ️',
            success: '✅',
            error: '❌',
            warning: '⚠️'
        };

        const notification = createElement('div', 'comfyui-toast-notification', {
            innerHTML: `${icons[type] || ''} ${message}`,
            className: `comfyui-toast comfyui-toast-${type}`
        });
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('comfyui-toast-hide');
            setTimeout(() => notification.remove(), 300);
        }, CONFIG.NOTIFICATION_DURATION);
    }

    /**
     * 隐藏排队通知
     */
    function hideQueueNotification() {
        const el = document.getElementById('comfyui-queue-notification');
        if (el) el.remove();
    }

    /**
     * 隐藏处理中通知
     */
    function hideProcessingNotification() {
        const els = document.querySelectorAll('#comfyui-processing-notification');
        els.forEach(el => el.remove());
    }

    /**
     * 隐藏所有通知
     */
    function hideAllNotifications() {
        hideQueueNotification();
        hideProcessingNotification();
    }

    /**
     * 创建DOM元素
     */
    function createElement(tag, id, options = {}) {
        const el = document.createElement(tag);
        el.id = id;
        if (options.innerHTML) {
            el.innerHTML = options.innerHTML;
        }
        if (options.className) {
            el.className = options.className;
        }
        return el;
    }

    // ==================== 注入样式 ====================
    const style = document.createElement('style');
    style.textContent = `
        /* 排队通知 */
        #comfyui-queue-notification,
        #comfyui-processing-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            z-index: 999999;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            min-width: 250px;
            max-width: 350px;
        }

        .comfyui-notification-header {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .comfyui-notification-body {
            font-size: 14px;
            opacity: 0.95;
            line-height: 1.5;
        }

        .comfyui-notification-progress {
            margin-top: 12px;
            height: 4px;
            background: rgba(255,255,255,0.3);
            border-radius: 2px;
            overflow: hidden;
        }

        .comfyui-progress-bar {
            height: 100%;
            background: white;
            transition: width 0.3s ease;
        }

        .comfyui-spinner {
            margin-top: 12px;
            width: 24px;
            height: 24px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: comfyui-spin 1s linear infinite;
        }

        @keyframes comfyui-spin {
            to { transform: rotate(360deg); }
        }

        /* Toast通知 */
        .comfyui-toast-notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }

        .comfyui-toast-info { background: #3b82f6; }
        .comfyui-toast-success { background: #10b981; }
        .comfyui-toast-error { background: #ef4444; }
        .comfyui-toast-warning { background: #f59e0b; }

        .comfyui-toast-hide {
            opacity: 0;
            transform: translateY(20px);
        }
    `;
    document.head.appendChild(style);

    console.log('[ComfyUI Queue] 队列代理脚本已加载');
})();
