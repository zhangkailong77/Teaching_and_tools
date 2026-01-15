<template>
  <div class="paper-editor">
    
    <!-- 1. 顶部导航栏 -->
    <div class="editor-header">
      <div class="left">
        <el-button link icon="ArrowLeft" @click="$emit('back')">返回列表</el-button>
        <span class="divider">/</span>
        <span class="page-title">创建新试卷</span>
      </div>
      
      <div class="center">
        <el-steps 
          :active="currentStep" 
          finish-status="success" 
          align-center 
          style="width: 500px;"
        >
          <el-step title="基础信息" />
          <el-step title="题目组装" />
          <el-step title="发布配置" />
        </el-steps>
      </div>

      <div class="right btn-group">
        <button v-if="currentStep > 0" class="btn-prev" @click="currentStep--">上一步</button>
        <button 
          v-if="currentStep < 2" 
          class="btn-next" 
          @click="handleNext"
        >
          下一步
        </button>
        <button 
          v-if="currentStep === 2" 
          class="btn-next success" 
          @click="handleSubmit" 
          :disabled="submitting"
        >
          {{ submitting ? '发布中...' : '完成并发布' }}
        </button>
      </div>
    </div>

    <!-- 2. 主体内容区 (滚动区域) -->
    <div class="editor-body">
      <div class="content-wrapper">
        <!-- 复用之前的 Wizard 子组件 -->
        <keep-alive>
          <component 
            :is="currentStepComponent" 
            v-model="examForm" 
            class="step-component"
          />
        </keep-alive>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { createExam, getExamDetail, updateExam } from '@/api/exam'
import Step1 from './wizard/Step1.vue'
import Step2 from './wizard/Step2.vue'
import Step3 from './wizard/Step3.vue'

const emit = defineEmits(['back', 'success'])
const props = defineProps<{ 
  initialData?: any
}>()
const currentStep = ref(0)
const submitting = ref(false)
const loading = ref(false)

const examForm = reactive({
  title: '',
  mode: 1,
  questions: [] as any[],
  random_config: [] as any[],
  duration: 60,
  pass_score: 60,
  total_score: 100
})

const loadData = async () => {
  if (!props.initialData?.id) {
    // 如果没有 ID，说明是新建模式，重置表单
    resetForm();
    currentStep.value = 0;
    return;
  }

  // 如果有 ID，说明是编辑/查看模式
  currentStep.value = 1; // 立即跳到第二步
  loading.value = true;
  
  try {
    const res = await getExamDetail(props.initialData.id);
    
    // ✅ 关键：使用 Object.assign 或直接赋值确保响应式
    examForm.title = res.title;
    examForm.mode = res.mode;
    examForm.duration = res.duration;
    examForm.pass_score = res.pass_score;
    examForm.total_score = res.total_score;
    examForm.start_time = res.start_time;
    examForm.end_time = res.end_time;
    examForm.class_ids = res.class_ids || [];
    
    // ✅ 关键：处理题目列表，确保 raw 数据存在以便 Step2 渲染
    if (res.questions) {
      examForm.questions = res.questions.map((q: any) => ({
        ...q,
        // 确保包含题目正文和选项
        raw: q.raw || { content: q.title, type: res.mode === 1 ? 'single' : '' } 
      }));
    }
    
    if (res.random_config) {
      examForm.random_config = res.random_config;
    }
  } catch (e) {
    console.error(e);
    ElMessage.error('获取详情失败');
  } finally {
    loading.value = false;
  }
};

watch(() => props.initialData, () => {
  loadData();
}, { immediate: true, deep: true });

// 4. 重置表单函数 (新建时调用)
const resetForm = () => {
  examForm.title = '';
  examForm.mode = 1;
  examForm.questions = [];
  examForm.random_config = [];
  examForm.duration = 60;
  examForm.pass_score = 60;
  examForm.total_score = 0;
  examForm.start_time = '';
  examForm.end_time = '';
  examForm.class_ids = [];
};

const currentStepComponent = computed(() => {
  switch (currentStep.value) {
    case 0: return Step1
    case 1: return Step2
    case 2: return Step3
    default: return Step1
  }
})

// 简单的校验逻辑 (同之前)
const handleNext = () => {
  if (currentStep.value === 0 && !examForm.title) return ElMessage.warning('请输入标题')
  currentStep.value++
}

const handleSubmit = async () => {
  if (examForm.class_ids.length === 0) return ElMessage.warning('请选择发布班级')
  if (!examForm.start_time) return ElMessage.warning('请设置考试有效时间范围')

  submitting.value = true
  try {
    let finalMode = examForm.mode
    let finalQuestions = undefined

    if (examForm.mode === 2 && examForm.questions.length > 0) {
      finalMode = 1 
      finalQuestions = examForm.questions.map((q: any) => ({ 
        question_id: q.question_id || q.id, // 兼容字段名
        score: q.score 
      }))
    } 

    else if (examForm.mode === 1) {
      finalQuestions = examForm.questions.map((q: any) => ({ 
        question_id: q.question_id || q.id, 
        score: q.score 
      }))
    }

    const payload = {
      title: examForm.title,
      mode: finalMode, 
      questions: finalQuestions, 
      random_config: finalMode === 2 ? examForm.random_config : undefined,
      duration: examForm.duration,
      pass_score: examForm.pass_score,
      total_score: examForm.total_score,
      start_time: examForm.start_time,
      end_time: examForm.end_time,
      class_ids: examForm.class_ids
    }

    if (props.initialData?.id) {
      await updateExam(props.initialData.id, payload)
      ElMessage.success('试卷更新成功')
    } else {
      await createExam(payload)
      ElMessage.success('试卷发布成功')
    }
    emit('success')
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  // ✅ 1. 只要检测到有 ID，立即切换到步骤 1 (即第二步：题目组装)
  if (props.initialData?.id) {
    currentStep.value = 1
    
    loading.value = true
    try {
      const res = await getExamDetail(props.initialData.id)
      
      // 2. 异步填充数据
      examForm.title = res.title
      examForm.mode = res.mode
      examForm.questions = res.questions || []
      examForm.random_config = res.random_config || []
      examForm.duration = res.duration
      examForm.pass_score = res.pass_score
      examForm.total_score = res.total_score
      examForm.start_time = res.start_time
      examForm.end_time = res.end_time
      examForm.class_ids = res.class_ids || []
            
    } catch (e) {
      ElMessage.error('加载试卷详情失败')
      currentStep.value = 0 // 如果加载彻底失败，退回第一步
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped lang="scss">
$header-height: 60px;
$primary: #00c9a7;

.paper-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px; /* 圆角跟 Tab 保持一致 */
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
  overflow: hidden;
}

.editor-header {
  height: 70px; /* 稍微增高一点，更大气 */
  background: white;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px; /* 增加左右内边距，防止贴边 */
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03); /* 更柔和的阴影 */

  .left {
    display: flex; align-items: center; gap: 12px;
    .page-title { font-size: 18px; font-weight: 700; color: #2c3e50; } /* 标题加深加大 */
    .divider { color: #e0e0e0; font-size: 18px; font-weight: 300; }
  }

  .center {
    flex: 1; display: flex; justify-content: center;
    
    /* 覆盖 Element Steps 样式，使其更精致 */
    :deep(.el-step__title) {
      font-size: 14px;
      font-weight: 500;
      color: #909399; /* 默认浅灰 */
    }
    :deep(.el-step__head.is-process) {
      color: $primary;
      border-color: $primary;
    }
    :deep(.el-step__title.is-process) {
      color: $primary; 
      font-weight: 700;
    }
    :deep(.el-step__head.is-success) {
      color: $primary;
      border-color: $primary;
    }
    :deep(.el-step__title.is-success) {
      color: $primary;
    }
    :deep(.el-step__line) {
      background-color: #f0f0f0; /* 线条更淡 */
    }
  }

  .right.btn-group {
    display: flex; gap: 15px; margin-right: 20px; /* ✅ 关键：右侧留出空间，不贴边 */

    .btn-prev {
      background: white;
      color: #606266;
      border: 1px solid #dcdfe6;
      padding: 10px 30px; /* 尺寸和 next 一样 */
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05); /* 淡淡的阴影 */

      &:hover {
        color: $primary;
        border-color: $primary; /* 悬停变色 */
        background: rgba(0, 201, 167, 0.05);
        transform: translateY(-2px); /* 同样的悬浮动效 */
        box-shadow: 0 4px 12px rgba(0, 201, 167, 0.15);
      }
      
      &:active { transform: translateY(0); }
    }

    /* 统一的下一步/发布按钮样式 (复用抽屉风格) */
    .btn-next {
      background: $primary;
      color: white;
      border: none;
      padding: 10px 30px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0, 201, 167, 0.3); /* 青绿色投影 */
      transition: all 0.3s;

      &:hover {
        transform: translateY(-2px); /* 上浮效果 */
        box-shadow: 0 6px 16px rgba(0, 201, 167, 0.4);
      }
      
      &:active { transform: translateY(0); }
      
      &:disabled { opacity: 0.6; cursor: not-allowed; }
    }
  }
}

.editor-body {
  flex: 1;
  overflow: hidden; /* 内部滚动 */
  padding: 0;
  padding: 20px;
  display: flex;
  justify-content: center;
}

.content-wrapper {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  overflow: hidden;
}

.step-component {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}
</style>