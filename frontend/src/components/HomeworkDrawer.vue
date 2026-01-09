<template>
  <el-drawer
    v-model="visible"
    :title="isReadOnly ? '作业详情' : '作业提交'"
    direction="rtl"
    size="600px"
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
      </div>

      <!-- 3. 老师评语 (仅已批改显示) -->
      <div v-if="taskInfo.status === 2" class="feedback-box">
        <h4>👨‍🏫 老师评分：<span class="score">{{ taskInfo.score }}分</span></h4>
        <div class="comment">评语：{{ taskInfo.feedback || '暂无评语' }}</div>
      </div>

      <!-- 4. 答题区域 -->
      <div class="hw-answer-area">
        <h4>{{ isReadOnly ? '我的提交：' : '填写答案：' }}</h4>
        
        <!-- 只读模式 (已提交/已批改) -->
        <div v-if="isReadOnly" class="read-only-wrapper">
          
          <!-- A. 成绩单 (仅已批改显示) -->
          <div v-if="taskInfo.status === 2" class="score-report">
            <div class="score-circle">{{ taskInfo.score }}</div>
            <div class="report-info">
              <h4>老师评语：</h4>
              <p>{{ taskInfo.feedback || '暂无评语' }}</p>
            </div>
          </div>

          <div class="divider"></div>

          <!-- B. 作业内容 (支持高亮) -->
          <div class="submission-viewer">
            <div 
               class="rich-content" 
               v-html="formatContent(resultData.content || submissionContent)"
             ></div>
          </div>

          <!-- C. 批注列表 (仅当有批注时显示) -->
          <div v-if="resultData.annotations && resultData.annotations.length > 0" class="annotations-box">
            <h4>老师批注：</h4>
            <div 
              v-for="note in resultData.annotations" 
              :key="note.id" 
              class="note-item"
              :class="{ active: activeAnnotationId === note.id }"
            >
              <span class="marker-dot"></span>
              <p>{{ note.text }}</p>
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
  feedback: ''
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
    taskInfo.id = task.assignment_id || task.id; // 兼容不同接口字段
    taskInfo.title = task.title || task.lessonTitle;
    taskInfo.content = task.content || task.contentRequirement || '请完成本节课实训任务。';
    taskInfo.deadline = task.deadline;
    taskInfo.status = task.status === 'pending' || task.status === 0 ? 0 : (task.status === 'graded' || task.status === 2 ? 2 : 1);
    taskInfo.score = task.score;
    taskInfo.feedback = task.feedback; // 如果接口有返回的话
  
    if (task.status !== 0) {
      const res = await getSubmissionResult(taskInfo.id);
      
      // 回显提交内容
      submissionContent.value = res.content;
      
      // 回显批改结果
      taskInfo.score = res.score;
      taskInfo.feedback = res.feedback;
      resultData.value = res; // 存入完整数据以供高亮显示
    } else {
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
    await submitHomework(taskInfo.id, { content: submissionContent.value });
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
  const processedContent = content.replace(/\]\((.*?)\)/g, (match, url) => {
    return `](${getImgUrl(url)})`;
  });

  // 然后再解析成 HTML
  return marked.parse(processedContent);
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
  .rich-text, .comment { font-size: 14px; color: #555; line-height: 1.6; }
  .score { color: $primary-color; font-size: 18px; font-weight: bold; }
}
.feedback-box { background: #f6ffed; border: 1px solid #b7eb8f; }

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
</style>