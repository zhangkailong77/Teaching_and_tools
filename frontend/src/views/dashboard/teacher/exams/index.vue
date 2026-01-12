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
      <div class="content-tabs">
        <el-tabs v-model="activeTab" class="custom-tabs">
          <el-tab-pane label="试卷管理" name="paper">
            <div class="placeholder-box">
              <img src="https://cdni.iconscout.com/illustration/premium/thumb/exam-paper-4438833-3718501.png" width="150"/>
              <p>试卷组装功能即将上线（阶段二）...</p>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="题库资源" name="bank">
            <!-- 引入题库组件 -->
            <QuestionBank v-if="activeTab === 'bank'" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TeacherSidebar from '@/components/TeacherSidebar.vue'
import QuestionBank from './components/QuestionBank.vue'

// 默认先展示题库，方便调试
const activeTab = ref('bank')
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
</style>