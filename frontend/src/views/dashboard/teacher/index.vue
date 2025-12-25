<template>
  <div class="dashboard-container">
    
    <!-- 1. 左侧 Sidebar (教师版) -->
    <aside class="sidebar">
      <div class="logo-area">
        <div class="logo-icon">T</div> <!-- T 代表 Teacher -->
        <span class="logo-text">TEACHER</span>
      </div>

      <div class="menu-group">
        <div class="menu-title">教学管理</div>
        <a href="#" class="menu-item active">
          <span class="icon">📚</span> 课程管理
        </a>
        <a href="#" class="menu-item">
          <span class="icon">👥</span> 学生名单
        </a>
        <a href="#" class="menu-item">
          <span class="icon">✍️</span> 作业批改
          <span class="badge">12</span> <!-- 待办红点 -->
        </a>
        <a href="#" class="menu-item">
          <span class="icon">📊</span> 成绩统计
        </a>
      </div>

      <div class="menu-group bottom">
        <div class="menu-title">系统设置</div>
        <a href="#" class="menu-item">
          <span class="icon">⚙️</span> 设置
        </a>
        <a href="#" class="menu-item logout" @click.prevent="handleLogout">
          <span class="icon">🚪</span> 退出登录
        </a>
      </div>
    </aside>

    <!-- 2. 中间主内容区 -->
    <main class="main-content">
      <header class="top-bar">
        <div class="welcome-text">
          <h2>工作台</h2>
          <p>管理您的课程内容与教学进度</p>
        </div>
        <!-- 教师特有的核心操作 -->
        <button class="create-btn" @click="handleCreateClass">
          + 创建新课程
        </button>
      </header>

      <!-- 数据概览卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="icon-box purple">👨‍🎓</div>
          <div class="info">
            <div class="num">128</div>
            <div class="label">学生总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="icon-box blue">📘</div>
          <div class="info">
            <div class="num">4</div>
            <div class="label">执教课程</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="icon-box orange">⚡</div>
          <div class="info">
            <div class="num">12</div>
            <div class="label">待批改作业</div>
          </div>
        </div>
      </div>

      <!-- 执教课程列表 -->
      <div class="section-title">
        <h3>我管理的课程</h3>
        <div class="filter-tabs">
          <span class="active">进行中</span>
          <span>已结课</span>
        </div>
      </div>

      <div class="course-list">
        <!-- 课程卡片 -->
        <div class="course-item" v-for="course in courses" :key="course.id">
          <div class="course-img" :style="{ background: course.color }">
            {{ course.category }}
          </div>
          <div class="course-info">
            <h4>{{ course.name }}</h4>
            <div class="meta">
              <span>👥 {{ course.students }} 学生</span>
              <span>📅 {{ course.date }}</span>
            </div>
          </div>
          <div class="course-actions">
            <button class="btn-outline">课件</button>
            <button class="btn-outline">作业</button>
            <button class="btn-primary">进入班级</button>
          </div>
        </div>
      </div>

    </main>

    <!-- 3. 右侧个人中心 -->
    <aside class="right-panel">
      <div class="header-tools">
        <span class="tool-icon">🔔</span>
      </div>

      <div class="profile-summary">
        <div class="avatar-large">
          <!-- 换个头像风格区分老师 -->
          <img src="https://api.dicebear.com/7.x/miniavs/svg?seed=Teacher1" alt="avatar" />
        </div>
        <!-- 动态显示老师名字 -->
        <h3>{{ userStore.userInfo?.username || 'Teacher' }}</h3>
        <p class="role-badge">高级讲师</p>
      </div>

      <div class="schedule-section">
        <div class="rec-header">
          <h4>近期日程</h4>
        </div>
        <div class="schedule-list">
          <div class="schedule-item">
            <div class="date-box">
              <span class="day">25</span>
              <span class="month">Dec</span>
            </div>
            <div class="s-info">
              <div class="title">ComfyUI 直播课</div>
              <div class="time">19:30 - 21:00</div>
            </div>
          </div>
          <div class="schedule-item">
            <div class="date-box">
              <span class="day">26</span>
              <span class="month">Dec</span>
            </div>
            <div class="s-info">
              <div class="title">Python 作业截止</div>
              <div class="time">23:59</div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';

const router = useRouter();
const userStore = useUserStore();

// 模拟教师管理的课程数据
const courses = ref([
  { id: 1, name: 'ComfyUI 基础入门 (2025春)', category: 'AI绘图', students: 45, date: 'Created Dec 01', color: '#6c5ce7' },
  { id: 2, name: 'Python 全栈开发', category: 'Backend', students: 83, date: 'Created Nov 20', color: '#0984e3' },
]);

onMounted(() => {
  userStore.fetchUserInfo();
});

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};

const handleCreateClass = () => {
  alert('功能开发中：将弹出创建课程的表单');
};
</script>

<style scoped lang="scss">
/* 教师端主题色：紫色系 */
$sidebar-width: 240px;
$right-panel-width: 300px;
$primary-purple: #00c9a7; 
$bg-color: #f5f6fa;
$text-dark: #2d3436;
$text-gray: #a4b0be;

.dashboard-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: $bg-color;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: $sidebar-width;
  background: white;
  display: flex; flex-direction: column; padding: 30px; border-right: 1px solid #eee;

  .logo-area {
    display: flex; align-items: center; gap: 10px; margin-bottom: 40px;
    .logo-icon { width: 32px; height: 32px; background: $primary-purple; color: white; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; }
    .logo-text { font-size: 18px; font-weight: 800; color: $primary-purple; letter-spacing: 1px; }
  }

  .menu-group {
    margin-bottom: 30px;
    &.bottom { margin-top: auto; margin-bottom: 0; }
    .menu-title { font-size: 12px; color: $text-gray; margin-bottom: 15px; font-weight: 600; }
    
    .menu-item {
      display: flex; align-items: center; gap: 12px; padding: 12px 15px; color: $text-dark; text-decoration: none; font-size: 14px; font-weight: 500; border-radius: 10px; transition: all 0.3s; margin-bottom: 5px; position: relative;
      &:hover { background-color: rgba(108, 92, 231, 0.1); color: $primary-purple; }
      &.active { background-color: rgba(108, 92, 231, 0.1); color: $primary-purple; border-right: 3px solid $primary-purple; }
      &.logout:hover { color: #e74c3c; background: rgba(231, 76, 60, 0.1); }
      
      .badge { background: #e74c3c; color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px; margin-left: auto; }
    }
  }
}

/* Main Content */
.main-content {
  flex: 1; padding: 30px 40px; overflow-y: auto; display: flex; flex-direction: column; gap: 30px;

  .top-bar {
    display: flex; justify-content: space-between; align-items: center;
    .welcome-text h2 { font-size: 24px; color: $text-dark; margin-bottom: 5px; }
    .welcome-text p { font-size: 14px; color: $text-gray; }
    .create-btn { background: $primary-purple; color: white; border: none; padding: 12px 24px; border-radius: 30px; cursor: pointer; font-weight: 600; box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3); transition: transform 0.2s; &:hover { transform: translateY(-2px); } }
  }

  /* 统计卡片 */
  .stats-row {
    display: flex; gap: 20px;
    .stat-card {
      flex: 1; background: white; padding: 20px; border-radius: 15px; display: flex; align-items: center; gap: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.02);
      .icon-box { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; 
        &.purple { background: #f3e5f5; } &.blue { background: #e3f2fd; } &.orange { background: #fff3e0; }
      }
      .info { .num { font-size: 24px; font-weight: bold; color: $text-dark; } .label { font-size: 13px; color: $text-gray; } }
    }
  }

  /* 课程列表 */
  .section-title {
    display: flex; justify-content: space-between; align-items: center; margin-top: 10px;
    h3 { font-size: 18px; color: $text-dark; }
    .filter-tabs {
      background: #e0e0e0; padding: 4px; border-radius: 20px; display: flex;
      span { padding: 6px 16px; font-size: 12px; cursor: pointer; border-radius: 16px; color: #666; &.active { background: white; color: $text-dark; font-weight: 600; box-shadow: 0 2px 5px rgba(0,0,0,0.1); } }
    }
  }

  .course-list {
    display: flex; flex-direction: column; gap: 15px;
    .course-item {
      background: white; padding: 20px; border-radius: 15px; display: flex; align-items: center; gap: 20px; transition: transform 0.2s;
      &:hover { transform: translateX(5px); box-shadow: 0 5px 20px rgba(0,0,0,0.03); }
      
      .course-img { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px; text-transform: uppercase; }
      
      .course-info {
        flex: 1;
        h4 { font-size: 16px; color: $text-dark; margin-bottom: 8px; }
        .meta { display: flex; gap: 15px; font-size: 12px; color: $text-gray; }
      }

      .course-actions {
        display: flex; gap: 10px;
        button { padding: 8px 16px; border-radius: 8px; font-size: 13px; cursor: pointer; font-weight: 500; }
        .btn-outline { background: transparent; border: 1px solid #eee; color: $text-dark; &:hover { border-color: $primary-purple; color: $primary-purple; } }
        .btn-primary { background: $primary-purple; color: white; border: none; &:hover { background: darken($primary-purple, 10%); } }
      }
    }
  }
}

/* Right Panel */
.right-panel {
  width: $right-panel-width; background: white; padding: 30px; display: flex; flex-direction: column; gap: 30px; border-left: 1px solid #eee;
  .header-tools { text-align: right; color: $text-gray; }
  .profile-summary {
    text-align: center;
    .avatar-large img { width: 80px; height: 80px; border-radius: 50%; border: 4px solid #f3e5f5; }
    h3 { font-size: 18px; margin: 10px 0 5px; }
    .role-badge { display: inline-block; background: $primary-purple; color: white; padding: 4px 12px; border-radius: 12px; font-size: 10px; }
  }
  .schedule-section {
    .rec-header h4 { font-size: 14px; margin-bottom: 15px; }
    .schedule-list {
      display: flex; flex-direction: column; gap: 15px;
      .schedule-item {
        display: flex; gap: 15px; align-items: center;
        .date-box { background: #f5f6fa; padding: 8px 12px; border-radius: 10px; text-align: center; .day { display: block; font-weight: bold; font-size: 16px; } .month { font-size: 10px; color: $text-gray; } }
        .s-info { .title { font-size: 13px; font-weight: 600; margin-bottom: 4px; } .time { font-size: 11px; color: $text-gray; } }
      }
    }
  }
}
</style>