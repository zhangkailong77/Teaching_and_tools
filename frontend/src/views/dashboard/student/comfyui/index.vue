<template>
  <div class="comfyui-proxy-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-content">
        <div class="spinner"></div>
        <h2>🚀 正在启动 ComfyUI 环境</h2>
        <p>系统正在唤醒 GPU 资源，这可能需要 30-60 秒...</p>
        <p class="tip">提示：请勿关闭此窗口</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-content">
        <div class="error-icon">❌</div>
        <h2>启动失败</h2>
        <p>{{ error }}</p>
        <el-button type="primary" @click="retry">重试</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </div>

    <!-- ComfyUI iframe -->
    <div v-else class="comfyui-container">
      <!-- 排队状态横幅 -->
      <div v-if="queueInfo" class="queue-banner" :class="getQueueStatus(queueInfo)">
        <div class="queue-content">
          <span class="queue-icon">{{ getQueueIcon(queueInfo) }}</span>
          <span class="queue-text">{{ getQueueText(queueInfo) }}</span>
          <span class="queue-detail">{{ getQueueDetail(queueInfo) }}</span>
        </div>
      </div>

      <!-- ComfyUI iframe -->
      <iframe
        ref="comfyIframe"
        :src="comfyUrl"
        class="comfyui-iframe"
        @load="onIframeLoad"
      ></iframe>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import request from '@/utils/request';

const router = useRouter();
const userStore = useUserStore();

// 使用computed确保获取到username
const username = computed(() => {
  return userStore.userInfo?.username || userStore.token || null;
});

const loading = ref(true);
const error = ref('');
const comfyUrl = ref('');
const comfyIframe = ref<HTMLIFrameElement | null>(null);
const queueInfo = ref<any>(null);

let queueCheckTimer: number | null = null;

// 启动 ComfyUI
const startComfyUI = async () => {
  loading.value = true;
  error.value = '';

  // 确保用户信息已加载
  if (!userStore.userInfo?.username) {
    try {
      await userStore.fetchUserInfo();
    } catch (e) {
      console.error('获取用户信息失败:', e);
    }
  }

  const currentUsername = userStore.userInfo?.username;
  if (!currentUsername) {
    error.value = '无法获取用户信息，请重新登录';
    loading.value = false;
    return;
  }

  try {
    const res = await request.post<any, any>('/practice/start-practice', {}, {
      timeout: 120000
    });

    if (res.port) {
      // 判断环境：开发环境直接访问 GPU，生产环境使用 Nginx 代理
      const isDev = import.meta.env.DEV;

      if (isDev) {
        // 开发环境：直接访问 GPU 服务器（需要 GPU 服务器开启 CORS）
        comfyUrl.value = `http://192.168.150.2:${res.port}/`;
      } else {
        // 生产环境：使用 Nginx 代理路径
        // URL格式: /comfyui/{username}/{port}
        comfyUrl.value = `/comfyui/${currentUsername}/${res.port}/`;
      }
      loading.value = false;
      startQueueCheck();
    } else {
      throw new Error('未获取到访问地址');
    }
  } catch (err: any) {
    error.value = err.message || '启动失败，请联系管理员';
    loading.value = false;
  }
};

const retry = () => {
  startComfyUI();
};

const goBack = () => {
  router.back();
};

// iframe加载完成
const onIframeLoad = () => {
  console.log('[ComfyUI Proxy] iframe 加载完成');

  // 尝试注入排队脚本到iframe中
  injectQueueScriptToIframe();

  // 设置iframe窗口变量
  try {
    if (comfyIframe.value && comfyIframe.value.contentWindow) {
      (comfyIframe.value.contentWindow as any).COMFY_USERNAME = userStore.username;
      (comfyIframe.value.contentWindow as any).COMFY_PROXY_BASE_URL = '/api/v1';
      console.log('[ComfyUI Proxy] 已设置iframe窗口变量');
    }
  } catch (e) {
    console.warn('[ComfyUI Proxy] 无法设置iframe变量（跨域）:', e);
  }
};

// 注入排队脚本到iframe
const injectQueueScriptToIframe = () => {
  try {
    const iframe = comfyIframe.value;
    if (!iframe || !iframe.contentDocument) {
      console.warn('[ComfyUI Proxy] 无法访问iframe文档');
      return;
    }

    const doc = iframe.contentDocument;

    // 检查是否已注入
    if (doc.querySelector('script[src*="comfyui-queue.js"]')) {
      console.log('[ComfyUI Proxy] 脚本已存在，跳过注入');
      return;
    }

    // 创建并注入脚本
    const script = doc.createElement('script');
    script.src = '/static/js/comfyui-queue.js';
    script.async = false;
    script.onload = () => {
      console.log('[ComfyUI Proxy] 脚本注入成功');
    };
    script.onerror = () => {
      console.error('[ComfyUI Proxy] 脚本加载失败');
    };

    doc.head.appendChild(script);
    console.log('[ComfyUI Proxy] 正在注入排队脚本...');
  } catch (e) {
    console.warn('[ComfyUI Proxy] 注入脚本失败:', e);
  }
};

// 检查队列状态
const startQueueCheck = () => {
  queueCheckTimer = window.setInterval(async () => {
    try {
      const res = await request.get('/comfy_proxy/queue/status');
      queueInfo.value = res;
    } catch (e) {
      // 忽略错误
    }
  }, 5000);
};

const stopQueueCheck = () => {
  if (queueCheckTimer) {
    clearInterval(queueCheckTimer);
    queueCheckTimer = null;
  }
};

const getQueueStatus = (info: any) => {
  if (info.available_slots > 0) return 'idle';
  if (info.queue_length > 0) return 'busy';
  return 'full';
};

const getQueueIcon = (status: string) => {
  const icons = { idle: '✅', busy: '⏳', full: '🔴' };
  return icons[status as keyof typeof icons] || 'ℹ️';
};

const getQueueText = (info: any) => {
  if (info.available_slots > 0) {
    return `系统空闲，可用名额: ${info.available_slots}/${info.max_concurrent}`;
  } else if (info.queue_length > 0) {
    return `系统繁忙，当前排队: ${info.queue_length} 人`;
  } else {
    return `系统繁忙，正在处理: ${info.processing_count}/${info.max_concurrent}`;
  }
};

const getQueueDetail = (info: any) => {
  if (info.queue_length > 0) {
    return `最多支持 ${info.max_concurrent} 人同时执行`;
  }
  return '';
};

onMounted(() => {
  startComfyUI();
});

onUnmounted(() => {
  stopQueueCheck();
});
</script>

<style scoped lang="scss">
.comfyui-proxy-page {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1a1a1a;
  overflow: hidden;
}

.loading-container,
.error-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content,
.error-content {
  text-align: center;
  color: white;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  margin: 40px;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #00c9a7;
  border-radius: 50%;
  margin: 0 auto 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-content h2,
.error-content h2 {
  margin: 0 0 16px;
  font-size: 24px;
}

.loading-content p {
  margin: 8px 0;
  opacity: 0.8;
  font-size: 16px;
}

.tip {
  color: #00c9a7;
  font-weight: 500;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.comfyui-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.queue-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;

  &.idle {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  }

  &.full {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }
}

.queue-content {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-size: 14px;
  font-weight: 500;
}

.queue-icon {
  font-size: 18px;
}

.queue-text {
  font-size: 15px;
}

.queue-detail {
  font-size: 12px;
  opacity: 0.8;
}

.comfyui-iframe {
  flex: 1;
  width: 100%;
  border: none;
  background: white;
}
</style>
