<template>
  <div class="comfyui-proxy-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-content">
        <div class="spinner"></div>
        <h2>正在启动 ComfyUI 环境</h2>
        <p>系统正在唤醒 GPU 资源，这可能需要 30-60 秒...</p>
        <p class="tip">提示：请勿关闭此窗口</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-content">
        <div class="error-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <circle cx="24" cy="24" r="20" stroke="#f56c6c" stroke-width="2"/>
            <path d="M16 16l16 16M32 16l-16 16" stroke="#f56c6c" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <h2>启动失败</h2>
        <p>{{ error }}</p>
        <el-button type="primary" @click="retry">重试</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </div>

    <!-- ComfyUI iframe -->
    <div v-else class="comfyui-container">
      <!-- 排队状态横幅 + 课程资料按钮 -->
      <div v-if="queueInfo" class="queue-banner" :class="getQueueStatus(queueInfo)">
        <div class="queue-content">
          <span class="queue-icon">{{ getQueueIcon(queueInfo) }}</span>
          <span class="queue-text">{{ getQueueText(queueInfo) }}</span>
          <span class="queue-detail">{{ getQueueDetail(queueInfo) }}</span>
        </div>
        <!-- 课程资料按钮 -->
        <button class="course-material-btn" @click="openCourseDrawer">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M3 3h7l2 2h3v9H3V3z" stroke="currentColor" stroke-width="1.2" fill="none" stroke-linejoin="round"/>
            <path d="M8 8v4M8 10h2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          <span>课程资料</span>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="arrow-icon">
            <path d="M5 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <!-- ComfyUI iframe -->
      <iframe
        ref="comfyIframe"
        :src="comfyUrl"
        class="comfyui-iframe"
        @load="onIframeLoad"
      ></iframe>
    </div>

    <!-- 课程资料抽屉 -->
    <el-drawer
      v-model="courseDrawerVisible"
      direction="rtl"
      :size="700"
      :modal="false"
      :close-on-click-modal="false"
      :close-on-press-escape="true"
      :z-index="100"
      class="course-material-drawer"
      modal-class="course-drawer-modal"
      destroy-on-close
    >
      <!-- 抽屉内容 -->
      <div class="drawer-wrapper">
        <!-- 列表视图 -->
        <div v-if="!isReadingMode" class="list-view">
          <!-- 抽屉头部 -->
          <div class="drawer-header">
            <div class="header-left">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4 4h6l2 2h4v9H4V4z" stroke="#00c9a7" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
              </svg>
              <span class="header-title">课程资料</span>
            </div>
            <button class="close-btn" @click="courseDrawerVisible = false">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M5 5l8 8M13 5l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- 内容区 -->
          <div class="drawer-content">
            <!-- 加载状态 -->
            <div v-if="courseLoading" class="course-loading">
              <el-skeleton :rows="5" animated />
            </div>

            <!-- 课程标题 -->
            <div v-else-if="courseInfo" class="course-info-section">
              <div class="course-title">{{ courseInfo.name }}</div>
              <div class="course-meta">
                <span class="meta-item">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M7 2l5 3-5 3-5-3 5-3z" stroke="currentColor" stroke-width="1.2" fill="none"/>
                    <path d="M2 9l5 3 5-3" stroke="currentColor" stroke-width="1.2" fill="none"/>
                  </svg>
                  {{ pdfChapterCount }} 个 PDF
                </span>
              </div>
            </div>

            <!-- 章节列表 -->
            <div v-if="!courseLoading && chapterList.length > 0" class="chapters-list">
              <div
                v-for="(chapter, index) in chapterList"
                :key="chapter.id"
                class="chapter-item"
                :class="{ 'is-open': chapter.isOpen }"
              >
                <div class="chapter-header" @click="toggleChapter(index)">
                  <div class="left">
                    <svg class="arrow-icon" :class="{ rotated: chapter.isOpen }" width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span class="title">{{ chapter.title }}</span>
                  </div>
                  <div class="right">
                    <span class="count">{{ chapter.lessons.length }} 个 PDF</span>
                  </div>
                </div>

                <div class="lesson-group" v-show="chapter.isOpen">
                  <div
                    v-for="lesson in chapter.lessons"
                    :key="lesson.id"
                    class="lesson-item"
                    @click="handleLessonClick(lesson)"
                  >
                    <div class="lesson-left">
                      <svg class="pdf-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M4 2h6l3 3v9a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="#ff6b6b" stroke-width="1.5" fill="none"/>
                        <path d="M10 2v3h3" stroke="#ff6b6b" stroke-width="1.5" fill="none"/>
                        <text x="8" y="11" text-anchor="middle" font-size="5" fill="#ff6b6b" font-weight="bold">PDF</text>
                      </svg>
                      <span class="lesson-title">{{ lesson.title }}</span>
                    </div>
                    <div class="lesson-right">
                      <button class="read-btn">
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                          <polygon points="3 2 3 10 10 6" fill="currentColor"/>
                        </svg>
                        阅读
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-else-if="!courseLoading && chapterList.length === 0" class="empty-course-state">
              <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <rect x="8" y="8" width="48" height="48" rx="8" stroke="#e5e7eb" stroke-width="2"/>
                <path d="M20 24h24M20 32h24M20 40h16" stroke="#e5e7eb" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <p>暂无课程资料</p>
              <span>请先在课程中心解锁课程</span>
            </div>
          </div>
        </div>

        <!-- 沉浸式阅读视图 -->
        <div v-else class="reading-view" :class="{ 'sidebar-hidden': isSidebarCollapsed }">
          <!-- 目录切换按钮（浮动） -->
          <button class="sidebar-toggle-btn" @click="isSidebarCollapsed = !isSidebarCollapsed">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          <!-- 左侧目录 -->
          <div v-show="!isSidebarCollapsed" class="read-sidebar">
            <div class="rs-header">
              <button class="back-btn" @click="exitReadingMode">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M10 3l-5 5 5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                返回列表
              </button>
              <h3>课程目录</h3>
            </div>

            <div class="rs-body">
              <div v-for="chapter in chapterList" :key="chapter.id" class="rs-chapter">
                <div class="rs-c-title">{{ chapter.title }}</div>
                <div class="rs-lessons">
                  <div
                    v-for="lesson in chapter.lessons"
                    :key="lesson.id"
                    class="rs-l-item"
                    :class="{ active: currentLesson?.id === lesson.id }"
                    @click="handleLessonClick(lesson)"
                  >
                    <span class="lesson-title">{{ lesson.title }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧 PDF 阅读区 -->
          <div class="read-content">
            <!-- 顶部工具栏 -->
            <div class="read-toolbar">
              <div class="file-info">
                <span class="badge">PDF</span>
                <span class="name">{{ currentLesson?.title }}</span>
              </div>
              <div class="tools">
                <div class="zoom-ctrl">
                  <button @click="scale > 0.5 ? scale -= 0.1 : null">-</button>
                  <span>{{ Math.round(scale * 100) }}%</span>
                  <button @click="scale < 2.0 ? scale += 0.1 : null">+</button>
                </div>
                <!-- 关闭抽屉按钮 -->
                <button class="close-drawer-btn" @click="courseDrawerVisible = false" title="关闭">
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <path d="M5 5l8 8M13 5l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- PDF 内容区 -->
            <div
              class="read-stage"
              ref="pdfScrollRef"
              @mousedown="onPdfMouseDown"
              @mousemove="onPdfMouseMove"
              @mouseup="onPdfMouseUp"
              @mouseleave="onPdfMouseUp"
              :class="{ 'dragging': isDragging }"
            >
              <VuePdfEmbed
                v-if="currentPdfUrl"
                :source="currentPdfUrl"
                :width="600 * scale"
                class="pdf-canvas"
              />
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import request from '@/utils/request';
import { getCourseChapters, type CourseChapterItem } from '@/api/content';
import { getImgUrl } from '@/utils/index';
import VuePdfEmbed from 'vue-pdf-embed';

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

// 课程资料抽屉状态
const courseDrawerVisible = ref(false);
const courseLoading = ref(false);
const courseInfo = ref<any>(null);
const chapterList = ref<CourseChapterItem[]>([]);

// 阅读模式状态
const isReadingMode = ref(false);
const isSidebarCollapsed = ref(false);
const currentLesson = ref<any>(null);
const currentPdfUrl = ref('');
const scale = ref(1.0);
const pdfScrollRef = ref<HTMLElement | null>(null);

// PDF 拖拽状态
const isDragging = ref(false);
const dragStartX = ref(0);
const dragStartY = ref(0);
const scrollLeft = ref(0);
const scrollTop = ref(0);

// PDF 拖拽事件处理
const onPdfMouseDown = (e: MouseEvent) => {
  if (!pdfScrollRef.value) return;
  isDragging.value = true;
  dragStartX.value = e.clientX - pdfScrollRef.value.offsetLeft;
  dragStartY.value = e.clientY - pdfScrollRef.value.offsetTop;
  scrollLeft.value = pdfScrollRef.value.scrollLeft;
  scrollTop.value = pdfScrollRef.value.scrollTop;
};

const onPdfMouseMove = (e: MouseEvent) => {
  if (!isDragging.value || !pdfScrollRef.value) return;
  e.preventDefault();
  const x = e.clientX - pdfScrollRef.value.offsetLeft;
  const y = e.clientY - pdfScrollRef.value.offsetTop;
  const walkX = (x - dragStartX.value) * 1.5; // 拖拽速度
  const walkY = (y - dragStartY.value) * 1.5;
  pdfScrollRef.value.scrollLeft = scrollLeft.value - walkX;
  pdfScrollRef.value.scrollTop = scrollTop.value - walkY;
};

const onPdfMouseUp = () => {
  isDragging.value = false;
};

// 计算 PDF 章节总数
const pdfChapterCount = computed(() => {
  return chapterList.value.reduce((sum, ch) => sum + ch.lessons.length, 0);
});

let queueCheckTimer: number | null = null;

// 启动 ComfyUI
const startComfyUI = async () => {
  loading.value = true;
  error.value = '';

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
      const isDev = import.meta.env.DEV;

      if (isDev) {
        comfyUrl.value = `http://edu.yanzhiedu.cn:${res.port}/`;
      } else {
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

const onIframeLoad = () => {
  console.log('[ComfyUI Proxy] iframe 加载完成');
  injectQueueScriptToIframe();

  try {
    if (comfyIframe.value && comfyIframe.value.contentWindow) {
      (comfyIframe.value.contentWindow as any).COMFY_USERNAME = userStore.username;
      (comfyIframe.value.contentWindow as any).COMFY_PROXY_BASE_URL = '/api/v1';
    }
  } catch (e) {
    console.warn('[ComfyUI Proxy] 无法设置iframe变量（跨域）:', e);
  }
};

const injectQueueScriptToIframe = () => {
  try {
    const iframe = comfyIframe.value;
    if (!iframe || !iframe.contentDocument) return;

    const doc = iframe.contentDocument;
    if (doc.querySelector('script[src*="comfyui-queue.js"]')) return;

    const script = doc.createElement('script');
    script.src = '/static/js/comfyui-queue.js';
    script.async = false;
    script.onload = () => console.log('[ComfyUI Proxy] 脚本注入成功');
    script.onerror = () => console.error('[ComfyUI Proxy] 脚本加载失败');
    doc.head.appendChild(script);
  } catch (e) {
    console.warn('[ComfyUI Proxy] 注入脚本失败:', e);
  }
};

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

const getQueueIcon = (info: any) => {
  if (info.available_slots > 0) return '✓';
  if (info.queue_length > 0) return '⏱';
  return '•';
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

// 打开课程资料抽屉
const openCourseDrawer = async () => {
  courseDrawerVisible.value = true;

  // 等待 DOM 更新后，强制设置抽屉容器的 pointer-events
  nextTick(() => {
    // 关键修复：设置遮罩层 pointer-events: none，让它不阻止底层交互
    const modal = document.querySelector('.el-modal-drawer, .course-drawer-modal');
    if (modal) {
      (modal as HTMLElement).style.pointerEvents = 'none';
      console.log('[抽屉] 已设置遮罩层 pointer-events: none');
    }

    // 确保抽屉本身可交互
    const drawer = document.querySelector('.course-material-drawer');
    if (drawer) {
      (drawer as HTMLElement).style.pointerEvents = 'auto';
      console.log('[抽屉] 已设置抽屉 pointer-events: auto');
    }
  });

  const hasCourseInfo = courseInfo.value !== null;
  const hasChapterList = chapterList.value && chapterList.value.length > 0;
  const shouldLoad = !hasCourseInfo && !hasChapterList;

  if (shouldLoad) {
    await loadCourseData();
  }
};

// 加载课程数据
const loadCourseData = async () => {
  courseLoading.value = true;

  try {
    const courses = await request.get<any, any[]>('/content/courses/me');

    // 查找包含 AI 的课程
    const targetCourse = courses.find((c: any) => {
      const name = c.name || '';
      return name.includes('AI') || name.includes('跨境电商') || name.includes('视觉营销');
    });

    if (targetCourse) {
      courseInfo.value = targetCourse;

      // 获取课程章节 - 使用 public_id
      const courseId = targetCourse.public_id || targetCourse.id.toString();
      const chapters = await getCourseChapters(courseId);

      // 只显示 PDF 类型的课时
      const pdfChapters = chapters
        .map((chapter: any) => ({
          ...chapter,
          lessons: chapter.lessons.filter((l: any) => l.type === 'pdf'),
          isOpen: false
        }))
        .filter((chapter: any) => chapter.lessons.length > 0);

      // 默认展开第一个章节
      if (pdfChapters.length > 0) {
        pdfChapters[0].isOpen = true;
      }

      chapterList.value = pdfChapters;
    } else {
      courseInfo.value = null;
    }
  } catch (e: any) {
    console.error('[课程资料] 加载课程数据失败:', e);
  } finally {
    courseLoading.value = false;
  }
};

// 切换章节展开/收起
const toggleChapter = (index: number) => {
  chapterList.value[index].isOpen = !chapterList.value[index].isOpen;
};

// 处理课时点击 - 进入阅读模式
const handleLessonClick = (lesson: any) => {
  if (!lesson.file_url) return;

  currentLesson.value = lesson;
  currentPdfUrl.value = getImgUrl(lesson.file_url);
  scale.value = 1.0;
  isReadingMode.value = true;

  nextTick(() => {
    if (pdfScrollRef.value) {
      pdfScrollRef.value.scrollTop = 0;
    }
  });
};

// 退出阅读模式
const exitReadingMode = () => {
  isReadingMode.value = false;
  currentLesson.value = null;
  currentPdfUrl.value = '';
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
  margin-bottom: 16px;
  color: #f56c6c;
}

.comfyui-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.queue-banner {
  background: linear-gradient(135deg, #00c9a7 0%, #00a896 100%);
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

.course-material-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);

  &:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateX(-2px);

    .arrow-icon {
      transform: translateX(2px);
    }
  }

  .arrow-icon {
    transition: transform 0.2s ease;
  }
}

.comfyui-iframe {
  flex: 1;
  width: 100%;
  border: none;
  background: white;
}

// 抽屉样式 - 允许底层交互
// 让抽屉容器不阻止底层点击，但抽屉本身可交互
:deep(.el-drawer__container) {
  pointer-events: none;
}

:deep(.course-material-drawer) {
  pointer-events: auto;

  .el-drawer__header {
    padding: 0;
    margin-bottom: 0;
  }

  .el-drawer__body {
    padding: 0;
  }

  .el-drawer__close {
    display: none;
  }
}

.drawer-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

// ===== 列表视图 =====
.list-view {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #fafafa;
  flex-shrink: 0;

  .header-left {
    display: flex;
    align-items: center;
    gap: 10px;

    .header-title {
      font-size: 16px;
      font-weight: 600;
      color: #1a1a1a;
    }
  }

  .close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    border-radius: 6px;
    cursor: pointer;
    color: #999;
    transition: all 0.2s ease;

    &:hover {
      background: #f5f5f5;
      color: #666;
    }
  }
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
}

.course-loading {
  padding: 20px;
}

.course-info-section {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;

  .course-title {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 12px;
    line-height: 1.4;
  }

  .course-meta {
    display: flex;
    gap: 16px;

    .meta-item {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      color: #666;
    }
  }
}

// 章节列表
.chapters-list {
  padding: 16px;

  .chapter-item {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    background: white;
    margin-bottom: 12px;

    &.is-open {
      border-color: #00c9a7;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);

      .chapter-header .arrow-icon {
        transform: rotate(0deg);
      }
    }

    .chapter-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 18px;
      background-color: #fafafa;
      cursor: pointer;
      user-select: none;
      transition: background-color 0.2s ease;

      &:hover {
        background-color: #f5f5f5;
      }

      .left {
        display: flex;
        align-items: center;
        gap: 10px;

        .arrow-icon {
          color: #999;
          transition: transform 0.3s ease;
          transform: rotate(-90deg);
          flex-shrink: 0;

          &.rotated {
            transform: rotate(0deg);
          }
        }

        .title {
          font-size: 15px;
          font-weight: 600;
          color: #333;
        }
      }

      .right {
        .count {
          font-size: 12px;
          color: #999;
          background: #f5f5f5;
          padding: 3px 10px;
          border-radius: 10px;
        }
      }
    }

    .lesson-group {
      border-top: 1px solid #e5e7eb;
      background: white;

      .lesson-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 18px 12px 44px;
        border-bottom: 1px solid #f9f9f9;
        cursor: pointer;
        transition: all 0.2s ease;

        &:last-child {
          border-bottom: none;
        }

        &:hover {
          background-color: #fafafa;

          .lesson-title {
            color: #00c9a7;
          }

          .read-btn {
            background: #00c9a7;
            color: white;
          }
        }

        .lesson-left {
          display: flex;
          align-items: center;
          gap: 10px;
          flex: 1;
          min-width: 0;

          .pdf-icon {
            flex-shrink: 0;
          }

          .lesson-title {
            font-size: 14px;
            color: #555;
            transition: color 0.2s ease;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }

        .lesson-right {
          flex-shrink: 0;
        }
      }
    }
  }
}

.read-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  padding: 5px 12px;
  border-radius: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(102, 126, 234, 0.1);
  color: #00c9a7;
  border: 1px solid transparent;

  &:hover {
    background: #00c9a7;
    color: white;
  }
}

.empty-course-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #999;

  p {
    margin: 16px 0 8px 0;
    font-size: 16px;
    font-weight: 500;
  }

  span {
    font-size: 14px;
    color: #bbb;
  }
}

// ===== 沉浸式阅读视图 =====
.reading-view {
  width: 100%;
  height: 100%;
  display: flex;
  overflow: hidden;
  position: relative;

  // 目录切换按钮（浮动）
  .sidebar-toggle-btn {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    z-index: 10;
    transition: left 0.3s ease;
    width: 32px;
    height: 60px;
    background: white;
    border: 1px solid #e5e7eb;
    border-left: none;
    border-radius: 0 8px 8px 0;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);

    svg {
      transition: transform 0.2s ease;
      transform: rotate(180deg);  // 修改：默认旋转180度
    }

    &:hover {
      background: #00c9a7;
      color: white;
      width: 36px;
    }
  }

  // 当侧边栏隐藏时，按钮移到左边缘
  &.sidebar-hidden .sidebar-toggle-btn {
    left: 0;

    svg {
      transform: rotate(0deg);  // 修改：旋转回0度
    }
  }

  // 左侧目录
  .read-sidebar {
    width: 260px;
    background: #fafafa;
    border-right: 1px solid #e5e7eb;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;

    .rs-header {
      padding: 16px;
      border-bottom: 1px solid #e5e7eb;

      .back-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #666;
        background: none;
        border: none;
        padding: 0;
        cursor: pointer;
        margin-bottom: 12px;
        transition: color 0.2s ease;

        &:hover {
          color: #00c9a7;
        }
      }

      h3 {
        font-size: 15px;
        color: #333;
        margin: 0;
      }
    }

    .rs-body {
      flex: 1;
      overflow-y: auto;
      padding: 12px;

      .rs-chapter {
        margin-bottom: 16px;

        .rs-c-title {
          font-size: 12px;
          font-weight: 600;
          color: #999;
          padding: 4px 8px;
          margin-bottom: 4px;
        }

        .rs-lessons {
          .rs-l-item {
            padding: 10px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            color: #333;
            transition: all 0.2s ease;
            margin-bottom: 2px;

            .lesson-title {
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            &:hover {
              background: rgba(0, 0, 0, 0.04);
            }

            &.active {
              background: rgba(102, 126, 234, 0.1);
              color: #00c9a7;
              font-weight: 500;
            }
          }
        }
      }
    }
  }

  // 右侧阅读区
  .read-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #f0f2f3;
    min-width: 0; // 防止 flex 子元素溢出
    overflow: hidden; // 防止内容溢出

    // 顶部工具栏
    .read-toolbar {
      height: 56px;
      min-width: 100%; // 确保工具栏不会被压缩
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid #e5e7eb;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 20px;
      flex-shrink: 0;

      .file-info {
        display: flex;
        align-items: center;
        gap: 10px;

        .badge {
          background: #1a1a1a;
          color: white;
          padding: 3px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 600;
        }

        .name {
          font-size: 14px;
          font-weight: 600;
          color: #333;
          max-width: 300px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .tools {
        display: flex;
        align-items: center;
        gap: 12px;

        .zoom-ctrl {
          display: flex;
          align-items: center;
          gap: 8px;

          button {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: #555;
            transition: all 0.2s ease;

            &:hover:not(:disabled) {
              border-color: #00c9a7;
              color: #00c9a7;
            }

            &:disabled {
              opacity: 0.4;
              cursor: not-allowed;
            }
          }

          span {
            font-size: 13px;
            font-weight: 600;
            color: #555;
            min-width: 40px;
            text-align: center;
          }
        }

        // 关闭抽屉按钮
        .close-drawer-btn {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          cursor: pointer;
          color: #666;
          transition: all 0.2s ease;

          &:hover {
            background: #f56c6c;
            border-color: #f56c6c;
            color: white;
          }
        }
      }
    }

    // PDF 内容区
    .read-stage {
      flex: 1;
      overflow-y: auto;
      overflow-x: auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      align-items: flex-start; // 改为左对齐，避免放大时左边被截断
      cursor: grab;

      &.dragging {
        cursor: grabbing;
        user-select: none; // 防止拖拽时选中文本
      }

      .pdf-canvas {
        display: block;
        margin: 0 auto; // 默认水平居中
        pointer-events: none; // 防止 PDF 内容本身干扰拖拽

        :deep(.vue-pdf-embed) {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0;
        }

        :deep(.vue-pdf-embed__page) {
          margin-bottom: 20px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
          background: white;
        }
      }
    }
  }
}
</style>

<!-- 全局样式：解决抽屉阻止底层交互问题 -->
<style>
/* 抽屉遮罩层 - 设置为不拦截点击事件 */
.el-modal-drawer,
.course-drawer-modal {
  pointer-events: none !important;
}

/* 抽屉本身恢复点击交互能力 */
.el-drawer.course-material-drawer {
  pointer-events: auto !important;
}

/* 确保抽屉的所有子元素都可以交互 */
.el-drawer.course-material-drawer * {
  pointer-events: auto !important;
}
</style>
