<template>
  <div class="dashboard-container">
    <StudentSidebar />

    <main class="main-content">
      
      <!-- ================= 视图 A: 课程概览 (默认显示) ================= -->
      <div v-if="!isLearningMode" class="detail-view animate__fadeIn">
        <!-- 顶部导航 -->
        <header class="top-bar">
          <div class="breadcrumb">
            <span>工作台</span> / 
            <span class="link" @click="router.push('/dashboard/student')">课程中心</span> / 
            <span class="current">开始学习</span>
          </div>
        </header>

        <!-- 课程信息卡片 -->
        <div class="course-header">
          <div class="cover-box">
            <img :src="getImgUrl(courseInfo.cover)" alt="cover" />
          </div>
          <div class="info-box">
            <div class="tags">
              <span class="tag">实训课程</span>
              <span class="tag status active">进行中</span>
            </div>
            <h1>{{ courseInfo.name }}</h1>
            <p class="desc">{{ courseInfo.intro || '暂无简介' }}</p>
            
            <div class="stats-grid">
              <div class="stat-item">
                <div class="icon-box blue">📊</div>
                <div class="stat-info">
                  <div class="label">本课程任务数量</div>
                  <div class="value">
                    <span class="num">{{ courseInfo.task_count }}</span>
                    <span class="unit">个</span>
                  </div>
                </div>
              </div>
              <div class="stat-item">
                <div class="icon-box purple">⏱️</div>
                <div class="stat-info">
                  <div class="label">本课程任务总时长</div>
                  <div class="value">
                    <span class="num">{{ courseInfo.total_duration }}</span>
                    <span class="unit">min</span>
                  </div>
                </div>
              </div>
              <div class="stat-item">
                <div class="icon-box orange">📑</div>
                <div class="stat-info">
                  <div class="label">本课程课时数</div>
                  <div class="value">
                    <span class="num">{{ courseInfo.lesson_count }}</span>
                    <span class="unit">节</span>
                  </div>
                </div>
              </div>
              <div class="stat-item">
                <div class="icon-box green">🎓</div>
                <div class="stat-info">
                  <div class="label">课程类型</div>
                  <div class="value">
                    <span class="type-badge">{{ courseInfo.course_type }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部 Tabs -->
        <div class="course-tabs">
          <div class="tab-header">
            <span class="tab-item" :class="{ active: activeTab === 'intro' }" @click="activeTab = 'intro'">课程介绍</span>
            <span class="tab-item" :class="{ active: activeTab === 'chapters' }" @click="activeTab = 'chapters'">章节目录</span>
            <span class="tab-item" :class="{ active: activeTab === 'materials' }" @click="activeTab = 'materials'">课件资料</span>
            <span class="tab-item" :class="{ active: activeTab === 'videos' }" @click="activeTab = 'videos'">课程视频</span>
          </div>
          
          <div class="tab-content">
            <div v-if="activeTab === 'intro'" class="intro-text">
              <h3>关于本课程</h3>
              <p>{{ courseInfo.intro || '暂无详细介绍' }}</p>
            </div>
            <!-- 1. 章节目录 -->
            <div v-if="activeTab === 'chapters'" class="chapter-list">
              <div v-for="(chapter, index) in pdfChapterList" :key="chapter.id" class="chapter-item" :class="{ 'is-open': chapter.isOpen }">
                <div class="chapter-header" @click="toggleChapter(index)">
                  <div class="left"><span class="arrow-icon">▼</span><span class="title">{{ chapter.title }}</span></div>
                  <div class="right"><span class="count">{{ chapter.lessons.length }} 小节</span></div>
                </div>
                <div class="lesson-group" v-show="chapter.isOpen">
                  <div v-for="lesson in chapter.lessons" :key="lesson.id" class="lesson-item" @click="handleLessonClick(lesson)">
                    <div class="lesson-left">
                      <span class="type-icon">{{ lesson.type === 'video' ? '▶️' : '' }}</span>
                      <span class="lesson-title">{{ lesson.title }}</span>
                    </div>
                    <div class="lesson-right">
                      <!-- ✅ 作业按钮逻辑 -->
                      <template v-if="lesson.assignment && lesson.assignment.status !== 'none'">
                        
                        <!-- 情况A: 已批改 -->
                        <span v-if="lesson.assignment.status === 'graded'" class="homework-tag score">
                          {{ lesson.assignment.score }}分
                        </span>

                        <!-- 情况B: 已提交 -->
                        <span v-else-if="lesson.assignment.status === 'submitted'" class="homework-tag submitted">
                          已提交
                        </span>

                        <!-- 情况C: 待做 (且课程已学完) -->
                        <button 
                          v-else-if="lesson.status === 2" 
                          class="btn-homework"
                          @click.stop="handleHomeworkClick(lesson)"
                        >
                          ✏️ 做作业
                        </button>
                        
                        <!-- 情况D: 待做 (但课程没学完) -->
                        <span v-else class="homework-tag locked" title="请先完成学习">
                          🔒 作业锁定
                        </span>

                      </template>

                      <button 
                        v-if="lesson.status === 2" 
                        class="status-btn finished"
                        @click.stop="handleLessonClick(lesson)"
                        title="点击复习"
                      >
                        已完成
                      </button>
                      
                      <button 
                        v-else-if="lesson.status === 1" 
                        class="status-btn learning" 
                        @click.stop="handleLessonClick(lesson)"
                      >
                        继续学习
                      </button>
                      
                      <button 
                        v-else 
                        class="status-btn start" 
                        @click.stop="handleLessonClick(lesson)"
                      >
                        开始学习
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 2. 课件资料 (PPT) -->
            <div v-if="activeTab === 'materials'" class="materials-list">
              <div class="material-item" v-for="item in materialList" :key="item.id">
                <div class="left">
                  <div class="icon-box ppt">P</div>
                  <div class="info"><div class="name">{{ item.title }}</div><div class="chapter-tag">{{ item.chapterTitle }}</div></div>
                </div>
                <div class="right">
                  <button class="btn-play" @click="handlePlayPPT(item.file_url, item.title)">▶ 幻灯片演示</button>
                </div>
              </div>
               <div v-if="materialList.length === 0" class="empty-state">暂无课件资料</div>
            </div>

            <!-- 3. 课程视频 -->
            <div v-if="activeTab === 'videos'" class="videos-container">
              <div class="video-layout">
                <!-- 左侧：视频播放器 -->
                <div class="video-player-section">
                  <div v-if="currentVideo" class="video-wrapper">
                    <video
                      ref="videoRef"
                      :src="getImgUrl(currentVideo.file_url)"
                      :poster="currentVideo.poster_url ? getImgUrl(currentVideo.poster_url) : ''"
                      controls
                      controlsList="nodownload"
                      class="video-element"
                      @play="onVideoPlay"
                      @pause="onVideoPause"
                      @timeupdate="onVideoTimeUpdate"
                      @ended="onVideoEnded"
                    >
                      您的浏览器不支持视频播放。
                    </video>
                    <!-- 自定义倍速控制 -->
                    <div class="video-controls">
                      <div class="speed-control">
                        <span class="speed-label">播放速度：</span>
                        <div class="speed-buttons">
                          <button
                            v-for="speed in [0.5, 1, 1.25, 1.5, 2]"
                            :key="speed"
                            :class="{ active: playbackSpeed === speed }"
                            @click="setPlaybackSpeed(speed)"
                            class="speed-btn"
                          >
                            {{ speed }}x
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="video-placeholder">
                    <div class="placeholder-icon">▶</div>
                    <p>请从右侧列表选择视频播放</p>
                  </div>
                </div>

                <!-- 右侧：视频列表 -->
                <div class="video-list-section">
                  <div class="video-list-content">
                    <div v-for="chapter in videoChapterList" :key="chapter.id" class="video-chapter">
                      <div class="video-chapter-title">{{ chapter.title }}</div>
                      <div
                        v-for="video in chapter.lessons"
                        :key="video.id"
                        :class="['video-item', { active: currentVideo?.id === video.id }]"
                        @click="playVideo(video)"
                      >
                        <div class="video-item-left">
                          <span class="video-icon">▶</span>
                          <span class="video-title">{{ video.title }}</span>
                        </div>
                        <div class="video-item-right">
                          <span v-if="video.duration" class="video-duration">{{ formatDuration(video.duration) }}</span>
                          <span v-if="currentVideo?.id === video.id" class="playing-indicator">播放中</span>
                        </div>
                      </div>
                    </div>
                    <div v-if="videoChapterList.length === 0" class="empty-state">暂无课程视频</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= 视图 B: 沉浸式学习模式 (复用教师端逻辑) ================= -->
      <div v-else class="learning-mode-view" ref="pdfContainerRef">
        <!-- 左侧：深色磨砂侧边栏 -->
        <div class="learn-sidebar">
          <div class="ls-header">
            <div class="back-btn" @click="exitLearningMode">
              <span>←</span> 退出学习
            </div>
            <h3>课程目录</h3>
          </div>
          
          <div class="ls-body">
            <div v-for="(chapter, cIndex) in pdfChapterList" :key="chapter.id" class="ls-chapter">
              <div class="ls-c-title">{{ chapter.title }}</div>
              <div class="ls-lessons">
                <div 
                  v-for="lesson in chapter.lessons" 
                  :key="lesson.id" 
                  class="ls-l-item"
                  :class="{ active: currentLesson?.id === lesson.id }"
                  @click="handleLessonClick(lesson)"
                >
                  <span class="icon">{{ lesson.type === 'video' ? '▶' : '' }}</span>
                  <span class="text">{{ lesson.title }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：毛玻璃阅读器 -->
        <div class="learn-content">
          <!-- 顶部工具栏 -->
          <div class="glass-toolbar">
            <div class="file-info">
              <span class="badge">{{ currentLesson?.type === 'video' ? 'VIDEO' : 'PDF' }}</span>
              <span class="name">{{ currentLesson?.title }}</span>
            </div>
            <div class="tools">
              <!-- 缩放控制 -->
              <div class="zoom-ctrl">
                <button @click="scale > 0.5 ? scale -= 0.1 : null">-</button>
                <span>{{ Math.round(scale * 100) }}%</span>
                <button @click="scale < 2.0 ? scale += 0.1 : null">+</button>
              </div>
              <span class="divider">|</span>
              <button class="btn-fullscreen" @click="toggleFullscreen">
                {{ isFullscreen ? '退出全屏' : '⛶ 全屏' }}
              </button>
            </div>
          </div>

          <!-- 内容渲染区 -->
          <div class="content-stage" ref="scrollContainer" @scroll="handleScroll">
            <div class="pdf-paper-wrapper">
              <VuePdfEmbed 
                v-if="currentLesson?.type === 'pdf'"
                :source="getImgUrl(currentLesson.file_url)" 
                :width="800 * scale"
                @loaded="handlePdfLoaded"
                class="pdf-canvas"
              />
              <div v-else-if="currentLesson?.type === 'video'" class="video-box">
                <p>视频播放器暂未集成</p>
              </div>
              <div v-else class="empty-box">暂不支持预览</div>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= 视图 C: PPT 演示模式 (复用) ================= -->
      <div v-if="showPPTPlayer" class="ppt-player" :class="{ 'is-fullscreen': isFullscreen }" ref="pptContainerRef" @wheel.prevent="handlePPTWheel">
      <!-- 1. 顶部栏 (鼠标悬停显示) -->
      <div class="ppt-header">
        <div class="title">{{ pptTitle }}</div>
        <div class="controls">
          <button class="btn-icon" @click="closePPTPlayer" title="退出">✕</button>
        </div>
      </div>

      <!-- 2. 核心舞台 (居中显示单页) -->
      <div class="ppt-body">
        
        <!-- A. 左侧缩略图侧边栏 (仅在非全屏时显示) -->
        <div class="ppt-sidebar" v-if="!isFullscreen && pptTotalPages > 0" ref="pptSidebarRef">
          <div 
            v-for="pageNum in pptTotalPages" 
            :key="pageNum"
            class="thumb-item"
            :class="{ active: pageNum === pptCurrentPage }"
            @click="pptCurrentPage = pageNum"
            :id="`thumb-item-${pageNum}`"
          >
            <span class="thumb-index">{{ pageNum }}</span>
            <div class="thumb-preview">
              <!-- 渲染小尺寸 PDF 作为缩略图 -->
              <VuePdfEmbed
                :source="pptUrl"
                :page="pageNum"
                :width="200"
                class="thumb-canvas"
              />
            </div>
          </div>
        </div>

        <!-- B. 核心舞台 (右侧) -->
        <!-- 去掉了之前的 .ppt-stage 样式里的居中，改为 flex-grow -->
        <div class="ppt-stage" @click="changePPTPage(1)">
          <VuePdfEmbed
            :source="pptUrl"
            :page="pptCurrentPage"
            :width="dynamicPdfWidth"
            class="ppt-slide"
            @loaded="onPPTLoaded"
          />
        </div>

      </div>

      <!-- 3. 底部控制栏 (仿 WPS 播放条) -->
      <div class="ppt-footer">
        <!-- 翻页控制器 -->
        <div class="page-nav">
          <button class="nav-btn" @click.stop="changePPTPage(-1)" :disabled="pptCurrentPage <= 1">◀ 上一页</button>
          <span class="page-num">第 <b>{{ pptCurrentPage }}</b> / {{ pptTotalPages }} 页</span>
          <button class="nav-btn" @click.stop="changePPTPage(1)" :disabled="pptCurrentPage >= pptTotalPages">下一页 ▶</button>
        </div>

        <!-- 全屏按钮 -->
        <div class="fullscreen-tool">
          <button class="btn-fs" @click="triggerBrowserFullscreen">⛶ 全屏放映</button>
        </div>
      </div>
      </div>

      <!-- ================= 作业提交抽屉 ================= -->
      <el-drawer
        v-model="showHomeworkDrawer"
        title="作业提交"
        direction="rtl"
        size="500px"
      >
        <div class="homework-body">
          <div class="hw-header">
            <h3>{{ currentAssignment?.lessonTitle }}</h3>
            <div class="hw-meta">
              <span>截止时间: {{ currentAssignment?.deadline ? new Date(currentAssignment.deadline).toLocaleDateString() : '无限制' }}</span>
            </div>
          </div>

          <!-- 题目要求 -->
          <div class="hw-requirement">
            <h4>作业要求：</h4>
            <p>{{ currentAssignment?.contentRequirement }}</p>
          </div>

          <!-- 答题区 -->
          <div class="hw-answer-area">
            <h4>你的答案：</h4>
            <textarea 
              v-model="submissionContent" 
              rows="8" 
              placeholder="在此输入答案，或点击下方按钮上传截图..."
            ></textarea>
            
            <div class="toolbar">
              <button class="btn-icon" @click="triggerUpload">📷 上传图片</button>
              <input type="file" ref="uploadInputRef" accept="image/*" style="display:none" @change="handleUpload"/>
            </div>
          </div>

          <div class="hw-footer">
            <button class="btn-primary" @click="handleSubmitHomework" :disabled="isSubmitting">
              {{ isSubmitting ? '提交中...' : '提交作业' }}
            </button>
          </div>
        </div>
      </el-drawer>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import StudentSidebar from '@/components/StudentSidebar.vue';
import { getStudentCourseDetail, getStudentCourseChapters, updateProgress, type CourseItem, type CourseChapterItem } from '@/api/content';
import { submitHomework } from '@/api/homework';
import { uploadImage } from '@/api/common';
import { getImgUrl } from '@/utils/index';
import VuePdfEmbed from 'vue-pdf-embed';
import { useWindowSize } from '@vueuse/core';

const route = useRoute();
const router = useRouter();

// 状态
const courseInfo = ref<Partial<CourseItem>>({});
const chapterList = ref<CourseChapterItem[]>([]);
const activeTab = ref('chapters'); // 学生端默认进目录

// 学习模式状态
const isLearningMode = ref(false); // 是否进入学习模式
const currentLesson = ref<any>(null); // 当前正在看的课时
const pdfPageCount = ref(0); // 总页码
const isFullscreen = ref(false); // 全屏状态
const pdfContainerRef = ref<HTMLElement | null>(null); // 用于全屏的 DOM 引用
const scale = ref(1.0);

const scrollContainer = ref<HTMLElement | null>(null);

// 断点续读：待恢复的滚动位置
const pendingRestorePosition = ref<number | null>(null);
let isRestoringPosition = false; // 是否正在恢复位置（恢复期间禁止保存）
let pdfRenderMonitorTimer: any = null; // PDF渲染监控定时器
let lastScrollHeight = 0; // 上一次检测的scrollHeight

// PDF 加载完成回调
const handlePdfLoaded = (doc: any) => {
  pdfPageCount.value = doc.numPages || 0;
  console.log(`PDF加载完成，共 ${pdfPageCount.value} 页`);

  if (pendingRestorePosition.value === null) return;

  // 新策略：等待PDF完全渲染后再滚动，而不是立即滚动
  // 监控scrollHeight变化，当稳定下来（不再增长）时再滚动

  const el = scrollContainer.value;
  if (!el) return;

  // 重置状态
  lastScrollHeight = el.scrollHeight;
  isRestoringPosition = true;

  // 停止之前的监控定时器（如果有）
  if (pdfRenderMonitorTimer) {
    clearInterval(pdfRenderMonitorTimer);
    pdfRenderMonitorTimer = null;
  }

  // 每隔200ms检查scrollHeight是否稳定
  // 如果连续3次检查（600ms）scrollHeight不变，认为渲染完成
  let stableCount = 0;
  const CHECK_INTERVAL = 200; // 间隔更长的检查周期
  const STABLE_THRESHOLD = 3; // 连续3次稳定

  const checkAndRestore = () => {
    const container = scrollContainer.value;
    if (!container || pendingRestorePosition.value === null) {
      clearInterval(pdfRenderMonitorTimer);
      return;
    }

    const currentScrollHeight = container.scrollHeight;
    const clientHeight = container.clientHeight;
    const scrollContentHeight = currentScrollHeight - clientHeight;

    // 只在状态变化时输出日志，避免刷屏
    if (currentScrollHeight !== lastScrollHeight) {
      console.log(`PDF渲染中: scrollHeight=${currentScrollHeight}`);
      stableCount = 0;
      lastScrollHeight = currentScrollHeight;
    } else {
      stableCount++;
      if (stableCount === 1) {
        console.log(`PDF渲染基本完成，等待稳定...`);
      }
    }

    // 连续稳定3次，且内容高度大于0，可以滚动了
    if (stableCount >= STABLE_THRESHOLD && scrollContentHeight > 0) {
      clearInterval(pdfRenderMonitorTimer);
      pdfRenderMonitorTimer = null;

      const targetPercent = pendingRestorePosition.value;
      const targetScrollTop = Math.round((targetPercent / 100) * scrollContentHeight);

      container.scrollTop = targetScrollTop;
      console.log(`✅ 滚动到 ${targetScrollTop}px (${targetPercent}%)`);

      // 5秒后允许用户滚动保存
      setTimeout(() => {
        isRestoringPosition = false;
        pendingRestorePosition.value = null;
      }, 5000);
    }
  };

  // 立即检查一次
  checkAndRestore();

  // 开始监控
  pdfRenderMonitorTimer = setInterval(checkAndRestore, CHECK_INTERVAL);
};

// === PPT 演示模式专用状态 ===
const showPPTPlayer = ref(false);
const pptUrl = ref('');
const pptTitle = ref('');
const pptCurrentPage = ref(1);
const pptTotalPages = ref(0);
const pptScale = ref(1.0); // 缩放比例
const pptContainerRef = ref<HTMLElement | null>(null); // 全屏容器

// 2. 新增一个计算属性
const dynamicPdfWidth = computed(() => {
  if (isFullscreen.value) {
    return window.innerWidth;
  }
  return 1500;
});

// ✅ 新增：动态计算 PPT 宽度
const windowWidth = ref(window.innerWidth);

// 监听窗口大小变化，保证清晰度
window.addEventListener('resize', () => {
  windowWidth.value = window.innerWidth;
});

const pdfChapterList = computed(() => {
  return chapterList.value.map(chapter => ({
    ...chapter,
    lessons: chapter.lessons.filter(l => l.type === 'pdf')
  }));
});

// 定义侧边栏容器引用 (可选，配合 Template)
const pptSidebarRef = ref<HTMLElement | null>(null);
watch(pptCurrentPage, (newPage) => {
  nextTick(() => {
    const targetElement = document.getElementById(`thumb-item-${newPage}`);
    
    if (targetElement && !isFullscreen.value) {
      targetElement.scrollIntoView({
        behavior: 'smooth', 
        block: 'center',    
        inline: 'nearest'
      });
    }
  });
});

const materialList = computed(() => {
  const list: any[] = [];
  chapterList.value.forEach(chapter => {
    chapter.lessons.forEach(lesson => {
      if (lesson.type === 'ppt') {
        list.push({
          ...lesson,
          chapterTitle: chapter.title
        });
      }
    });
  });
  return list;
});

// === 视频播放相关状态 ===
const currentVideo = ref<any>(null); // 当前播放的视频
const videoRef = ref<HTMLVideoElement | null>(null);
const playbackSpeed = ref(1); // 播放速度

// 视频章节列表（过滤 type='video' 的课时）
const videoChapterList = computed(() => {
  return chapterList.value
    .map(chapter => ({
      ...chapter,
      lessons: chapter.lessons.filter(l => l.type === 'video')
    }))
    .filter(chapter => chapter.lessons.length > 0);
});

// 播放视频
const playVideo = (video: any) => {
  currentVideo.value = video;
  nextTick(() => {
    if (videoRef.value) {
      videoRef.value.play().catch(err => {
        console.log('自动播放被阻止，需要用户交互:', err);
      });
    }
  });
};

// 设置播放速度
const setPlaybackSpeed = (speed: number) => {
  playbackSpeed.value = speed;
  if (videoRef.value) {
    videoRef.value.playbackRate = speed;
  }
};

// 视频事件处理
const onVideoPlay = () => console.log('视频开始播放');
const onVideoPause = () => console.log('视频暂停');
const onVideoTimeUpdate = () => {
  // 可用于记录播放进度（如果需要）
};
const onVideoEnded = () => console.log('视频播放结束');

// 格式化时长（秒 -> MM:SS）
const formatDuration = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const handlePlayPPT = (fileUrl: string, title: string) => {
  if (!fileUrl) return alert('文件路径无效');
  
  // 依然使用 PDF 影子文件逻辑 (保证排版不乱)
  const pdfUrl = fileUrl.replace(/\.pptx?$/i, '_ppt.pdf');
  
  pptUrl.value = getImgUrl(pdfUrl);
  pptTitle.value = title;
  pptCurrentPage.value = 1; 
  pptScale.value = 1.0;
  showPPTPlayer.value = true;
};

// 2. 关闭演示
const closePPTPlayer = () => {
  showPPTPlayer.value = false;
  pptUrl.value = '';
};

// 3. 翻页逻辑
const changePPTPage = (delta: number) => {
  const newPage = pptCurrentPage.value + delta;
  if (newPage >= 1 && newPage <= pptTotalPages.value) {
    pptCurrentPage.value = newPage;
  }
};

// 4. 加载完成回调
const onPPTLoaded = (doc: any) => {
  pptTotalPages.value = doc.numPages;
};

// 5. 浏览器原生全屏
const triggerBrowserFullscreen = () => {
  if (pptContainerRef.value) {
    if (!document.fullscreenElement) {
      pptContainerRef.value.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }
};

// === ✅ 新增：滚轮翻页防抖 ===
let isWheeling = false;

const handlePPTWheel = (e: WheelEvent) => {
  // 如果正在翻页冷却中，忽略这次滚动
  if (isWheeling) return;
  
  // 开启冷却 (300毫秒内不接受新的滚动)
  isWheeling = true;
  setTimeout(() => { isWheeling = false; }, 300);

  // deltaY > 0 代表向下滚动 -> 下一页
  // deltaY < 0 代表向上滚动 -> 上一页
  if (e.deltaY > 0) {
    changePPTPage(1);
  } else {
    changePPTPage(-1);
  }
};

onMounted(async () => {
  const id = route.params.id as string;
  if (id) {
    // 调用学生专用 API
    const detail = await getStudentCourseDetail(id);
    courseInfo.value = detail;
    
    const chapters = await getStudentCourseChapters(id);
    if (chapters.length > 0) chapters[0].isOpen = true;
    chapterList.value = chapters;
  }
  window.addEventListener('resize', () => { windowWidth.value = window.innerWidth });
});


// ✅ 新增：滚动监听逻辑（断点续读版 + 防抖）
// last_position 存储滚动百分比 (0-100)，0=未开始，1-99=进行中，100=已完成

// 防抖定时器
let scrollSaveTimer: any = null;
let lastSavedPercent = 0;

const handleScroll = () => {
  const el = scrollContainer.value;
  if (!el || !currentLesson.value || !isLearningMode.value) return;

  // 恢复位置期间禁止保存
  if (isRestoringPosition) return;

  // 计算滚动百分比
  const scrollHeight = el.scrollHeight - el.clientHeight;
  const scrollPercent = scrollHeight > 0
    ? Math.round((el.scrollTop / scrollHeight) * 100)
    : 0;

  // 1. 判断是否"开始学习了" (滚动 > 0%)
  if (currentLesson.value.status === 0 && scrollPercent > 0) {

    // 更新本地状态
    currentLesson.value.status = 1;
    updateLocalListStatus(currentLesson.value.id, 1, scrollPercent);

    // 发送请求给后端
    updateProgress({
      lesson_id: currentLesson.value.id,
      status: 1,
      last_position: scrollPercent
    });

    lastSavedPercent = scrollPercent;
    return;
  }

  // 2. 判断是否"看完了" (滚动 >= 95%)
  const isBottom = scrollPercent >= 95;

  if (isBottom && currentLesson.value.status !== 2) {

    // 清除防抖定时器，立即保存
    if (scrollSaveTimer) {
      clearTimeout(scrollSaveTimer);
    }

    // 更新本地状态
    currentLesson.value.status = 2;
    updateLocalListStatus(currentLesson.value.id, 2, 100);

    // 发送请求给后端
    updateProgress({
      lesson_id: currentLesson.value.id,
      status: 2,
      last_position: 100
    });

    lastSavedPercent = 100;
    return;
  }

  // 3. 实时保存进行中的进度（防抖：每1秒最多保存一次）
  // 只有滚动变化超过 15% 才保存（防止 PDF 懒加载导致的不准确）
  if (scrollPercent > 0 && scrollPercent < 95 && currentLesson.value.status !== 2) {
    if (Math.abs(scrollPercent - lastSavedPercent) >= 15) {
      // 清除之前的定时器
      if (scrollSaveTimer) {
        clearTimeout(scrollSaveTimer);
      }

      // 设置新的防抖定时器，1秒后保存
      scrollSaveTimer = setTimeout(() => {
        updateProgress({
          lesson_id: currentLesson.value.id,
          status: 1,
          last_position: scrollPercent
        });
        // 更新本地状态
        updateLocalListStatus(currentLesson.value.id, 1, scrollPercent);
        lastSavedPercent = scrollPercent;
      }, 1000);
    }
  }
};

// 辅助：更新本地列表状态 (避免刷新页面才变)
const updateLocalListStatus = (lessonId: number, status: number, lastPosition?: number) => {
  pdfChapterList.value.forEach(ch => {
    const l = ch.lessons.find(x => x.id === lessonId);
    if (l) {
      l.status = status;
      if (lastPosition !== undefined) l.last_position = lastPosition;
    }
  });
};


// 交互函数 (复用教师端逻辑)
const toggleChapter = (index: number) => { chapterList.value[index].isOpen = !chapterList.value[index].isOpen; };
const handleLessonClick = (lesson: any) => {
  if (!lesson.file_url) return alert('该课时暂无文件');

  console.log('点击课时:', {
    id: lesson.id,
    title: lesson.title,
    status: lesson.status,
    last_position: lesson.last_position
  });

  currentLesson.value = lesson;
  isLearningMode.value = true;
  scale.value = 1.0;

  // 设置待恢复的滚动位置
  if (lesson.status === 1 && lesson.last_position > 0) {
    pendingRestorePosition.value = lesson.last_position;
    console.log(`设置待恢复位置: ${lesson.last_position}%`);
  } else if (lesson.status === 2) {
    pendingRestorePosition.value = 100; // 已完成，滚动到底部
  } else {
    pendingRestorePosition.value = null;
  }

  nextTick(() => {
    const el = scrollContainer.value;
    if (!el) {
      console.error('scrollContainer 不存在');
      return;
    }

    if (lesson.status === 2 && pendingRestorePosition.value === 100) {
      // 已完成，直接滚动到底部（不需要等 PDF 加载）
      el.scrollTop = el.scrollHeight;
      console.log('已完成，滚动到底部');
      pendingRestorePosition.value = null;
    }
    // 其他情况：等待 PDF 加载完成后恢复滚动位置
  });
};

const exitLearningMode = () => {
  // 停止PDF渲染监控定时器
  if (pdfRenderMonitorTimer) {
    clearInterval(pdfRenderMonitorTimer);
    pdfRenderMonitorTimer = null;
  }

  // 退出前保存当前进度
  const el = scrollContainer.value;
  console.log(`退出学习: isLearningMode=${isLearningMode.value}, currentLesson=${!!currentLesson.value}, el=${!!el}`);

  if (el && currentLesson.value && isLearningMode.value) {
    const scrollHeight = el.scrollHeight - el.clientHeight;
    const scrollPercent = scrollHeight > 0
      ? Math.round((el.scrollTop / scrollHeight) * 100)
      : 0;

    console.log(`退出前保存进度: scrollTop=${Math.round(el.scrollTop)}, scrollHeight=${el.scrollHeight}, clientHeight=${el.clientHeight}, scrollPercent=${scrollPercent}%`);

    const newStatus = scrollPercent >= 95 ? 2 : (scrollPercent > 0 ? 1 : 0);

    // 保存进度
    updateProgress({
      lesson_id: currentLesson.value.id,
      status: newStatus,
      last_position: scrollPercent >= 95 ? 100 : scrollPercent
    });

    console.log(`退出前保存: lesson_id=${currentLesson.value.id}, status=${newStatus}, last_position=${scrollPercent >= 95 ? 100 : scrollPercent}`);

    // 更新本地状态
    currentLesson.value.status = newStatus;
    updateLocalListStatus(currentLesson.value.id, newStatus, scrollPercent >= 95 ? 100 : scrollPercent);
  }

  isLearningMode.value = false;
  currentLesson.value = null;
};

// ✅ 5. 全屏切换逻辑
const toggleFullscreen = () => {
  if (!pdfContainerRef.value) return;

  if (!document.fullscreenElement) {
    pdfContainerRef.value.requestFullscreen().catch(err => {
      console.error(`全屏启用失败: ${err.message}`);
    });
    isFullscreen.value = true;
  } else {
    document.exitFullscreen();
    isFullscreen.value = false;
  }
};

// 监听全屏变化（防止用户按 Esc 退出时状态没更新）
document.addEventListener('fullscreenchange', () => {
  isFullscreen.value = !!document.fullscreenElement;
});


// --------作业相关--------
// 作业抽屉状态
const showHomeworkDrawer = ref(false);
const currentAssignment = ref<any>(null); // 当前选中的作业信息
const submissionContent = ref(''); // 学生填写的答案
const isSubmitting = ref(false);
const uploadInputRef = ref<HTMLInputElement | null>(null);

// 点击“做作业”按钮
const handleHomeworkClick = (lesson: any) => {
  // A. 前置检查：必须先学完课程
  if (lesson.status !== 2) {
    alert('请先完成本节课的学习（翻阅到最后一页）后再进行作业！');
    return;
  }
  
  // B. 打开抽屉
  currentAssignment.value = {
    ...lesson.assignment,
    lessonTitle: lesson.title,
    // 这里为了演示，我们假设题目就是标题。
    // 实际项目中，你可能需要调用 getTaskDetail 接口去获取详细的作业要求富文本
    contentRequirement: `请根据【${lesson.title}】的教学内容，完成相关实操并上传截图。` 
  };
  
  // 如果已提交过，这里应该回显（目前后端没返回具体content，暂时置空）
  submissionContent.value = ''; 
  showHomeworkDrawer.value = true;
};

// 图片上传逻辑 (插入到文本框)
const triggerUpload = () => uploadInputRef.value?.click();

const handleUpload = async (e: Event) => {
  const files = (e.target as HTMLInputElement).files;
  if (files && files[0]) {
    try {
      const res = await uploadImage(files[0], 'common');
      // 简单地把图片 Markdown 或 HTML 插入文本框
      submissionContent.value += `\n\n![截图](${res.url})`;
    } catch (error) {
      alert('上传失败');
    }
  }
};

// 提交作业
const handleSubmitHomework = async () => {
  if (!submissionContent.value) return alert('请填写作业内容或上传截图');
  
  isSubmitting.value = true;
  try {
    await submitHomework(currentAssignment.value.assignment_id, {
      content: submissionContent.value
    });
    alert('作业提交成功！');
    showHomeworkDrawer.value = false;
    
    // 刷新页面数据，更新按钮状态
    const id = route.params.id as string;
    await fetchChapters(id);
    
  } catch (error) {
    console.error(error);
  } finally {
    isSubmitting.value = false;
  }
};
// -----------------
</script>

<style scoped lang="scss">
$primary-color: #00c9a7;
$bg-color: #f5f6fa;
$text-dark: #2d3436;
$text-gray: #a4b0be;

.dashboard-container { display: flex; width: 100vw; height: 100vh; background-color: $bg-color; font-family: 'Inter', sans-serif; overflow: hidden; }
.main-content { flex: 1; padding: 30px 40px; overflow-y: auto; }

/* 顶部 */
.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
  .breadcrumb { font-size: 14px; color: $text-gray; .link { cursor: pointer; &:hover { color: $primary-color; text-decoration: underline; } } .current { color: $text-dark; font-weight: 600; margin-left: 5px; } }
  .btn-outline { background: white; border: 1px solid #ddd; padding: 6px 16px; border-radius: 6px; cursor: pointer; color: $text-dark; &:hover { border-color: $primary-color; color: $primary-color; } }
}

/* 课程概览区 */
.course-header {
  background: white; border-radius: 16px; padding: 25px; display: flex; gap: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.02); margin-bottom: 25px;
  
  .cover-box {
    width: 480px; 
    height: 270px; 
    
    flex-shrink: 0; 
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #eee;
    
    img { 
      width: 100%; 
      height: 100%; 
      object-fit: cover; 
    }
  }

  .info-box {
    flex: 1; display: flex; flex-direction: column;
    .tags { margin-bottom: 10px; display: flex; gap: 10px; 
      .tag { font-size: 12px; padding: 4px 10px; background: #f0f2f5; color: #666; border-radius: 4px; }
      .status { background: #e0f2f1; color: $primary-color; &.locked { background: #fef0f0; color: #f56c6c; } }
    }
    h1 { font-size: 26px; color: $text-dark; margin: 0 0 15px; }
    .desc {
      font-size: 14px;
      color: #606266;       /* 使用更柔和的深灰色，不刺眼 */
      line-height: 1.8;     /* 黄金行高，提升阅读舒适度 */
      margin-bottom: 20px;
      flex: 1;
      
      /* ✅ 专业排版三件套 */
      text-indent: 2em;     /* 首行缩进2个字符 */
      text-align: justify;  /* 两端对齐，让右边缘整齐 */
      letter-spacing: 0.5px;/* 微调字间距，中文更疏朗 */
      
      /* 防止文字过多溢出，限制行数 (可选，如果想全部显示就去掉这几行) */
      display: -webkit-box;
      -webkit-line-clamp: 3; /* 最多显示3行，多余显示省略号 */
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 一行4个 */
  gap: 15px;
  margin-top: auto; /* 推到底部 */
  margin-bottom: 0;
  
  .stat-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #eee;

    .icon-box {
      width: 40px; height: 40px;
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 20px;
      flex-shrink: 0;
      
      &.blue { background: #e3f2fd; color: #2196f3; }
      &.purple { background: #f3e5f5; color: #9c27b0; }
      &.orange { background: #fff3e0; color: #ff9800; }
      &.green { background: #e8f5e9; color: #4caf50; }
    }

    .stat-info {
      .label { font-size: 12px; color: #999; margin-bottom: 2px; }
      .value { 
        display: flex; align-items: baseline; gap: 2px;
        .num { font-size: 20px; font-weight: 800; color: #2d3436; }
        .unit { font-size: 12px; color: #999; }
      }
      .type-badge {
        font-size: 14px; font-weight: bold; color: $primary-color;
      }
    }
  }
}
  }
}

/* Tabs */
.course-tabs {
  background: white; border-radius: 16px; min-height: 300px; box-shadow: 0 5px 20px rgba(0,0,0,0.02);
  .tab-header {
    display: flex; border-bottom: 1px solid #eee; padding: 0 20px;
    .tab-item { padding: 15px 20px; cursor: pointer; font-weight: 500; color: #666; border-bottom: 3px solid transparent; 
      &.active { color: $primary-color; border-bottom-color: $primary-color; }
      &:hover { color: $primary-color; }
    }
  }
  .tab-content {
    padding: 30px;

    .intro-text {
      h3 {
        font-size: 18px;
        color: #303133;
        margin-bottom: 15px;
        font-weight: 700;
        
        /* 加个左侧竖线装饰，显得更像标题 */
        padding-left: 10px;
        border-left: 4px solid $primary-color;
        line-height: 1;
      }

      p {
        font-size: 15px;      /* 正文稍微大一点点 */
        color: #555;          /* 标准正文灰 */
        line-height: 2;       /* 宽松的行高，适合长阅读 */
        
        /* ✅ 专业排版优化 */
        text-indent: 2em;     /* 首行缩进 */
        text-align: justify;  /* 两端对齐 */
        letter-spacing: 1px;  /* 增加字间距 */
        margin-bottom: 15px;  /* 段落间距 */
        
        /* 保持换行符 (如果数据库里有换行的话) */
        white-space: pre-wrap; 
      }
    }
  }
}

.loading-box { text-align: center; padding: 50px; color: #999; }

/* 章节列表容器 */
.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 15px;

  .chapter-item {
    border: 1px solid #eee;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s;
    background: white;

    /* 展开时的样式 */
    &.is-open {
      border-color: $primary-color; /* 展开时边框变色 */
      box-shadow: 0 4px 12px rgba(0, 201, 167, 0.05);
      
      .chapter-header .arrow-icon {
        transform: rotate(0deg);
      }
    }

    /* 1. 章节头部 */
    .chapter-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px 20px;
      background-color: #fafafa;
      cursor: pointer;
      user-select: none;

      &:hover { background-color: #f0fdfa; }

      .left {
        display: flex; align-items: center; gap: 10px;
        .arrow-icon { font-size: 12px; color: #999; transition: transform 0.3s; transform: rotate(-90deg); }
        .title { font-size: 16px; font-weight: bold; color: #333; }
      }
      
      .right {
        .count { font-size: 12px; color: #999; }
      }
    }

    /* 2. 课时列表 */
    .lesson-group {
      border-top: 1px solid #eee;
      
      .lesson-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 20px 12px 45px; /* 左边缩进，体现层级 */
        border-bottom: 1px solid #f9f9f9;
        cursor: pointer;
        transition: background 0.2s;

        &:last-child { border-bottom: none; }
        &:hover { 
          background-color: #fff; 
          .lesson-title { color: $primary-color; }
          .btn-play { opacity: 1; transform: translateX(0); }
        }

        .lesson-left {
          display: flex; align-items: center; gap: 10px; flex: 1;
          .type-icon { font-size: 16px; }
          .lesson-title { font-size: 14px; color: #555; transition: color 0.2s; }
          .badge-free { 
            font-size: 10px; color: #00c9a7; border: 1px solid #00c9a7; 
            padding: 1px 4px; border-radius: 4px; 
          }
        }

        .lesson-right {
          display: flex; align-items: center; gap: 20px;

          .action-link {
            font-size: 13px;
            color: $primary-color; /* 使用你的青绿色 */
            cursor: pointer;
            padding: 5px 12px;
            border-radius: 4px;
            transition: all 0.2s;
            font-weight: 500;

            /* 鼠标放上去的效果 */
            &:hover {
              background-color: rgba(0, 201, 167, 0.1); /* 浅青色背景 */
              text-decoration: underline; /* 下划线 */
            }
          }
          
          /* 预览按钮：默认隐藏/淡出，悬停时出现 */
          .btn-play {
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid $primary-color;
            background: white;
            color: $primary-color;
            font-size: 12px;
            cursor: pointer;
            opacity: 0; /* 默认隐藏 */
            transform: translateX(10px);
            transition: all 0.3s;
            
            &:hover { background: $primary-color; color: white; }
          }
        }
      }
    }
  }
}

/* === 学习模式布局 === */
.learning-mode-view {
  position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
  background: #f0f2f5; /* 浅灰底色 */
  z-index: 2000; /* 覆盖原来的 Sidebar */
  display: flex;
  overflow: hidden;

  /* 1. 左侧目录 (深色半透明) */
  .learn-sidebar {
    width: 300px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(0,0,0,0.05);
    display: flex; flex-direction: column;
    box-shadow: 5px 0 15px rgba(0,0,0,0.02);
    
    .ls-header {
      padding: 20px; border-bottom: 1px solid #eee;
      .back-btn { font-size: 14px; color: #666; cursor: pointer; margin-bottom: 10px; display: flex; align-items: center; gap: 5px; &:hover { color: $primary-color; } }
      h3 { font-size: 18px; color: #333; margin: 0; }
    }
    .ls-body {
      flex: 1; overflow-y: auto; padding: 10px;
      .ls-chapter {
        margin-bottom: 15px;
        .ls-c-title { font-size: 13px; font-weight: bold; color: #999; padding: 5px 10px; }
        .ls-lessons {
          .ls-l-item {
            padding: 10px 15px; border-radius: 8px; cursor: pointer; font-size: 14px; color: #333; display: flex; gap: 8px; margin-bottom: 2px;
            &:hover { background: rgba(0,0,0,0.03); }
            &.active { background: rgba(0, 201, 167, 0.1); color: $primary-color; font-weight: 500; }
            .text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
          }
        }
      }
    }
  }

  /* 2. 右侧内容区 */
  .learn-content {
    flex: 1; display: flex; flex-direction: column;
    background: #eef1f5; /* 稍微深一点的背景，突出纸张 */
    
    /* 顶部工具栏 (毛玻璃) */
    .glass-toolbar {
      height: 60px;
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(0,0,0,0.05);
      display: flex; justify-content: space-between; align-items: center;
      padding: 0 30px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.02);
      z-index: 10;

      .file-info { 
        display: flex; align-items: center; gap: 10px; 
        .badge { background: $text-dark; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .name { font-size: 16px; font-weight: 600; color: #333; }
      }
      .tools {
        display: flex; align-items: center; gap: 15px;
        button { background: white; border: 1px solid #ddd; padding: 5px 12px; border-radius: 6px; cursor: pointer; color: #555; font-size: 13px; transition: all 0.2s;
          &:hover { border-color: $primary-color; color: $primary-color; }
          &:disabled { opacity: 0.5; cursor: not-allowed; }
        }
        .zoom-ctrl {
          display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: bold; color: #555;
          button { padding: 2px 8px; }
        }
        .btn-fullscreen { background: $primary-color; color: white; border: none; &:hover { filter: brightness(0.95); color: white; } }
      }
    }

    /* 3. 内容舞台 (PDF 容器) */
    .content-stage {
      flex: 1; 
      overflow: auto; /* ✅ 关键：允许上下左右滚动 */
      padding: 40px;
      display: flex; 
      justify-content: center; /* 默认居中 */
      background: #f0f2f3;
      
      .pdf-paper-wrapper { 
        background: white; /* 不需要背景色了，PDF组件自带白底 */
        box-shadow: none;        /* 组件自带阴影更好 */
        transition: transform 0.2s ease; /* 缩放动画 */
        flex-shrink: 0;
        display: inline-block;
      }
      
      /* 修改组件样式，让每一页之间有间距 */
      .pdf-canvas {
        display: block;
        /* vue-pdf-embed 渲染出来的是多个 canvas/div */
        :deep(.vue-pdf-embed__page) {
          margin-bottom: 20px; /* 页间距 */
          box-shadow: 0 4px 15px rgba(0,0,0,0.3); /* 每一页的阴影 */
        }
      }
    }
  }
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* --- 课件资料列表样式 --- */
.materials-list {
  display: flex; flex-direction: column; gap: 10px;

  .material-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 15px 20px;
    border: 1px solid #eee; border-radius: 12px; background: #fff;
    transition: all 0.2s;

    &:hover { border-color: $primary-color; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }

    .left {
      display: flex; align-items: center; gap: 15px;
      .icon-box {
        width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 20px;
        &.ppt { background-color: #ff6b6b; } /* 红色代表PPT */
        &.pdf { background-color: #ff9f43; }
      }
      .info {
        .name { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 4px; }
        .chapter-tag { font-size: 12px; color: #999; background: #f5f5f5; padding: 2px 6px; border-radius: 4px; display: inline-block; }
      }
    }

    .right {
      display: flex; align-items: center; gap: 15px;
      .btn-play {
        background: $primary-color; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;
        &:hover { filter: brightness(0.9); transform: translateY(-1px); }
      }
      .btn-download {
        color: #999; text-decoration: none; font-size: 13px;
        &:hover { color: $text-dark; text-decoration: underline; }
      }
    }
  }
}

/* --- 课程视频样式 --- */
.videos-container {
  .video-layout {
    display: flex;
    gap: 20px;
    min-height: 500px;
  }

  /* 左侧视频播放器 */
  .video-player-section {
    flex: 1;
    min-width: 0;

    .video-wrapper {
      background: #000;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);

      .video-element {
        width: 100%;
        aspect-ratio: 16/9;
        display: block;
        background: #000;
      }

      .video-controls {
        background: #1a1a1a;
        padding: 12px 16px;
        border-top: 1px solid #333;

        .speed-control {
          display: flex;
          align-items: center;
          gap: 12px;

          .speed-label {
            color: #999;
            font-size: 13px;
          }

          .speed-buttons {
            display: flex;
            gap: 6px;

            .speed-btn {
              padding: 4px 10px;
              background: #333;
              color: #ccc;
              border: 1px solid #444;
              border-radius: 4px;
              font-size: 12px;
              cursor: pointer;
              transition: all 0.2s;

              &:hover {
                background: #444;
                color: #fff;
              }

              &.active {
                background: $primary-color;
                color: #fff;
                border-color: $primary-color;
              }
            }
          }
        }
      }
    }

    .video-placeholder {
      aspect-ratio: 16/9;
      background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;

      .placeholder-icon {
        width: 80px;
        height: 80px;
        background: rgba(0, 201, 167, 0.1);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        color: $primary-color;
      }

      p {
        color: #666;
        font-size: 14px;
        margin: 0;
      }
    }
  }

  /* 右侧视频列表 */
  .video-list-section {
    width: 320px;
    flex-shrink: 0;

    .video-list-content {
      background: #fff;
      border-radius: 12px;
      border: 1px solid #eee;
      max-height: 500px;
      overflow-y: auto;

      &::-webkit-scrollbar {
        width: 6px;
      }
      &::-webkit-scrollbar-track {
        background: #f5f5f5;
        border-radius: 3px;
      }
      &::-webkit-scrollbar-thumb {
        background: #ddd;
        border-radius: 3px;
        &:hover {
          background: #ccc;
        }
      }

      .video-chapter {
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }

        .video-chapter-title {
          padding: 12px 16px;
          background: #f8f9fa;
          font-size: 13px;
          font-weight: 600;
          color: #666;
          position: sticky;
          top: 0;
        }

        .video-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          cursor: pointer;
          transition: all 0.2s;
          border-bottom: 1px solid #f5f5f5;

          &:last-child {
            border-bottom: none;
          }

          &:hover {
            background: #f8f9fa;

            .video-title {
              color: $primary-color;
            }
          }

          &.active {
            background: rgba(0, 201, 167, 0.08);
            border-left: 3px solid $primary-color;
            padding-left: 13px;

            .video-title {
              color: $primary-color;
              font-weight: 500;
            }
          }

          .video-item-left {
            display: flex;
            align-items: center;
            gap: 10px;
            flex: 1;
            min-width: 0;

            .video-icon {
              color: #999;
              font-size: 12px;
              flex-shrink: 0;
            }

            .video-title {
              font-size: 14px;
              color: #333;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
              transition: color 0.2s;
            }
          }

          .video-item-right {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;

            .video-duration {
              font-size: 12px;
              color: #999;
            }

            .playing-indicator {
              font-size: 11px;
              color: $primary-color;
              background: rgba(0, 201, 167, 0.1);
              padding: 2px 6px;
              border-radius: 4px;
            }
          }
        }
      }

      .empty-state {
        padding: 40px 20px;
        text-align: center;
        color: #999;
        font-size: 14px;
      }
    }
  }
}

/* 响应式：小屏幕时上下排列 */
@media (max-width: 1024px) {
  .videos-container .video-layout {
    flex-direction: column;
  }

  .video-list-section {
    width: 100% !important;
  }
}

/* === PPT 放映厅样式 (升级版) === */
.ppt-player {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: #f5f7fa; 
  color: #333;
  z-index: 3000;
  display: flex;
  flex-direction: column;
  user-select: none;

  /* 顶部栏：默认浮在上面，背景半透明 */
  .ppt-header {
    position: absolute; top: 0; left: 0; width: 100%; height: 60px;
    display: flex; justify-content: space-between; align-items: center; padding: 0 20px;
    background: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent); /* 渐变阴影 */
    color: #fff; z-index: 20;
    transition: opacity 0.3s;
    opacity: 0; /* 默认隐藏，鼠标动了才显示 */
    
    .title { font-size: 16px; font-weight: bold; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }
    .btn-icon { background: none; border: none; color: white; font-size: 24px; cursor: pointer; opacity: 0.8; &:hover { opacity: 1; } }
  }

  .ppt-body {
    flex: 1; 
    display: flex;
    overflow: hidden; /* 防止溢出 */
    position: relative;
    /* 去掉之前的 padding，因为现在 header/footer 不再悬浮遮挡了 */
    padding-top: 0; 
    padding-bottom: 0;
  }

  /* ✅ 新增：左侧缩略图栏 */
  .ppt-sidebar {
    width: 260px;
    background: #fff; /* 白底 */
    border-right: 1px solid #e0e0e0;
    overflow-y: auto;
    display: flex; flex-direction: column; padding: 15px; gap: 15px; flex-shrink: 0;

    .thumb-item {
      display: flex; align-items: flex-start; gap: 10px; cursor: pointer; opacity: 0.8; transition: opacity 0.2s;
      &:hover { opacity: 1; }
      
      &.active {
        opacity: 1;
        .thumb-preview { border-color: $primary-color; box-shadow: 0 0 0 3px rgba(0, 201, 167, 0.2); }
        .thumb-index { color: $primary-color; font-weight: bold; }
      }

      .thumb-index { font-size: 12px; color: #999; margin-top: 2px; width: 18px; }
      .thumb-preview {
        border: 1px solid #eee; /* 给缩略图加个边框 */
        border-radius: 4px; overflow: hidden; background: #eee;
        width: 100%; height: auto; pointer-events: none;
      }
    }
  }

  /* 底部栏：默认浮在下面 */
  .ppt-footer {
    position: absolute; bottom: 0; left: 0; width: 100%; height: 70px;
    background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); /* 渐变阴影 */
    display: flex; justify-content: space-between; align-items: center; padding: 0 40px;
    color: #ccc; z-index: 20;
    transition: opacity 0.3s;
    opacity: 0; /* 默认隐藏 */

    .page-nav {
      display: flex; align-items: center; gap: 30px; margin: 0 auto; transform: translateX(80px);
      .nav-btn { font-size: 16px; padding: 8px 20px; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.2); color: white; border-radius: 30px; backdrop-filter: blur(4px); &:hover { background: $primary-color; border-color: $primary-color; } &:disabled { opacity: 0.3; cursor: not-allowed; background: transparent; } }
      .page-num { font-size: 16px; color: rgba(255,255,255,0.8); b { color: white; font-size: 20px; } }
    }
    .fullscreen-tool .btn-fs { background: transparent; border: 1px solid rgba(255,255,255,0.3); color: white; padding: 6px 12px; border-radius: 4px; &:hover { background: white; color: black; } }
    .zoom-tools { visibility: hidden; } /* 演示模式隐藏缩放，因为是自适应的 */
  }

  /* 鼠标悬停在整个屏幕时，显示上下栏 */
  &:hover {
    .ppt-header, .ppt-footer { opacity: 1; }
  }

  /* === 🌟 核心舞台：全屏自适应 === */
  .ppt-stage {
    flex: 1;
    /* ✅ 改动 2: 背景改为浅灰，突出中间的 PPT */
    background: #e3e5e7; 
    
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    position: relative;
    padding: 20px; /* 给四周留点呼吸空间 */

    /* PDF 画布样式 */
    :deep(.ppt-slide) {
      /* ✅ 改动 3: 强制适应容器大小 (Contain) */
      max-width: 100% !important;
      max-height: 100% !important;
      width: auto !important;
      height: auto !important;
      
      object-fit: contain; 
      box-shadow: 0 4px 20px rgba(0,0,0,0.15); /* 柔和阴影 */
      background-color: white;
    }
  }

  &.is-fullscreen .ppt-stage {
    padding: 0; /* 全屏时去掉内边距，尽可能大 */
    background: white;
    
    :deep(.ppt-slide) {
      max-width: 100vw;
      max-height: 100vh;
    }
  }
}

/* 状态按钮通用样式 */
.status-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  padding: 6px 16px;
  border-radius: 20px; /* 胶囊形状 */
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  border: 1px solid transparent; /* 预留边框 */
  
  .icon { font-size: 14px; }

  /* 1. 开始学习 (描边风格) */
  &.start {
    background-color: transparent;
    border-color: #e0e0e0;
    color: #606266;
    
    &:hover {
      border-color: $primary-color;
      color: $primary-color;
      background-color: rgba(0, 201, 167, 0.05);
      transform: translateY(-1px);
    }
  }

  /* 2. 继续学习 (暖色调，醒目) */
  &.learning {
    background-color: #fff7e6; /* 浅橙色背景 */
    color: #fa8c16;            /* 深橙色文字 */
    border-color: #ffd591;
    
    &:hover {
      background-color: #fa8c16;
      color: white;
      border-color: #fa8c16;
      box-shadow: 0 4px 10px rgba(250, 140, 22, 0.3);
      transform: translateY(-1px);
    }
  }

  /* 3. 已完成 (清爽绿，像勋章一样) */
  &.finished {
    background-color: #e6fffb; /* 极浅的青绿色背景 */
    color: $primary-color;     /* 品牌主色文字 */
    border-color: transparent; /* 无边框，像标签 */
    
    &:hover {
      background-color: $primary-color;
      color: white;
      box-shadow: 0 4px 10px rgba(0, 201, 167, 0.3);
      transform: translateY(-1px);
      /* 鼠标放上去时，可以把文字变成“去复习” (可选高级效果，这里保持简单) */
    }
  }
}

/* 作业按钮样式 */
.homework-tag {
  font-size: 12px; padding: 2px 8px; border-radius: 4px; margin-right: 10px;
  &.score { color: #52c41a; background: #f6ffed; border: 1px solid #b7eb8f; font-weight: bold; }
  &.submitted { color: #1890ff; background: #e6f7ff; border: 1px solid #91d5ff; }
  &.locked { color: #999; background: #f5f5f5; border: 1px solid #ddd; cursor: not-allowed; }
}

.btn-homework {
  background: #fff7e6; border: 1px solid #ffd591; color: #fa8c16;
  padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-right: 10px;
  &:hover { background: #fa8c16; color: white; }
}

/* 抽屉样式 */
.homework-body {
  padding: 10px;
  .hw-header { border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 15px;
    h3 { margin: 0 0 5px; color: $text-dark; }
    .hw-meta { font-size: 12px; color: #999; }
  }
  .hw-requirement { background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; color: #555; font-size: 14px; }
  
  .hw-answer-area {
    textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; resize: vertical; outline: none; font-family: inherit; &:focus { border-color: $primary-color; } }
    .toolbar { margin-top: 10px; }
    .btn-icon { background: white; border: 1px solid #ddd; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; &:hover { color: $primary-color; border-color: $primary-color; } }
  }
  
  .hw-footer { margin-top: 30px; button { width: 100%; padding: 12px; background: $primary-color; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; &:disabled { opacity: 0.6; } } }
}
</style>