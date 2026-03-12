<template>
  <div class="dashboard-container">
    <!-- 顶部导航 -->
    <header class="grading-header">
      <div class="left">
        <button class="back-btn" @click="router.back()">← 返回列表</button>
        <h3>{{ gradingData.assignment_title }}</h3>
      </div>
      <div class="right">
        <span class="stat">已批改: {{ gradedCount }} / {{ gradingData.students?.length }}</span>
      </div>
    </header>

    <div class="grading-body" v-if="gradingData.students">
      
      <!-- 1. 左侧：学生列表 -->
      <div class="student-list">
        <div 
          v-for="stu in sortedStudents" 
          :key="stu.student_id" 
          class="stu-item"
          :class="{ active: currentStudent?.student_id === stu.student_id }"
          @click="currentStudent = stu"
        >
          <div class="avatar">
            <img :src="getImgUrl(stu.avatar) || defaultAvatar" />
            <div class="status-dot" :class="getStatusClass(stu.status)"></div>
          </div>
          <div class="info">
            <div class="name">{{ stu.student_name }}</div>
            <div class="status-text">{{ getStatusText(stu.status) }}</div>
          </div>
          <div class="score" v-if="stu.score">{{ stu.score }}分</div>
        </div>
      </div>

      <!-- 2. 右侧：批改区 -->
      <div class="grading-area">
        
        <!-- 空状态 -->
        <div v-if="!currentStudent" class="empty-grading">
          请在左侧选择一名学生开始批改
        </div>

        <!-- 批改面板 -->
        <div v-else class="grading-panel">
          
          <!-- ✅ 区域 A (左侧 65%)：作业内容展示区 -->
          <div class="panel-left">
            <div class="content-header">
              <!-- 左侧：学生信息 -->
              <div class="student-info">
                <span class="name">{{ currentStudent.student_name }}</span>
                <span class="divider">|</span>
                <span class="code">{{ currentStudent.student_number || '无学号' }}</span>
              </div>
              
              <!-- 右侧：提交时间 -->
              <span class="time">
                提交时间： {{ formatDate(currentStudent.submitted_at) }}
              </span>
            </div>
            
            <!-- 未提交状态 -->
            <div v-if="currentStudent.status === 0" class="not-submitted">
              <div class="empty-icon">📭</div>
              <p>该学生暂未提交作业</p>
            </div>
            
            <div v-else class="content-wrapper">
              <div 
                  class="rich-content" 
                  ref="contentRef"
                  @mouseup="handleTextSelect"
                  @click="handleContentClick"
                  v-html="formatContent(currentStudent.annotated_content || currentStudent.content)"
                ></div>

              <!-- ✅ 悬浮菜单 (Fixed 定位) -->
              <div 
                v-if="showPopover" 
                class="popover-menu" 
                :style="{ top: popoverPosition.top + 'px', left: popoverPosition.left + 'px' }"
                @mousedown.prevent 
              >
                <!-- mousedown.prevent 防止点击按钮时失去焦点导致选区消失 -->
                <button @click="addMark">💬 添加批注</button>
              </div>

              <!-- ✅ 2. 批注列表区 (放在正文下面) -->
              <div class="annotations-section" v-if="annotations.length > 0">
                <div class="anno-title">批注详情 ({{ annotations.length }})</div>
                <div class="anno-grid">
                  <div class="anno-card" v-for="(note, index) in annotations" :key="note.id" :id="`card-${note.id}`" @click="focusHighlight(note.id)">
                    <div class="card-head">
                      <span class="badge">#{{ index + 1 }}</span>
                      <button class="del" @click="removeAnnotation(index)">✕</button>
                    </div>
                    <textarea 
                      v-model="note.text" 
                      placeholder="在此输入批注..." 
                      rows="2"
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ✅ 区域 B (右侧 35%)：评分控制台 (仅当已提交时显示) -->
          <div class="panel-right" v-if="currentStudent.status !== 0">
            <div class="score-card">
              <div class="card-header">
                <h3>📝 评分反馈</h3>
                <span class="status-badge" :class="getStatusClass(currentStudent.status)">
                  {{ getStatusText(currentStudent.status) }}
                </span>
              </div>
              
              <!-- 分数输入区 (大字号，居中) -->
              <div class="score-section">
                <div class="score-input-wrapper">
                  <input 
                    type="number" 
                    v-model="form.score" 
                    min="0" 
                    max="100" 
                    placeholder="--"
                    :class="{ 'has-score': form.score !== undefined }"
                  />
                  <span class="suffix">分</span>
                </div>
                <p class="score-hint">请输入 0-100 之间的分数</p>
              </div>

              <!-- 评语输入区 -->
              <div class="feedback-section">
                <label>评语建议</label>
                <div class="textarea-wrapper">
                  <textarea 
                    v-model="form.feedback" 
                    rows="6" 
                    placeholder="写点鼓励的话，或者指出需要改进的地方..."
                  ></textarea>
                </div>
                
                <!-- 快捷评语 (胶囊样式) -->
                <div class="quick-tags">
                  <span class="tag" @click="addFeedback('👍 做得很好！')">👍 做得很好</span>
                  <span class="tag" @click="addFeedback('📷 图片不清晰，请重交。')">📷 图片不清</span>
                  <span class="tag" @click="addFeedback('📝 请补充更多细节。')">📝 补充细节</span>
                  <span class="tag" @click="addFeedback('💡 思路很有创意！')">💡 有创意</span>
                </div>
              </div>
            </div>

            <!-- 底部操作 -->
            <div class="action-footer">
              <button class="btn-submit" @click="handleGrade">
                <span class="icon">✨</span> 提交评分 & 下一位
              </button>
              <p class="hint">快捷键: <kbd>Ctrl</kbd> + <kbd>Enter</kbd></p>
            </div>
          </div>

        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getAssignmentSubmissions, submitGrade, type GradingData, type SubmissionItem } from '@/api/homework';
import { getImgUrl } from '@/utils/index';
import { marked } from 'marked'; 
import { useUserStore } from '@/stores/modules/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const gradingData = ref<Partial<GradingData>>({});
const currentStudent = ref<SubmissionItem | null>(null);
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';

const form = reactive({ score: undefined as number | undefined, feedback: '' });

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown);
  const id = Number(route.params.id);
  const res = await getAssignmentSubmissions(id);
  gradingData.value = res;
  
  // 默认选中第一个待批改的学生
  const firstPending = res.students.find(s => s.status === 1);
  if (firstPending) currentStudent.value = firstPending;
});

onUnmounted(() => { // 记得引入 onUnmounted
  window.removeEventListener('keydown', handleKeydown);
});

// 监听当前学生变化，回显分数
watch(currentStudent, (newVal) => {
  if (newVal) {
    form.score = newVal.score;
    form.feedback = newVal.feedback || '';
  }
});


// 1. 自动跳转逻辑
const goToNextStudent = () => {
  // 找到当前学生的索引
  const index = sortedStudents.value.findIndex(s => s.student_id === currentStudent.value?.student_id);
  // 如果后面还有人，切换到下一个
  if (index !== -1 && index < sortedStudents.value.length - 1) {
    currentStudent.value = sortedStudents.value[index + 1];
  } else {
    alert('所有学生已批改完毕！');
  }
};

// 提交评分
const handleGrade = async () => {
  if (!currentStudent.value?.submission_id) return;
  if (form.score === undefined) return alert('请输入分数');
  if (userStore.pendingHomeworkCount > 0) {
    userStore.pendingHomeworkCount--;
  }

  let currentHtml = contentRef.value?.innerHTML || '';
  currentHtml = currentHtml.replace(/http(s)?:\/\/[^\/]+\/static\//g, '/static/');
  
  await submitGrade(currentStudent.value.submission_id, {
    score: form.score,
    feedback: form.feedback,
    annotated_content: currentHtml,
    annotations: annotations.value
  });
  
  alert('评分与批注已保存');
  // 更新本地状态
  currentStudent.value.status = 2;
  currentStudent.value.score = form.score;
  currentStudent.value.feedback = form.feedback;
  currentStudent.value.annotated_content = currentHtml;
  currentStudent.value.annotations = annotations.value;
  goToNextStudent();
};

// 3. 监听键盘 (Ctrl+Enter)
const handleKeydown = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    handleGrade();
  }
};

// 辅助
const sortedStudents = computed(() => {
  if (!gradingData.value.students) return [];
  // 排序：待批改(1) > 已批改(2) > 未交(0)
  return [...gradingData.value.students].sort((a, b) => {
    const order: Record<number, number> = { 1: 0, 2: 1, 0: 2 }; // 优先级 map
    return order[a.status] - order[b.status];
  });
});
const gradedCount = computed(() => gradingData.value.students?.filter(s => s.status === 2).length || 0);
const getStatusClass = (s: number) => ['gray', 'orange', 'green'][s];
const getStatusText = (s: number) => ['未提交', '待批改', '已批改'][s];
const formatDate = (d?: string) => d ? new Date(d).toLocaleString() : '';

// 简单的 Markdown 解析器
const formatContent = (content?: string) => {
  if (!content) return '';
  const processed = content.replace(/\]\((.*?)\)/g, (match, url) => {
    return `](${getImgUrl(url)})`;
  });

  const finalContent = processed.replace(/src="(\/static\/[^"]*)"/g, (match, url) => {
    return `src="${getImgUrl(url)}"`;
  });
  if (content.includes('highlight-marker')) {
      return finalContent; // 直接返回处理过路径的 HTML
  }

  return marked.parse(finalContent);
};

const addFeedback = (text: string) => {
  form.feedback = (form.feedback ? form.feedback + ' ' : '') + text;
};


// ----批注----
// 定义批注数据结构
interface Annotation {
  id: string;
  text: string;
}

const contentRef = ref<HTMLElement | null>(null); // 作业内容区域的 DOM
const showPopover = ref(false); // 控制悬浮菜单显示
const popoverPosition = reactive({ top: 0, left: 0 }); // 悬浮菜单位置
const annotations = ref<Annotation[]>([]); // 批注列表

// 监听学生切换，回显批注
watch(currentStudent, (newVal) => {
  if (newVal) {
    form.score = newVal.score;
    form.feedback = newVal.feedback || '';
    // ✅ 回显批注数据
    annotations.value = newVal.annotations || []; 
  }
});

// A. 鼠标抬起：检测选区，显示菜单
const handleTextSelect = () => {
  const selection = window.getSelection();
  // 如果没有选中文本，或者是点击操作，就隐藏菜单
  if (!selection || selection.toString().trim().length === 0) {
    showPopover.value = false;
    return;
  }

  // 计算位置 (显示在选区正上方)
  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();
  
  // 这里需要一点数学：减去左侧边栏宽度(250)和顶部高度(60)，或者直接用 fixed 定位
  // 为了简单稳妥，我们用 fixed 定位
  popoverPosition.top = rect.top - 40; 
  popoverPosition.left = rect.left + (rect.width / 2) - 40; // 居中
  
  showPopover.value = true;
};

// B. 点击“批注”按钮：包裹高亮标签
const addMark = () => {
  const selection = window.getSelection();
  if (!selection || !selection.rangeCount) return;

  const range = selection.getRangeAt(0);
  const span = document.createElement('span');
  const id = 'note-' + Date.now(); // 生成唯一ID
  
  span.className = 'highlight-marker'; // 加上高亮样式
  span.setAttribute('data-id', id);    // 绑定ID
  
  try {
    range.surroundContents(span); // 核心 API：用 span 包裹选中的文字
  } catch (e) {
    alert('无法跨段落批注，请在同一段落内选择');
    return;
  }
  
  // 清除选区，隐藏菜单
  selection.removeAllRanges();
  showPopover.value = false;

  // 添加到右侧列表
  annotations.value.push({ id, text: '' });
  
  // 可选：自动聚焦到刚生成的输入框 (略)
};

// C. 删除批注
const removeAnnotation = (index: number) => {
  const note = annotations.value[index];
  
  if (!note || !note.id) return;

  // 1. 操作 DOM：移除高亮标签 (Unwrap)
  // 在 contentRef 里找到那个带有 data-id 的 span
  const highlightSpan = contentRef.value?.querySelector(`span[data-id="${note.id}"]`);
  
  if (highlightSpan) {
    // 创建一个文档片段，把 span 里的内容(可能是文字，也可能是其他标签)移出来
    const parent = highlightSpan.parentNode;
    while (highlightSpan.firstChild) {
      parent?.insertBefore(highlightSpan.firstChild, highlightSpan);
    }
    // 移除空壳 span
    parent?.removeChild(highlightSpan);
  }

  // 2. 操作数据：从列表移除
  annotations.value.splice(index, 1);
};

// 1. 点击正文高亮 -> 聚焦卡片
const handleContentClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  // 检查点击的是不是高亮标记
  if (target.classList.contains('highlight-marker')) {
    const id = target.getAttribute('data-id');
    if (id) {
      // 找到对应的卡片
      const card = document.getElementById(`card-${id}`);
      if (card) {
        // 滚动到卡片
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // 添加闪烁动画类
        card.classList.add('flash-active');
        setTimeout(() => card.classList.remove('flash-active'), 1500);
      }
    }
  }
};

// 2. 点击卡片 -> 聚焦正文高亮
const focusHighlight = (id: string) => {
  const marker = contentRef.value?.querySelector(`span[data-id="${id}"]`);
  if (marker) {
    // 滚动到正文位置
    marker.scrollIntoView({ behavior: 'smooth', block: 'center' });
    // 添加高亮动画类 (需要配合 CSS)
    marker.classList.add('flash-highlight');
    setTimeout(() => marker.classList.remove('flash-highlight'), 1500);
  }
};
</script>

<style scoped lang="scss">
$primary: #00c9a7;
$bg: #f5f6fa;
$text-dark: #2A5850;

.dashboard-container { height: 100vh; display: flex; flex-direction: column; background: $bg; }

/* 头部 */
.grading-header {
  height: 60px; background: white; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; padding: 0 20px;
  .left { display: flex; align-items: center; gap: 15px; 
    .back-btn { border: none; background: none; cursor: pointer; color: #666; font-size: 14px; &:hover { color: $primary; } }
    h3 { margin: 0; font-size: 16px; }
  }
}

/* 主体 */
.grading-body { flex: 1; display: flex; overflow: hidden; }

/* 左侧名单 */
.student-list {
  width: 250px; background: white; border-right: 1px solid #eee; overflow-y: auto;
  .stu-item {
    display: flex; align-items: center; gap: 10px; padding: 15px; cursor: pointer; border-bottom: 1px solid #f9f9f9; transition: background 0.2s;
    &:hover { background: #f0fdfa; }
    &.active { background: #e6fffa; border-right: 3px solid $primary; }
    
    .avatar { position: relative; width: 40px; height: 40px; 
      img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
      .status-dot { position: absolute; bottom: 0; right: 0; width: 10px; height: 10px; border-radius: 50%; border: 2px solid white; 
        &.gray { background: #ccc; } &.orange { background: #fa8c16; } &.green { background: $primary; }
      }
    }
    .info { flex: 1; .name { font-weight: 600; font-size: 14px; } .status-text { font-size: 12px; color: #999; } }
    .score { font-weight: bold; color: $primary; }
  }
}

/* 右侧批改区 */
.grading-area { flex: 1; padding: 20px; overflow-y: auto; display: flex; justify-content: center; }
.grading-panel {
  background: white;
  width: 100%; /* 撑满父容器 */
  height: 100%; /* 撑满高度 */
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.05);
  display: flex; /* ✅ 开启 Flex */
  overflow: hidden; /* 防止圆角溢出 */
}

.panel-left {
  flex: 65%;
  border-right: 1px solid #f0f0f0;
  padding: 30px;
  overflow-y: auto; /* ✅ 独立滚动条 */
  background-color: #fff;

  .content-header {
    border-bottom: 1px solid #f0f0f0; /* 更轻的边框 */
    padding-bottom: 15px;
    margin-bottom: 25px;
    display: flex; /* 左右对齐 */
    justify-content: space-between;
    align-items: center;

    .student-info {
      display: flex; align-items: baseline; gap: 10px;
      .name { font-size: 18px; font-weight: 700; color: $text-dark; }
      .code { font-size: 13px; color: #999; font-family: monospace; }
      .divider { color: #eee; }
    }

    .time { font-size: 12px; color: #a4b0be; background: #f9f9f9; padding: 4px 10px; border-radius: 4px; }
  }

  /* 核心：限制图片大小 */
  .rich-content {
    font-size: 15px;
    line-height: 1.8;
    color: #333;
    
    :deep(img) {
      display: block;
      max-width: 100%;       /* 宽度不超容器 */
      max-height: 400px;     /* ✅ 高度限制：最大 400px，防止刷屏 */
      width: auto;           /* 保持比例 */
      margin: 15px 0;
      border-radius: 8px;
      border: 1px solid #eee;
      cursor: zoom-in;       /* 提示可放大 */
      transition: transform 0.2s;
      
      &:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      }
    }
  }

  .not-submitted {
    text-align: center; margin-top: 100px; color: #ccc;
    .empty-icon { font-size: 48px; margin-bottom: 10px; }
  }
}

/* === 右侧：评分控制台 (35%) === */
.panel-right {
  flex: 350px; /* 固定宽度或者比例 */
  background-color: #f8f9fc; /* 浅灰背景，区分内容区 */
  padding: 25px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-left: 1px solid #eee;

  .score-card {
    background: white;
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03); /* 悬浮卡片感 */
    
    .card-header {
      display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;
      h3 { margin: 0; font-size: 16px; color: #333; font-weight: 700; }
      .status-badge { font-size: 12px; padding: 2px 8px; border-radius: 4px; font-weight: 500;
        &.orange { background: #fff7e6; color: #fa8c16; }
        &.green { background: #f6ffed; color: #52c41a; }
      }
    }
    
    /* 分数大输入框 */
    .score-section {
      text-align: center; margin-bottom: 30px;
      .score-input-wrapper {
        position: relative; display: inline-block; width: 120px;
        input {
          width: 100%; height: 60px; font-size: 36px; font-weight: 800; text-align: center;
          border: none; border-bottom: 3px solid #eee; background: transparent;
          color: #ccc; transition: all 0.3s;
          &:focus, &.has-score { border-color: $primary; color: $primary; }
          &:focus { outline: none; }
          /* 隐藏数字选择器箭头 */
          &::-webkit-inner-spin-button { -webkit-appearance: none; }
        }
        .suffix {
          position: absolute; right: 0; bottom: 12px; font-size: 14px; color: #999; font-weight: normal;
        }
      }
      .score-hint { margin-top: 8px; font-size: 12px; color: #ccc; }
    }

    /* 评语区 */
    .feedback-section {
      label { display: block; margin-bottom: 10px; font-weight: 600; font-size: 13px; color: #555; }
      .textarea-wrapper {
        background: #f9f9f9; border-radius: 12px; padding: 5px; border: 1px solid transparent; transition: all 0.2s;
        &:focus-within { background: white; border-color: $primary; box-shadow: 0 0 0 3px rgba(0,201,167,0.1); }
        
        textarea {
          width: 100%; border: none; background: transparent; padding: 10px; resize: none; outline: none;
          font-size: 14px; line-height: 1.6; color: #333;
        }
      }
    }

    /* 快捷评语 */
    .quick-tags {
      margin-top: 15px; display: flex; flex-wrap: wrap; gap: 8px;
      .tag {
        font-size: 12px; padding: 6px 12px; background: white; border: 1px solid #eee; border-radius: 20px;
        color: #666; cursor: pointer; transition: all 0.2s;
        &:hover { border-color: $primary; color: $primary; background: #f0fdfa; transform: translateY(-1px); }
      }
    }
  }

  .action-footer {
    text-align: center;
    .btn-submit {
      width: 100%; padding: 15px; background: $primary; color: white; border: none; border-radius: 12px;
      font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.2s;
      box-shadow: 0 8px 20px rgba(0,201,167,0.25);
      display: flex; align-items: center; justify-content: center; gap: 8px;
      
      &:hover { transform: translateY(-2px); box-shadow: 0 12px 25px rgba(0,201,167,0.35); }
      &:active { transform: translateY(0); }
    }
    .hint { margin-top: 12px; font-size: 12px; color: #bbb; kbd { background: #eee; padding: 2px 5px; border-radius: 4px; font-family: monospace; } }
  }
}

.submission-content {
  flex: 1;
  .content-header { border-bottom: 1px dashed #eee; padding-bottom: 10px; margin-bottom: 20px; color: #999; font-size: 12px; }
  .rich-content { 
    font-size: 14px; line-height: 1.8; color: #333; 
    /* 这里的样式为了适配 markdown 图片 */
    :deep(img) { max-width: 100%; border-radius: 8px; margin: 10px 0; border: 1px solid #eee; }
  }
}

.grading-controls {
  margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; background: #f9f9f9; padding: 20px; border-radius: 8px;
  .input-group { margin-bottom: 15px; 
    label { display: block; margin-bottom: 5px; font-weight: bold; font-size: 13px; }
    input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
  }
  .btn-submit { width: 100%; background: $primary; color: white; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; &:hover { filter: brightness(0.9); } }
}

/* 悬浮菜单 */
.popover-menu {
  position: fixed; z-index: 9999;
  background: #333; color: white; border-radius: 4px; padding: 4px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  transform: translateX(-50%); /* 居中校正 */
  
  button { background: transparent; border: none; color: white; padding: 4px 8px; cursor: pointer; font-size: 12px; &:hover { background: rgba(255,255,255,0.2); border-radius: 2px; } }
  &::after { content: ''; position: absolute; bottom: -5px; left: 50%; margin-left: -5px; border-width: 5px 5px 0; border-style: solid; border-color: #333 transparent transparent transparent; }
}

/* 高亮标记 (注入到 v-html 里的) */
:deep(.highlight-marker) {
  background-color: #ffeb3b;
  border-bottom: 2px solid #fbc02d;
  cursor: pointer;
}

/* 批注列表 */
.annotations-list {
  background: white; border-radius: 12px; padding: 15px; margin-bottom: 15px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  max-height: 300px; overflow-y: auto; /* 太多了可以滚动 */
  
  h4 { font-size: 14px; margin: 0 0 10px; color: #333; border-left: 3px solid #ffeb3b; padding-left: 8px; }
  
  .note-item {
    background: #fffbef; border: 1px solid #f0e6ce; border-radius: 8px; padding: 10px; margin-bottom: 8px;
    
    .note-header { display: flex; justify-content: space-between; margin-bottom: 5px; .index { font-weight: bold; color: #b7a980; font-size: 12px; } .del-btn { color: #ff6b6b; cursor: pointer; border: none; background: none; font-size: 12px; } }
    .note-input { width: 100%; border: none; background: transparent; outline: none; font-size: 13px; color: #555; resize: none; font-family: inherit; }
  }
}

/* 作业内容包裹层 */
.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 30px; /* 正文和批注区的间距 */
}

/* 批注区域 */
.annotations-section {
  border-top: 1px dashed #eee;
  padding-top: 20px;
  
  .anno-title {
    font-size: 14px;
    font-weight: bold;
    color: #333;
    margin-bottom: 15px;
    border-left: 4px solid #ffeb3b; /* 黄色高亮条 */
    padding-left: 10px;
  }

  /* 网格布局：一行放两个便利贴 */
  .anno-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
    
    .anno-card {
      background: #fffbef; /* 淡黄色便利贴背景 */
      border: 1px solid #f0e6ce;
      border-radius: 8px;
      padding: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.02);
      transition: transform 0.2s;
      
      &:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.05); }

      .card-head {
        display: flex; justify-content: space-between; margin-bottom: 8px;
        .badge { background: #e8dcb9; color: #8c7e58; font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
        .del { border: none; background: none; color: #aaa; cursor: pointer; font-size: 14px; &:hover { color: #ff4d4f; } }
      }
      
      textarea {
        width: 100%; border: none; background: transparent; 
        font-size: 13px; color: #555; resize: none; outline: none;
        line-height: 1.5;
        &::placeholder { color: #bbb; }
      }
    }
  }
}

/* 动画：卡片闪烁 (淡黄色 -> 深黄色 -> 淡黄色) */
@keyframes flashCard {
  0% { box-shadow: 0 0 0 0 rgba(255, 235, 59, 0); transform: scale(1); }
  50% { box-shadow: 0 0 15px rgba(255, 235, 59, 0.8); border-color: #fbc02d; transform: scale(1.02); }
  100% { box-shadow: 0 0 0 0 rgba(255, 235, 59, 0); transform: scale(1); }
}

/* 动画：文字闪烁 (背景加深) */
@keyframes flashText {
  0% { background-color: #ffeb3b; }
  50% { background-color: #ff9800; color: white; padding: 2px 4px; border-radius: 4px; }
  100% { background-color: #ffeb3b; color: inherit; padding: 0 2px; }
}

/* 应用动画的类 */
.flash-active {
  animation: flashCard 1s ease;
  border-color: #fbc02d !important; /* 保持边框深色一点 */
}

/* 注意：高亮样式在 v-html 里，需要 :deep */
:deep(.flash-highlight) {
  animation: flashText 1s ease;
}

/* 给卡片加个手型，提示可点 */
.anno-card {
  cursor: pointer;
}
</style>