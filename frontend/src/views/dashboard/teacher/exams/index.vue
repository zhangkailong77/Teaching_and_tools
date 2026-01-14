<template>
  <div class="exam-container">
    <TeacherSidebar />
    
    <main class="main-content">
      <header class="page-header">
        <div class="header-text">
          <h2>考试中心</h2>
          <p>管理试题资源，组织在线考试与测评</p>
        </div>
      </header>

      <!-- 核心 Tab 区域 -->
      <div v-if="!isEditorMode && !isResultMode" class="content-tabs">
        <el-tabs v-model="activeTab" class="custom-tabs">
          <el-tab-pane label="试卷管理" name="paper">
            <PaperList 
              v-if="activeTab === 'paper'" 
              ref="paperListRef"
              @create="switchToEditor(null)" 
              @edit="switchToEditor" 
              @view-results="handleViewResults"
            />
          </el-tab-pane>
          
          <el-tab-pane label="题库资源" name="bank">
            <QuestionBank v-if="activeTab === 'bank'" />
          </el-tab-pane>
        </el-tabs>
      </div>

      <div v-else-if="isEditorMode" class="editor-container">
        <PaperEditor :initial-data="currentExamData" @back="handleBack" @success="handleBack" />
      </div>

      <div v-else-if="isResultMode && !isGradingMode" class="result-container">
        <ExamResultView :exam-id="currentExamId" @back="handleBack" @go-grade="handleGoGrade" />
      </div>

      <div v-else-if="isGradingMode" class="grading-wrapper">
        <GradingPaper 
          :record-id="currentRecordId" 
          :exam-id="currentExamId" 
          @back="handleBackFromGrading(false)" 
          @success="handleBackFromGrading(true)"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TeacherSidebar from '@/components/TeacherSidebar.vue'
import QuestionBank from './components/QuestionBank.vue'
import PaperList from './components/PaperList.vue'
import PaperEditor from './components/PaperEditor.vue' 
import ExamResultView from './components/ExamResultView.vue'
import GradingPaper from './components/GradingPaper.vue'

// 默认先展示题库，方便调试
const activeTab = ref('paper')
const paperListRef = ref()
const isEditorMode = ref(false)
const currentEditExam = ref<any>(null)
const currentExamData = ref<any>(null)
const isResultMode = ref(false)
const currentExamId = ref<number | null>(null)


const isGradingMode = ref(false) // ✅ 新增状态
const currentRecordId = ref<number | null>(null) // ✅ 新增记录ID

// 处理进入批阅
const handleGoGrade = (recordId: number) => {
  currentRecordId.value = recordId
  isGradingMode.value = true
}

// 处理批阅完成/返回
const handleBackFromGrading = (refresh = false) => {
  isGradingMode.value = false
  currentRecordId.value = null
  // 如果提交了成绩，需要刷新 ExamResultView 的数据
  // 这里可以通过 provide/inject 或者 ref 调用子组件方法，
  // 或者简单点：ExamResultView 本身就有 mounted fetch，切回去时会自动刷新吗？不会。
  // 所以我们可以在 handleBack 时触发刷新。
}


const handleViewResults = (id: number) => {
  console.log('父组件收到查看成绩请求，ID:', id)
  currentExamId.value = id
  isResultMode.value = true
}

const handleBack = () => {
  isEditorMode.value = false
  isResultMode.value = false
  currentExamId.value = null
}

const handleEdit = (exam: any) => {
  currentEditExam.value = exam // 保存要编辑的对象
  isEditorMode.value = true
}

const switchToEditor = (exam: any = null) => {
  currentExamData.value = exam // 如果是 null 则是新建，如果有数据则是编辑
  isEditorMode.value = true
}

const handleSuccess = () => {
  isEditorMode.value = false
  currentExamData.value = null // 清空数据
  setTimeout(() => {
    paperListRef.value?.fetchData()
  }, 100)
}
</script>

<style scoped lang="scss">
$primary-color: #00c9a7;
$bg-color: #f5f6fa;

.exam-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: $bg-color;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}

.main-content {
  flex: 1;
  padding: 30px 40px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 20px;
  h2 { font-size: 24px; color: #2d3436; margin: 0 0 5px; }
  p { color: #a4b0be; font-size: 14px; margin: 0; }
}

/* Tab 样式美化 */
.content-tabs {
  background: white;
  border-radius: 16px;
  padding: 20px;
  flex: 1; /* 让它占据剩余空间 */
  overflow-y: auto; /* 当内容超出时可以滚动 */
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background-color: #f0f0f0;
  }
  
  :deep(.el-tabs__item) {
    font-size: 15px;
    font-weight: 500;
    color: #666;
    &.is-active {
      color: $primary-color;
      font-weight: bold;
    }
  }
  
  :deep(.el-tabs__active-bar) {
    background-color: $primary-color;
    height: 3px;
    border-radius: 3px;
  }
}

.placeholder-box {
  text-align: center;
  padding: 100px 0;
  color: #999;
  img { opacity: 0.6; margin-bottom: 20px; }
}

.list-mode-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* ✅ 编辑器模式容器：占满全屏，抵消 main-content 的 padding */
.editor-mode-container {
  height: calc(100% + 60px); /* 补偿上下 padding (30px * 2) */
  width: calc(100% + 80px);  /* 补偿左右 padding (40px * 2) */
  margin: -30px -40px;       /* 负 margin 抵消 padding */
  position: relative;
  z-index: 10;
}

.grading-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative; /* 确保 z-index 生效 */
}
</style>