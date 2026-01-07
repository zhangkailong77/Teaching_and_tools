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
        <!-- 这里假设 content 是富文本，如果后端只返回了标题，这里可能需要再调一次详情接口 -->
        <!-- 为了简化，假设列表接口或者打开时传入了 content -->
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
        <div v-if="isReadOnly" class="answer-read-only">
          {{ submissionContent }}
          <!-- 如果有图片，解析 markdown 显示图片 (这里简化处理) -->
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
const open = (task: any) => {
  visible.value = true;
  // 初始化数据
  taskInfo.id = task.assignment_id || task.id; // 兼容不同接口字段
  taskInfo.title = task.title || task.lessonTitle;
  taskInfo.content = task.content || task.contentRequirement || '请完成本节课实训任务。';
  taskInfo.deadline = task.deadline;
  taskInfo.status = task.status === 'pending' || task.status === 0 ? 0 : (task.status === 'graded' || task.status === 2 ? 2 : 1);
  taskInfo.score = task.score;
  taskInfo.feedback = task.feedback; // 如果接口有返回的话
  
  // 如果是已提交，这里应该回显内容 (目前假设 content 没存，暂时置空，真实场景需调接口获取详情)
  submissionContent.value = task.my_content || ''; 
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
</style>