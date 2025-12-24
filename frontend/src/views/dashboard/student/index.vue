<template>
  <div class="dashboard-container">
    
    <!-- 1. 左侧侧边栏 (Sidebar) -->
    <aside class="sidebar">
      <div class="logo-area">
        <div class="logo-icon">C</div>
        <span class="logo-text">COURSUE</span>
      </div>

      <div class="menu-group">
        <div class="menu-title">工作台</div>
        <a href="#" class="menu-item active">
          <span class="icon">🏠</span> 课程中心
        </a>
        <a href="#" class="menu-item">
          <span class="icon">🔔</span> 消息通知
        </a>
        <a href="#" class="menu-item">
          <span class="icon">💻</span> 我的实训
        </a>
        <a href="#" class="menu-item">
          <span class="icon">📝</span> 作业任务
        </a>
        <!-- 新增：我的班级 -->
        <a href="#" class="menu-item">
          <span class="icon">👥</span> 我的班级
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

    <!-- 2. 中间主内容区 (Main Content) -->
    <main class="main-content">
      <!-- 顶部搜索栏 -->
      <header class="top-bar">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" placeholder="搜索课程..." />
        </div>
      </header>

      <!-- 实训入口 Banner (对应需求：云端实训台入口) -->
      <div class="banner-card">
        <div class="banner-text">
          <div class="tag">ONLINE COURSE</div>
          <h2>真实产业项目驱动教学<br>打造“学练用”一体化实战闭环</h2>
          <!-- 跳转系统 B 的按钮 -->
          <button class="action-btn" @click="openSystemB">
            启动 ComfyUI 环境 <span class="arrow">▶</span>
          </button>
        </div>
        <!-- 装饰背景圆圈 -->
        <div class="circle c1"></div>
        <div class="circle c2"></div>
      </div>

      <!-- 统计小卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="icon-box green">🔔</div>
          <div class="info">
            <div class="num">2/8 已学习</div>
            <div class="label">风格重绘</div>
          </div>
          <span class="more">⋮</span>
        </div>
        <div class="stat-card">
          <div class="icon-box blue">💻</div>
          <div class="info">
            <div class="num">2/8 已学习</div>
            <div class="label">产品迁移</div>
          </div>
          <span class="more">⋮</span>
        </div>
        <div class="stat-card">
          <div class="icon-box purple">🎨</div>
          <div class="info">
            <div class="num">2/8 已学习</div>
            <div class="label">图片扩展</div>
          </div>
          <span class="more">⋮</span>
        </div>
      </div>

      <!-- 我的课程列表 (对应需求：展示已加入的班级列表，显示学习进度百分比) -->
      <div class="section-title">
        <h3>继续学习 (我的课程)</h3>
        <div class="nav-arrows">
          <button>&lt;</button>
          <button>&gt;</button>
        </div>
      </div>

      <div class="course-grid">
        <!-- 课程卡片 v-for -->
        <div class="course-card" v-for="course in courses" :key="course.id">
          <div class="card-cover" :style="{ backgroundColor: course.color }">
            <span class="fav-icon">❤</span>
            <div class="course-tag">FRONTEND</div>
          </div>
          <div class="card-body">
            <h4>{{ course.name }}</h4>
            
            <!-- 进度条 -->
            <div class="progress-wrapper">
              <div class="progress-bg">
                <div class="progress-fill" :style="{ width: course.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ course.progress }}%</span>
            </div>

            <div class="teacher-info">
              <div class="avatar">{{ course.teacher[0] }}</div>
              <div class="details">
                <div class="name">{{ course.teacher }}</div>
                <div class="role">Lecturer</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>

    <!-- 3. 右侧个人中心 (Right Panel) -->
    <aside class="right-panel">
      <div class="header-tools">
        <span class="tool-icon">⋮</span>
      </div>

      <div class="profile-summary">
        <div class="avatar-large">
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="avatar" />
          <div class="status-ring"></div>
        </div>
        <h3>Good Morning, {{ userStore.userInfo?.username || 'Student' }}</h3>
        <p>坚持学习，达成目标</p>
        
        <div class="action-buttons">
          <button class="btn-circle">🔔</button>
          <button class="btn-circle">📩</button>
          <button class="btn-circle">📅</button>
        </div>
      </div>

      <!-- 简单的活跃度图表装饰 -->
      <div class="chart-placeholder">
        <div class="bar" style="height: 40%"></div>
        <div class="bar" style="height: 60%"></div>
        <div class="bar" style="height: 80%"></div>
        <div class="bar" style="height: 50%"></div>
        <div class="bar" style="height: 70%"></div>
      </div>

      <div class="recommend-section">
        <div class="rec-header">
          <h4>推荐导师</h4>
          <button class="add-btn">+</button>
        </div>
        <div class="mentor-list">
          <div class="mentor-item">
            <div class="m-avatar">P</div>
            <div class="m-info">
              <div class="name">Prashant Kumar</div>
              <div class="job">Software Developer</div>
            </div>
            <button class="follow-btn">Follow</button>
          </div>
          <!-- 更多导师... -->
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

// 模拟课程数据
const courses = ref([
  { id: 1, name: 'ComfyUI 基础入门', teacher: 'Prashant Singh', progress: 35, color: '#333' },
  { id: 2, name: 'Stable Diffusion 进阶', teacher: 'Ravi Kumar', progress: 78, color: '#f1c40f' },
  { id: 3, name: 'Python 自动化脚本', teacher: 'Alice Dev', progress: 12, color: '#3498db' }
]);

onMounted(() => {
  // 页面加载时获取用户信息
  userStore.fetchUserInfo();
});

// 退出登录
const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};

// 打开系统 B (实训台)
const openSystemB = () => {
  // 这里可以写 window.open('http://system-b-url.com')
  alert('正在跳转至 ComfyUI 云端实训环境...');
};
</script>

<style scoped lang="scss">
/* 全局布局变量 */
$sidebar-width: 240px;
$right-panel-width: 300px;
$primary-color: #00c9a7; /* 截图中的那个青绿色 */
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

/* --- 1. 左侧 Sidebar --- */
.sidebar {
  width: $sidebar-width;
  background: white;
  display: flex;
  flex-direction: column;
  padding: 30px;
  border-right: 1px solid #eee;

  .logo-area {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 40px;
    .logo-icon {
      width: 32px; height: 32px; background: $primary-color; color: white;
      border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;
    }
    .logo-text { font-size: 18px; font-weight: 800; color: $primary-color; letter-spacing: 1px; }
  }

  .menu-group {
    margin-bottom: 30px;
    &.bottom { margin-top: auto; margin-bottom: 0; }

    .menu-title { font-size: 12px; color: $text-gray; margin-bottom: 15px; font-weight: 600; }
    
    .menu-item {
      display: flex; align-items: center; gap: 12px;
      padding: 12px 15px;
      color: $text-dark; text-decoration: none; font-size: 14px; font-weight: 500;
      border-radius: 10px; transition: all 0.3s;
      margin-bottom: 5px;

      &:hover { background-color: rgba(0, 201, 167, 0.1); color: $primary-color; }
      &.active { background-color: rgba(0, 201, 167, 0.1); color: $primary-color; border-right: 3px solid $primary-color; }
      &.logout:hover { color: #e74c3c; background: rgba(231, 76, 60, 0.1); }
    }
  }
}

/* --- 2. 中间 Main Content --- */
.main-content {
  flex: 1;
  padding: 30px 40px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 30px;

  /* 搜索栏 */
  .top-bar {
    .search-box {
      background: white; padding: 12px 20px; border-radius: 30px; display: flex; align-items: center; gap: 10px; width: 400px;
      input { border: none; outline: none; width: 100%; font-size: 14px; }
      .search-icon { color: $text-gray; }
    }
  }

  /* Banner */
  .banner-card {
    background: linear-gradient(135deg, #00c9a7 0%, #00b894 100%);
    border-radius: 20px; padding: 40px; position: relative; overflow: hidden; color: white;
    box-shadow: 0 10px 20px rgba(0, 201, 167, 0.2);

    .banner-text {
      position: relative; z-index: 2;
      .tag { font-size: 10px; background: rgba(255,255,255,0.2); display: inline-block; padding: 4px 10px; border-radius: 10px; margin-bottom: 10px; }
      h2 { font-size: 24px; margin-bottom: 20px; line-height: 1.4; }
      .action-btn {
        background: #2d3436; color: white; border: none; padding: 10px 24px; border-radius: 30px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 10px; transition: transform 0.2s;
        &:hover { transform: scale(1.05); }
        .arrow { background: white; color: #2d3436; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; }
      }
    }
    /* 装饰圆圈 */
    .circle { position: absolute; border-radius: 50%; background: rgba(255,255,255,0.1); }
    .c1 { width: 200px; height: 200px; right: -50px; top: -50px; }
    .c2 { width: 100px; height: 100px; right: 100px; bottom: -20px; }
  }

  /* 统计卡片行 */
  .stats-row {
    display: flex; gap: 20px;
    .stat-card {
      flex: 1; background: white; padding: 15px; border-radius: 15px; display: flex; align-items: center; gap: 15px;
      .icon-box {
        width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
        &.green { background: #e3f9f5; color: $primary-color; }
        &.blue { background: #e3f2fd; color: #2196f3; }
        &.purple { background: #f3e5f5; color: #9c27b0; }
      }
      .info {
        flex: 1;
        .num { font-size: 12px; color: $text-gray; margin-bottom: 4px; }
        .label { font-weight: bold; font-size: 14px; color: $text-dark; }
      }
      .more { color: $text-gray; cursor: pointer; }
    }
  }

  /* 课程列表 */
  .section-title {
    display: flex; justify-content: space-between; align-items: center;
    h3 { font-size: 18px; color: $text-dark; }
    .nav-arrows {
      display: flex; gap: 10px;
      button { width: 30px; height: 30px; border-radius: 50%; border: 1px solid #ddd; background: white; cursor: pointer; color: $text-gray; &:hover { border-color: $text-dark; color: $text-dark; } }
    }
  }

  .course-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;
    
    .course-card {
      background: white; border-radius: 15px; overflow: hidden; transition: transform 0.3s;
      &:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }

      .card-cover {
        height: 120px; padding: 15px; position: relative; color: white; display: flex; flex-direction: column; justify-content: space-between;
        .fav-icon { align-self: flex-end; cursor: pointer; }
        .course-tag { font-size: 10px; background: rgba(0,0,0,0.3); padding: 4px 8px; border-radius: 4px; align-self: flex-start; }
      }

      .card-body {
        padding: 20px;
        h4 { margin: 0 0 15px 0; font-size: 16px; color: $text-dark; }
        
        .progress-wrapper {
          margin-bottom: 20px; display: flex; align-items: center; gap: 10px;
          .progress-bg { flex: 1; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }
          .progress-fill { height: 100%; background: $primary-color; border-radius: 3px; }
          .progress-text { font-size: 12px; color: $text-gray; }
        }

        .teacher-info {
          display: flex; align-items: center; gap: 10px;
          .avatar { width: 30px; height: 30px; border-radius: 50%; background: #eee; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #666; }
          .details {
            .name { font-size: 12px; font-weight: 600; color: $text-dark; }
            .role { font-size: 10px; color: $text-gray; }
          }
        }
      }
    }
  }
}

/* --- 3. 右侧 Right Panel --- */
.right-panel {
  width: $right-panel-width;
  background: white;
  padding: 30px;
  display: flex; flex-direction: column; gap: 30px;
  border-left: 1px solid #eee;

  .header-tools { text-align: right; .tool-icon { font-size: 20px; cursor: pointer; } }

  .profile-summary {
    text-align: center;
    .avatar-large {
      width: 80px; height: 80px; margin: 0 auto 15px; position: relative;
      img { width: 100%; height: 100%; border-radius: 50%; }
      .status-ring { position: absolute; inset: -4px; border: 2px solid $primary-color; border-radius: 50%; border-bottom-color: transparent; transform: rotate(-45deg); }
    }
    h3 { font-size: 16px; margin-bottom: 5px; color: $text-dark; }
    p { font-size: 12px; color: $text-gray; margin-bottom: 20px; }
    .action-buttons {
      display: flex; justify-content: center; gap: 15px;
      .btn-circle { width: 40px; height: 40px; border-radius: 50%; border: 1px solid #eee; background: white; cursor: pointer; transition: all 0.2s; &:hover { background: $primary-color; color: white; border-color: $primary-color; } }
    }
  }

  /* 柱状图装饰 */
  .chart-placeholder {
    height: 100px; display: flex; align-items: flex-end; justify-content: space-between; padding: 0 20px;
    .bar { width: 8px; background: #e0e0e0; border-radius: 4px 4px 0 0; &.active { background: #9c27b0; } }
    .bar:nth-child(2) { background: #e3f2fd; }
    .bar:nth-child(3) { background: #ce93d8; }
    .bar:nth-child(4) { background: #9c27b0; } /* 模拟高亮 */
  }

  .recommend-section {
    .rec-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; h4 { font-size: 14px; } .add-btn { border: none; background: white; font-size: 20px; cursor: pointer; } }
    .mentor-list {
      display: flex; flex-direction: column; gap: 15px;
      .mentor-item {
        display: flex; align-items: center; gap: 10px;
        .m-avatar { width: 36px; height: 36px; border-radius: 50%; background: #34495e; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; }
        .m-info { flex: 1; .name { font-size: 12px; font-weight: 600; } .job { font-size: 10px; color: $text-gray; } }
        .follow-btn { border: none; background: $primary-color; color: white; padding: 4px 10px; border-radius: 10px; font-size: 10px; cursor: pointer; }
      }
    }
  }
}
</style>