<template>
  <el-drawer
    v-model="visible"
    :title="isReadOnly ? '作业详情' : '作业提交'"
    direction="rtl"
    size="900px"
    class="hw-drawer"
  >
    <div class="homework-body" v-loading="loading">
      <!-- 1. 头部信息 -->
      <div class="hw-header">
        <h3>{{ taskInfo.title }}</h3>
        <div class="hw-meta">
          <span class="tag" :class="statusClass">{{ statusText }}</span>
          <span class="date">截止: {{ formatDate(taskInfo.deadline) }}</span>
        </div>
      </div>

      <!-- 2. 题目要求 -->
      <div class="hw-requirement">
        <h4>📝 作业要求：</h4>
        <div class="rich-text" v-html="taskInfo.content || '暂无详细描述'"></div>

        <!-- ✅ 新增：附件展示区域 -->
        <div v-if="taskInfo.attachments && taskInfo.attachments.length > 0" class="hw-attachments">
           <h5>📎 参考资料：</h5>
           <div class="file-list">
             <a 
               v-for="(url, index) in taskInfo.attachments" 
               :key="index"
               :href="getFileUrl(url)" 
               target="_blank"
               class="file-item"
             >
               <span class="icon">📄</span>
               <span class="name">附件 {{ index + 1 }}</span>
             </a>
           </div>
        </div>
      </div>

      <!-- 4. 答题区域 -->
      <div class="hw-answer-area">
        <h4>{{ isReadOnly ? '我的提交：' : '填写答案：' }}</h4>
        
        <!-- 只读模式 (已提交/已批改) -->
        <div v-if="isReadOnly" class="read-only-wrapper">
          
          <!-- 顶部：成绩单 (横跨全宽) -->
          <div v-if="taskInfo.status === 2" class="score-report-banner">
             <div class="score">{{ taskInfo.score }}<small>分</small></div>
             <div class="feedback">
               <h4>👨‍🏫 老师总评：</h4>
               <p>{{ taskInfo.feedback || '暂无评语' }}</p>
             </div>
          </div>

          <!-- 主体：左右分栏 -->
          <div class="review-body">
            
            <!-- 左侧：作业内容 -->
            <div class="review-left">
               <div class="section-title">我的提交</div>
               <div 
                 class="rich-content"
                 ref="contentRef"
                 v-html="formatContent(resultData.content || submissionContent)"
                 @click="handleHighlightClick"
               ></div>
            </div>

            <!-- 右侧：批注列表 -->
            <div class="review-right" v-if="resultData.annotations && resultData.annotations.length > 0">
               <div class="section-title">批注详情 ({{ resultData.annotations.length }})</div>
               <div class="anno-list">
                 <div 
                   v-for="(note, index) in resultData.annotations" 
                   :key="note.id" 
                   class="anno-card"
                   :class="{ active: activeAnnotationId === note.id }"
                   :id="`card-${note.id}`"
                   @click="focusHighlight(note.id)" 
                 >
                   <div class="card-head"><span class="badge">#{{ index + 1 }}</span></div>
                   <p>{{ note.text }}</p>
                 </div>
               </div>
            </div>
          </div>
        </div>

        <!-- 编辑模式 (未提交) -->
        <div v-else>
          <textarea 
            v-model="submissionContent" 
            rows="8" 
            placeholder="在此输入答案，或点击下方按钮上传截图..."
            class="answer-input"
          ></textarea>
          
          <div class="toolbar">
            <button class="btn-icon" @click="triggerUpload">📷 上传图片</button>
            <input type="file" ref="uploadInputRef" accept="image/*" style="display:none" @change="handleUpload"/>
          </div>
        </div>
      </div>

      <!-- 5. 底部操作 -->
      <div class="hw-footer" v-if="!isReadOnly">
        <button class="btn-primary" @click="handleSubmit" :disabled="submitting">
          {{ submitting ? '提交中...' : '确认提交' }}
        </button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue';
import { submitHomework } from '@/api/homework';
import { uploadImage } from '@/api/common';
import { getSubmissionResult, type SubmissionResult } from '@/api/homework';
import { getImgUrl } from '@/utils/index';
import { marked } from 'marked';

const contentRef = ref<HTMLElement | null>(null);
const resultData = ref<Partial<SubmissionResult>>({});
const activeAnnotationId = ref<string | null>(null); // 当前点击的高亮ID


// 定义 Props 不需要，我们要用 defineExpose 暴露方法给父组件调用
const emit = defineEmits(['success']);

const visible = ref(false);
const loading = ref(false);
const submitting = ref(false);
const uploadInputRef = ref<HTMLInputElement | null>(null);

// 作业数据模型
const taskInfo = reactive({
  id: 0,
  title: '',
  content: '',
  deadline: '',
  status: 0, // 0:未交, 1:已交, 2:已批
  score: null as number | null,
  feedback: '',
  attachments: [] as string[]
});
const submissionContent = ref('');

// 计算属性
const isReadOnly = computed(() => taskInfo.status !== 0); // 只要交了就暂定只读
const statusText = computed(() => ['待提交', '已提交', '已批改'][taskInfo.status] || '未知');
const statusClass = computed(() => ['pending', 'submitted', 'graded'][taskInfo.status]);

// === 对外暴露的方法：打开抽屉 ===
const open = async (task: any) => {
  visible.value = true;
  loading.value = true;

  try {
    taskInfo.id = task.assignment_id || task.id; 
    taskInfo.title = task.title || task.lessonTitle;
    
    // 先设置默认值，稍后用接口数据覆盖
    taskInfo.content = task.content || task.contentRequirement || '请完成本节课实训任务。';
    taskInfo.deadline = task.deadline;
    taskInfo.status = task.status === 'pending' || task.status === 0 ? 0 : (task.status === 'graded' || task.status === 2 ? 2 : 1);
    taskInfo.score = task.score;
    taskInfo.feedback = task.feedback; 
    
    // ✅ 修改点 1：先清空附件列表
    taskInfo.attachments = []; 

    // ✅ 修改点 2：无论什么状态，都调用接口获取【题目详情】和【附件】
    // 后端接口已经改过，支持返回 assignment_attachments 和 assignment_requirement
    const res = await getSubmissionResult(taskInfo.id);
    
    // 填充附件
    if (res.assignment_attachments) {
      taskInfo.attachments = res.assignment_attachments;
    }
    // 填充最新的作业要求 (覆盖默认文本)
    if (res.assignment_requirement) {
      taskInfo.content = res.assignment_requirement;
    }

    // ✅ 修改点 3：根据状态处理【提交内容】
    if (taskInfo.status !== 0) {
      // 如果已提交/已批改，回显学生的答案和分数
      submissionContent.value = res.content;
      taskInfo.score = res.score;
      taskInfo.feedback = res.feedback;
      resultData.value = res; 
    } else {
      // 如果未提交，清空输入框
      submissionContent.value = '';
    }

  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const handleHighlightClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  if (target.classList.contains('highlight-marker')) {
    const id = target.getAttribute('data-id');
    if (id) {
      activeAnnotationId.value = id; // 激活对应的批注卡片
    }
  }
};

// 提交逻辑
const handleSubmit = async () => {
  if (!submissionContent.value) return alert('内容不能为空');
  submitting.value = true;
  try {
    const cleanContent = submissionContent.value.replace(/http(s)?:\/\/[^\/]+\/static\//g, '/static/');
    await submitHomework(taskInfo.id, { content: cleanContent });
    alert('提交成功！');
    visible.value = false;
    emit('success'); // 通知父组件刷新列表
  } catch (e) {
    console.error(e);
  } finally {
    submitting.value = false;
  }
};

// 上传逻辑
const triggerUpload = () => uploadInputRef.value?.click();
const handleUpload = async (e: Event) => {
  const files = (e.target as HTMLInputElement).files;
  if (files && files[0]) {
    try {
      const res = await uploadImage(files[0], 'common');
      submissionContent.value += `\n\n![截图](${res.url})`;
    } catch { alert('上传失败'); }
  }
};

const formatDate = (str?: string) => str ? new Date(str).toLocaleDateString() : '无限制';

defineExpose({ open });

// 增加一个格式化函数
const formatContent = (content?: string) => {
  if (!content) return '';
  
  // 1. 获取 Base URL
  const baseUrl = import.meta.env.VITE_IMG_BASE_URL;

  // 2. 替换 Markdown 里的图片路径
  // 将 ](/static/ 替换为 ](http://.../static/
  const processed = content.replace(/\]\(\/static\//g, `](${baseUrl}/static/`);

  // 3. 替换 HTML 里的图片路径 (兼容老师批改后的内容)
  // 将 src="/static/ 替换为 src="http://.../static/
  const finalContent = processed.replace(/src="\/static\//g, `src="${baseUrl}/static/`);

  return marked.parse(finalContent);
}

// 2. ✅ 新增：点击卡片 -> 聚焦正文高亮
const focusHighlight = (id: string) => {
  // 设置当前激活 ID (让卡片变色)
  activeAnnotationId.value = id;

  // 找到正文里的 span
  const marker = contentRef.value?.querySelector(`span[data-id="${id}"]`);
  
  if (marker) {
    // 滚动到正文位置
    marker.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // 添加闪烁动画类
    marker.classList.add('flash-highlight');
    setTimeout(() => marker.classList.remove('flash-highlight'), 1500);
  }
};

// ✅ 新增：获取完整文件路径的辅助函数
const getFileUrl = (url: string) => {
  if (!url) return '';
  // 1. 如果已经是完整的网络地址，直接返回
  if (url.startsWith('http') || url.startsWith('https')) {
    return url;
  }
  
  // 2. 获取后端基础地址
  let baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
  baseUrl = baseUrl.replace('/api/v1', '');
  
  // 去掉末尾可能多余的斜杠
  if (baseUrl.endsWith('/')) {
    baseUrl = baseUrl.slice(0, -1);
  }
  
  // 3. 拼接地址
  return `${baseUrl}${url}`;
};
</script>

<style scoped lang="scss">
$primary-color: #00c9a7;

.homework-body { padding: 10px; }
.hw-header { border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 15px;
  h3 { margin: 0 0 8px; color: #333; }
  .hw-meta { font-size: 12px; color: #999; display: flex; gap: 15px; align-items: center; }
  .tag { padding: 2px 8px; border-radius: 4px; font-weight: bold;
    &.pending { background: #fff7e6; color: #fa8c16; }
    &.submitted { background: #e6f7ff; color: #1890ff; }
    &.graded { background: #f6ffed; color: #52c41a; }
  }
}
.hw-requirement, .feedback-box { background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px;
  h4 { margin: 0 0 10px; font-size: 14px; color: #333; }
  .rich-text { 
    font-size: 14px; 
    color: #555; 
    line-height: 1.6;
    
    /* ✅ 新增：强制换行属性 */
    word-break: break-all;       /* 强制打断长单词 */
    overflow-wrap: break-word;   /* 标准换行属性 */
    white-space: pre-wrap;       /* 保留用户输入的换行符，同时允许自动换行 */
    
    /* 防止图片过大撑开 */
    :deep(img) {
      max-width: 100%;
      height: auto;
      border-radius: 4px;
    }
  }
  .score { color: $primary-color; font-size: 18px; font-weight: bold; }
}
.feedback-box { background: #f6ffed; border: 1px solid #b7eb8f; }

.hw-attachments {
  margin-top: 15px; border-top: 1px dashed #ddd; padding-top: 10px;
  h5 { margin: 0 0 8px; font-size: 13px; color: #666; font-weight: 600; }
  
  .file-list {
    display: flex; flex-wrap: wrap; gap: 10px;
  }
  
  .file-item {
    display: flex; align-items: center; gap: 6px;
    background: #fff; border: 1px solid #ddd;
    padding: 8px 12px; border-radius: 6px;
    text-decoration: none; color: #555; font-size: 13px;
    transition: all 0.2s;
    
    &:hover {
      border-color: $primary-color; color: $primary-color; background: #f0fdfa;
    }
    .icon { font-size: 16px; }
  }
}

.hw-answer-area {
  h4 { margin: 0 0 10px; font-size: 14px; }
  .answer-input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; resize: vertical; outline: none; font-family: inherit; &:focus { border-color: $primary-color; } }
  .answer-read-only { padding: 15px; background: #f5f5f5; border-radius: 8px; white-space: pre-wrap; color: #666; }
  .toolbar { margin-top: 10px; .btn-icon { background: white; border: 1px solid #ddd; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; &:hover { color: $primary-color; border-color: $primary-color; } } }
}
.hw-footer { margin-top: 30px; button { width: 100%; padding: 12px; background: $primary-color; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; &:disabled { opacity: 0.6; } } }

/* 成绩单样式 */
.score-report {
  background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 8px; padding: 15px;
  display: flex; align-items: center; gap: 20px; margin-bottom: 20px;
  
  .score-circle {
    width: 60px; height: 60px; border-radius: 50%; background: #52c41a; color: white;
    font-size: 24px; font-weight: bold; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 10px rgba(82, 196, 26, 0.3);
  }
  .report-info { flex: 1; h4 { margin: 0 0 5px; color: #333; } p { margin: 0; color: #666; font-size: 14px; } }
}

/* 高亮交互样式 */
.rich-content {
  line-height: 1.8; font-size: 14px; color: #333; padding: 10px; border: 1px dashed #ddd; border-radius: 8px; background: #fafafa;
  
  /* 必须加上 :deep 才能影响 v-html 里的内容 */
  :deep(.highlight-marker) {
    background-color: #fff1b8; border-bottom: 2px solid #fadb14; cursor: pointer; transition: background 0.2s;
    &:hover { background-color: #ffec3d; }
  }

  :deep(img) {
    max-width: 100%;       /* 宽度不超容器 */
    max-height: 300px;     /* 高度限制 */
    object-fit: contain;   /* 保持比例 */
    border-radius: 8px;
    border: 1px solid #eee;
    margin-top: 10px;
    display: block;
  }
}

/* 批注列表样式 */
.annotations-box {
  margin-top: 20px; border-top: 1px solid #eee; padding-top: 15px;
  
  .note-item {
    display: flex; gap: 10px; padding: 10px; border-radius: 6px; margin-bottom: 5px; transition: all 0.2s;
    .marker-dot { width: 8px; height: 8px; background: #fadb14; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
    p { margin: 0; font-size: 13px; color: #555; }
    
    /* 激活状态 (点击高亮时) */
    &.active { background: #fffbe6; transform: translateX(5px); border-left: 3px solid #fadb14; }
  }
}

/* 成绩单横幅 */
.score-report-banner {
  background: linear-gradient(135deg, #f6ffed 0%, #e6f7ff 100%);
  border: 1px solid #b7eb8f; border-radius: 12px; padding: 20px;
  display: flex; align-items: center; gap: 30px; margin-bottom: 25px;
  
  .score { font-size: 48px; font-weight: 800; color: #52c41a; line-height: 1; small { font-size: 16px; font-weight: normal; color: #888; } }
  .feedback { h4 { margin: 0 0 5px; font-size: 14px; color: #555; } p { margin: 0; color: #333; font-weight: 500; } }
}

/* 分栏布局 */
.review-body {
  display: flex; gap: 30px; height: calc(100vh - 200px); /* 让它撑满高度 */
  
  .review-left {
    flex: 1; overflow-y: auto; padding-right: 10px;
    .section-title { font-size: 14px; font-weight: bold; color: #999; margin-bottom: 10px; }
  }
  
  .review-right {
    width: 300px; flex-shrink: 0; overflow-y: auto; padding-left: 10px; border-left: 1px solid #eee;
    .section-title { font-size: 14px; font-weight: bold; color: #999; margin-bottom: 10px; padding-left: 10px; }
    
    .anno-list { display: flex; flex-direction: column; gap: 15px; padding: 5px; }
    
    .anno-card {
      background: #fffbef; border: 1px solid #f0e6ce; border-radius: 8px; padding: 12px;
      transition: all 0.3s; cursor: pointer;
      
      .card-head { margin-bottom: 5px; .badge { background: #e8dcb9; color: #8c7e58; font-size: 10px; padding: 1px 5px; border-radius: 4px; } }
      p { margin: 0; font-size: 13px; color: #555; line-height: 1.5; }
      
      /* 激活状态 */
      &.active {
        background: #fff; border-color: #fadb14; box-shadow: 0 4px 12px rgba(250, 219, 20, 0.4); transform: scale(1.02);
      }
    }
  }
}

@keyframes flashText {
  0% { background-color: #ffeb3b; }
  50% { background-color: #ff9800; color: white; padding: 2px 4px; border-radius: 4px; }
  100% { background-color: #ffeb3b; color: inherit; padding: 0 2px; }
}

/* 必须加上 :deep 才能影响 v-html 里的内容 */
:deep(.flash-highlight) {
  animation: flashText 1s ease;
}
</style>