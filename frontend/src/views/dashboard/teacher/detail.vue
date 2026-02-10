<template>
  <div class="dashboard-container">
    <TeacherSidebar />

    <main class="main-content">
      <div v-if="!isLearningMode" class="detail-view animate__fadeIn">
      <header class="top-bar">
        <div class="breadcrumb">
          <span>教学管理</span> / 
          <span class="link" @click="router.push('/dashboard/teacher/courses')">课程资源库</span> / 
          <span class="current">课程详情</span>
        </div>
        <button class="btn-outline" @click="router.back()">← 返回列表</button>
      </header>

      <div v-if="loading" class="loading-box">加载中...</div>
      <div v-else class="detail-container">
        <!-- 预览模式横幅 -->
        <div v-if="courseInfo.is_locked" class="preview-banner">
          <span class="banner-text">您正在预览模式中查看此课程，开通后可解锁全部内容</span>
        </div>

        <div class="course-header">
          <div class="cover-box">
            <img :src="getImgUrl(courseInfo.cover) || defaultCover" alt="cover" />
          </div>

          <div class="info-box">
            <div class="tags">
              <span class="tag">系统课程</span>
              <span class="tag status" :class="{ locked: courseInfo.is_locked, preview: courseInfo.is_locked }">
                {{ courseInfo.is_locked ? '预览模式' : '✅ 已授权' }}
              </span>
            </div>

            <h1>{{ courseInfo.name }}</h1>

            <p class="desc">{{ courseInfo.intro || '该课程暂无详细介绍...' }}</p>
            
            <div class="stats-grid">
              
              <!-- 1. 任务数量 -->
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

              <!-- 2. 总时长 -->
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

              <!-- 3. 课时数 -->
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

              <!-- 4. 课程类型 -->
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

        <!-- 3. 内容 Tabs (预留位置) -->
        <div v-if="isLearningMode" class="learning-container">
          <!-- 左侧：迷你目录 (复用之前的列表逻辑，稍微简化) -->
          <div class="mini-sidebar">
            <div class="sidebar-header">
              <span>课程目录</span>
              <button class="btn-exit" @click="exitLearningMode">退出学习 ✕</button>
            </div>
            <div class="sidebar-body">
              <div v-for="(chapter, cIndex) in chapterList" :key="chapter.id" class="mini-chapter">
                <div class="c-title" @click="toggleChapter(cIndex)">
                  {{ chapter.title }}
                </div>
                <div v-show="chapter.isOpen" class="c-lessons">
                  <div 
                    v-for="lesson in chapter.lessons" 
                    :key="lesson.id" 
                    class="l-item"
                    :class="{ active: currentLesson?.id === lesson.id }"
                    @click="handleLessonClick(lesson)"
                  >
                    <span class="icon">{{ lesson.type === 'video' ? '📺' : '📄' }}</span>
                    <span class="text">{{ lesson.title }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="course-tabs">
          <div class="tab-header">
            <span 
              class="tab-item" 
              :class="{ active: activeTab === 'intro' }" 
              @click="activeTab = 'intro'"
            >
              课程介绍
            </span>
            <span 
              class="tab-item" 
              :class="{ active: activeTab === 'chapters' }" 
              @click="activeTab = 'chapters'"
            >
              章节目录
            </span>
            <span
              class="tab-item"
              :class="{ active: activeTab === 'materials' }"
              @click="activeTab = 'materials'"
            >
              课件资料
            </span>
            <span
              class="tab-item"
              :class="{ active: activeTab === 'videos' }"
              @click="activeTab = 'videos'"
            >
              课程视频
            </span>
          </div>
          
          <div class="tab-content">
            <!-- 暂时显示简介 -->
            <div v-if="activeTab === 'intro'" class="intro-text">
              <h3>关于本课程</h3>
              <p>{{ courseInfo.intro || '暂无详细介绍' }}</p>
            </div>

            <!-- 内容块 2: 章节目录 (复用之前的漂亮样式) -->
            <div v-if="activeTab === 'chapters'" class="chapter-list">
              <div v-for="(chapter, index) in pdfChapterList" :key="chapter.id" class="chapter-item" :class="{ 'is-open': chapter.isOpen }">
                <!-- 一级标题 -->
                <div class="chapter-header" @click="toggleChapter(index)">
                  <div class="left">
                    <span class="arrow-icon">▼</span>
                    <span class="title">{{ chapter.title }}</span>
                  </div>
                  <div class="right">
                    <span class="count">{{ chapter.lessons.length }} 个课时</span>
                  </div>
                </div>

                <!-- 二级列表 -->
                <div class="lesson-group" v-show="chapter.isOpen">
                  <div
                    v-for="lesson in chapter.lessons"
                    :key="lesson.id"
                    class="lesson-item"
                    :class="{ 'preview-locked': courseInfo.is_locked && lesson.is_previewable === false }"
                    @click="handleLessonClick(lesson)"
                  >
                    <div class="lesson-left">
                      <span class="type-icon ppt" v-if="lesson.type === 'ppt'">📑</span>
                      <span class="type-icon video" v-else-if="lesson.type === 'video'">▶️</span>
                      <span class="lesson-title">{{ lesson.title }}</span>
                      <span v-if="lesson.is_free" class="badge-free">试读</span>
                    </div>
                    <div class="lesson-right">
                      <span
                        v-if="lesson.task && !courseInfo.is_locked"
                        class="action-btn task-btn"
                        @click.stop="handleTaskClick(lesson.task)"
                      >
                        作业预览
                      </span>
                      <span v-if="!courseInfo.is_locked || lesson.is_previewable" class="action-link" @click.stop="handleLessonClick(lesson)">
                        {{ lesson.type === 'video' ? '播放视频' : '查看详情' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 预览模式提示 -->
              <div v-if="courseInfo.is_locked" class="preview-tip">
                <span class="tip-text">预览模式下可查看第1章的详细内容，其他章节开通后解锁</span>
              </div>
            </div>

            <!-- 内容块 3: 课件资料 -->
            <div v-if="activeTab === 'materials'" class="materials-list">

              <div v-if="materialList.length === 0" class="empty-state">
                暂无课件资料
              </div>

              <div class="material-item" v-for="item in materialList" :key="item.id" :class="{ 'preview-locked': courseInfo.is_locked && item.is_previewable === false }">
                <div class="left">
                  <!-- 图标 -->
                  <div class="icon-box ppt" v-if="item.type === 'ppt'">P</div>
                  <div class="icon-box pdf" v-else>F</div>

                  <div class="info">
                    <div class="name">{{ item.title }}</div>
                    <div class="chapter-tag">{{ item.chapterTitle }}</div>
                  </div>
                </div>

                <div class="right">
                  <button v-if="!courseInfo.is_locked || item.is_previewable" class="btn-play" @click="handlePlayPPT(item.file_url, item.title)">
                    ▶ 幻灯片演示
                  </button>
                </div>
              </div>

              <!-- 预览模式提示 -->
              <div v-if="courseInfo.is_locked && materialList.length > 0" class="preview-tip-inline">
                <span class="tip-text">预览模式下第1章的课件可查看，其他课件开通后解锁</span>
              </div>
            </div>

            <!-- 内容块 4: 课程视频 -->
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
                        :class="['video-item', { active: currentVideo?.id === video.id, 'preview-locked': courseInfo.is_locked && video.is_previewable === false }]"
                        @click="(!courseInfo.is_locked || video.is_previewable) && playVideo(video)"
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
                    <!-- 预览模式提示 -->
                    <div v-if="courseInfo.is_locked && videoChapterList.length > 0" class="preview-tip-inline">
                      <span class="tip-text">预览模式下第1章的视频可播放，其他视频开通后解锁</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
      </div>

      <!-- ================= 模式 B: 沉浸式学习模式 (全屏覆盖) ================= -->
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
          <div class="content-stage">
            <div class="pdf-paper-wrapper">
              <VuePdfEmbed 
                v-if="currentLesson?.type === 'pdf'"
                :source="getImgUrl(currentLesson.file_url)" 
                :page="pdfPage"
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

      <!-- ================= PPT 沉浸式放映厅 ================= -->
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

      <el-drawer
        v-model="showTaskDrawer"
        title="作业详情"
        direction="rtl"
        size="500px"
        class="task-drawer"
      >
        <template #header>
          <div class="task-drawer-header">
            <span class="icon">📝</span>
            <h3>{{ currentTask?.title }}</h3>
          </div>
        </template>

        <div class="task-drawer-body" v-loading="isDrawerLoading">
          <!-- A. 题目预览区 -->
          <div class="task-preview-box">
            <h4>作业要求</h4>
            <div class="content-text" v-html="currentTask?.content || '暂无详细描述'"></div>
          </div>

          <div class="divider-line"></div>

          <!-- B. 分班发布设置区 (核心) -->
          <div class="publish-section">
            <h4>📅 发布设置 (设置截止时间即视为发布)</h4>
            
            <div v-if="publishList.length === 0" class="empty-hint">
              暂无关联班级，请先去新建班级并绑定此课程。
            </div>

            <div class="class-publish-list">
              <div class="cp-item" v-for="item in publishList" :key="item.class_id">
                
                <!-- 班级信息 -->
                <div class="cp-info">
                  <div class="cp-name">{{ item.class_name }}</div>
                  <div class="cp-status">
                    <span v-if="item.is_published" class="tag success">● 已发布</span>
                    <span v-else class="tag gray">○ 未发布</span>
                  </div>
                </div>

                <!-- 日期选择器 -->
                <div class="cp-date">
                  <v-date-picker 
                    v-model="item.deadline" 
                    mode="dateTime" 
                    is24hr 
                    :model-config="dateConfig" 
                    color="teal"
                    :popover="{ visibility: 'click', placement: 'bottom-end', keepVisibleOnInput: true }"
                  >
                    <template #default="{ inputValue, inputEvents }">
                      <div class="input-mini">
                        <!-- 图标放 input 前面或者后面都可以，CSS里用 position: absolute 定位了 -->
                        <span class="icon">📅</span>
                        <input :value="inputValue" v-on="inputEvents" placeholder="点击设置截止时间" readonly />
                      </div>
                    </template>
                  </v-date-picker>
                </div>

              </div>
            </div>
          </div>

          <!-- 底部按钮 -->
          <div class="task-footer">
            <button class="btn-primary" @click="handleSavePublish" :disabled="isPublishLoading">
              {{ isPublishLoading ? '保存中...' : '保存并发布' }}
            </button>
          </div>
        </div>



      </el-drawer>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import TeacherSidebar from '@/components/TeacherSidebar.vue';
import { getCourseDetail, getCourseChapters, getCourseTasks, getTaskPublishStatus, publishTaskToClasses, type CourseItem, type CourseChapterItem, type CourseTaskItem, type ClassTaskStatus } from '@/api/content';
import { getImgUrl } from '@/utils/index';
import VuePdfEmbed from 'vue-pdf-embed';

const activeTab = ref('intro'); 
const route = useRoute();
const router = useRouter();

const loading = ref(true);
const courseInfo = ref<Partial<CourseItem>>({});
const defaultCover = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop';
const chapterList = ref<CourseChapterItem[]>([]);

// 定义抽屉状态
const showTaskDrawer = ref(false);
const currentTask = ref<any>(null); // 当前选中的作业内容
const publishList = ref<ClassTaskStatus[]>([]); // 班级发布列表
const isPublishLoading = ref(false);            // 保存按钮 Loading
const isDrawerLoading = ref(false);             // 抽屉内容 Loading
const dateConfig = { type: 'string', mask: 'YYYY-MM-DD HH:mm' };

// ✅ 点击“做作业/查看作业”按钮
const handleTaskClick = async (task: any) => {
  currentTask.value = task;
  showTaskDrawer.value = true;
  isDrawerLoading.value = true; // 开始转圈
  
  try {
    // 拉取该作业在各班级的发布情况
    const res = await getTaskPublishStatus(task.id);
    publishList.value = res;
  } catch (error) {
    console.error(error);
  } finally {
    isDrawerLoading.value = false;
  }
};

// 4. 新增：保存发布设置
const handleSavePublish = async () => {
  if (!currentTask.value) return;
  
  isPublishLoading.value = true;
  try {
    // 构造提交数据
    const configs = publishList.value.map(item => ({
      class_id: item.class_id,
      // 如果选了时间，转成 ISO 格式传给后端；没选传 undefined
      deadline: item.deadline ? new Date(item.deadline).toISOString() : undefined
    }));

    await publishTaskToClasses(currentTask.value.id, configs);
    
    alert('发布设置已保存！');
    showTaskDrawer.value = false;
  } catch (error) {
    console.error(error);
    alert('保存失败');
  } finally {
    isPublishLoading.value = false;
  }
};

// 新增pdf状态变量
const isLearningMode = ref(false); // 是否进入学习模式
const currentLesson = ref<any>(null); // 当前正在看的课时
const pdfPageCount = ref(0); // 总页码
const isFullscreen = ref(false); // 全屏状态
const pdfContainerRef = ref<HTMLElement | null>(null); // 用于全屏的 DOM 引用
const scale = ref(1.0);

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
    // 全屏模式：使用屏幕真实宽度，保证高清且填满
    return window.innerWidth;
  }
  // 非全屏模式：使用你指定的固定宽度
  return 1500;
});

// ✅ 新增：动态计算 PPT 宽度
import { useWindowSize } from '@vueuse/core'; 
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
// ✅ 新增：监听页码变化，自动滚动侧边栏
watch(pptCurrentPage, (newPage) => {
  // 使用 nextTick 确保 DOM 已经更新（高亮样式已生效）
  nextTick(() => {
    // 1. 找到当前页对应的缩略图元素
    const targetElement = document.getElementById(`thumb-item-${newPage}`);
    
    // 2. 如果元素存在，并且侧边栏是显示状态
    if (targetElement && !isFullscreen.value) {
      // 3. 调用原生 API 让它滚动到可视区域
      // block: 'center' 表示尽量把它滚到中间，体验最好
      targetElement.scrollIntoView({
        behavior: 'smooth', // 平滑滚动
        block: 'center',    // 垂直方向居中
        inline: 'nearest'
      });
    }
  });
});

const materialList = computed(() => {
  const list: any[] = [];
  chapterList.value.forEach(chapter => {
    chapter.lessons.forEach(lesson => {
      // 过滤条件：类型是 PPT
      if (lesson.type === 'ppt') {
        list.push({
          ...lesson,
          chapterTitle: chapter.title // 把章节名带上，方便列表显示
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
  pptCurrentPage.value = 1; // 重置到第一页
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

// ✅ 3. 修改点击课时的逻辑
const handleLessonClick = (lesson: any) => {
  // 预览模式下，检查是否可预览
  if (courseInfo.value.is_locked && lesson.is_previewable === false) {
    alert('预览模式下无法查看此内容，开通后可解锁全部章节');
    return;
  }

  if (!lesson.file_url) return alert('该课时暂无文件');

  currentLesson.value = lesson;
  isLearningMode.value = true;
  pdfPage.value = 1;
  scale.value = 1.0; // 重置缩放
};

// ✅ 4. 退出学习模式
const exitLearningMode = () => {
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

// PDF 加载完成回调
const handlePdfLoaded = (doc: any) => {
  pdfPageCount.value = doc.numPages;
};


// 1. 定义任务列表状态
const taskList = ref<CourseTaskItem[]>([]);

// 2. 新增获取任务的函数
const fetchTasks = async (id: string) => {
  try {
    const res = await getCourseTasks(id);
    taskList.value = res;
  } catch (error) {
    console.error("加载任务失败", error);
  }
};

onMounted(async () => {
  const id = route.params.id as string;
  
  if (id) {
    await fetchDetail(id);
    await fetchChapters(id);
    await fetchTasks(id);
  }
});

const fetchDetail = async (id: string) => {
  try {
    loading.value = true;
    const res = await getCourseDetail(id);
    courseInfo.value = res;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// ✅ 新增：加载章节函数
const fetchChapters = async (id: string) => {
  try {
    const res = await getCourseChapters(id);
    // 默认展开第一个章节
    if (res.length > 0) res[0].isOpen = true;
    chapterList.value = res;
  } catch (error) {
    console.error("加载章节失败", error);
  }
};

// 4. 辅助函数：去除 HTML 标签（用于列表预览）
const stripHtml = (html: string) => {
  if (!html) return '';
  const tmp = document.createElement('DIV');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
};

// Toggle 函数稍微改一下 (因为现在是 ref 数组，不是 reactive 对象直接修改)
const toggleChapter = (index: number) => {
  chapterList.value[index].isOpen = !chapterList.value[index].isOpen;
};

const formatDate = (isoStr?: string) => {
  if (!isoStr) return '';
  return new Date(isoStr).toLocaleDateString();
};
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

/* 预览模式横幅 */
.preview-banner {
  background: white;
  border: 1px solid #1565c0;
  border-radius: 12px;
  padding: 15px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(21, 101, 192, 0.1);

  .banner-text {
    font-size: 14px;
    color: #1565c0;
    font-weight: 500;
  }
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
      .status.preview { background: white; color: #1565c0; border: 1px solid #1565c0; }
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

        /* 预览模式禁用状态 */
        &.preview-locked {
          cursor: not-allowed;
          opacity: 0.7;
          &:hover { background-color: #fafafa; }
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

  /* 预览模式提示 */
  .preview-tip {
    background: white;
    border: 1px solid #1565c0;
    border-radius: 12px;
    padding: 15px 20px;
    margin-top: 10px;

    .tip-text { font-size: 13px; color: #1565c0; }
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

    /* 预览模式禁用状态 */
    &.preview-locked {
      opacity: 0.7;
      cursor: not-allowed;
      &:hover { border-color: #eee; box-shadow: none; }
    }

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

  /* 预览模式内联提示 */
  .preview-tip-inline {
    background: white;
    border: 1px solid #1565c0;
    border-radius: 8px;
    padding: 10px 15px;
    margin-top: 5px;

    .tip-text { font-size: 12px; color: #1565c0; }
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

          /* 预览模式禁用状态 */
          &.preview-locked {
            cursor: not-allowed;
            opacity: 0.7;
            &:hover { background: transparent; }
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

/* 作业按钮样式 */
.task-btn {
  font-size: 12px;
  color: #119fe0; /* 橙色，区分于课件的青色 */
  background: #f8f8f8;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px; /* 和课件按钮拉开距离 */
  font-weight: 600;
  transition: all 0.2s;

  &:hover {
    background: #418add;
    color: white;
  }
}

/* 抽屉样式微调 */
.task-drawer-header {
  display: flex; align-items: center; gap: 12px;
  /* 图标背景 */
  .icon { 
    font-size: 20px; 
    background: #e0f2f1; /* 浅青色背景 */
    color: $primary-color; 
    width: 36px; height: 36px; 
    display: flex; align-items: center; justify-content: center; 
    border-radius: 10px; 
  }
  h3 { margin: 0; font-size: 18px; color: $text-dark; font-weight: 700; }
}

.task-preview-box {
  padding: 0 5px;
  h4 { margin: 0 0 12px; color: #333; font-size: 15px; font-weight: 600; }
  /* 作业要求内容框 */
  .content-text { 
    font-size: 14px; color: #555; line-height: 1.8; 
    background: #f8f9fa; /* 极浅灰 */
    padding: 20px; 
    border-radius: 12px; 
    border: 1px solid #eee;
  }
}

.divider-line { height: 1px; background: #f0f0f0; margin: 25px 0; }

.publish-section {
  padding: 0 5px;
  h4 { 
    margin: 0 0 15px; color: $text-dark; font-size: 15px; font-weight: 600; 
    display: flex; align-items: center; gap: 8px;
    &::before { content: ''; display: block; width: 4px; height: 16px; background: $primary-color; border-radius: 2px; }
  }
  
  .class-publish-list {
    display: flex; flex-direction: column; gap: 12px;
    
    /* 班级列表项卡片 */
    .cp-item {
      display: flex; align-items: center; justify-content: space-between;
      padding: 16px; 
      border: 1px solid #f0f0f0; /* 极细边框 */
      border-radius: 12px; 
      background: white;
      transition: all 0.2s ease;
      
      /* 悬停效果 */
      &:hover {
        border-color: $primary-color;
        background-color: #f0fdfa; /* 悬停变淡青色 */
        box-shadow: 0 4px 12px rgba(0, 201, 167, 0.08);
      }
      
      .cp-info {
        .cp-name { font-weight: 600; font-size: 14px; margin-bottom: 6px; color: $text-dark; }
        .cp-status {
          .tag { font-size: 12px; display: inline-flex; align-items: center; gap: 4px; font-weight: 500;}
          .tag.success { color: $primary-color; }
          .tag.gray { color: #ccc; }
        }
      }
      
      /* 日期选择器容器 */
      .cp-date {
        width: 200px;
        .input-mini {
          position: relative;
          input { 
            width: 100%; 
            padding: 8px 12px 8px 30px; /* 左边留空给图标 */
            font-size: 13px; 
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            outline: none; 
            cursor: pointer;
            color: #555;
            background: #fff;
            transition: border-color 0.2s;
            
            &:hover { border-color: #bbb; }
            &:focus { border-color: $primary-color; box-shadow: 0 0 0 3px rgba(0,201,167,0.1); }
          }
          /* 图标放到左边，更符合直觉 */
          .icon { 
            position: absolute; left: 10px; top: 50%; 
            transform: translateY(-50%); font-size: 14px; color: $primary-color; 
          }
        }
      }
    }
  }
}

.task-footer {
  margin-top: 30px; 
  padding-top: 20px;
  border-top: 1px solid #f5f5f5;
  text-align: right;
  
  .btn-primary { 
    width: 100%; 
    justify-content: center; 
    padding: 14px; /* 加大点击区域 */
    border-radius: 12px; 
    border: none; 
    background: $primary-color; /* 实心青绿色 */
    color: white; 
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 6px 15px rgba(0, 201, 167, 0.3); /* 漂亮的投影 */
    transition: all 0.2s;

    &:hover { 
      filter: brightness(0.95); 
      transform: translateY(-2px); 
      box-shadow: 0 8px 20px rgba(0, 201, 167, 0.4);
    }
    
    &:active { transform: translateY(0); }
    &:disabled { background: #ccc; box-shadow: none; cursor: not-allowed; }
  }
}
</style>