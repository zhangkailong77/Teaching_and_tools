<template>
  <div class="dashboard-container">
    
    <!-- 左侧 Sidebar (保持统一) -->
    <TeacherSidebar />

    <!-- 主内容区 -->
    <main class="main-content">
      <header class="top-bar">
        <div class="breadcrumb">
          <span>教学管理</span> / <span class="current">课程资源库</span>
        </div>
        <!-- <div class="actions">
          <button class="btn-primary" @click="showModal = true">+ 新建课程包</button>
        </div> -->
      </header>

      <!-- 课程卡片网格 -->
      <div class="course-grid">
        
        <div 
          class="course-card" 
          v-for="course in courseList" 
          :key="course.id"
          :class="{ 'locked': course.is_locked }" 
        >
          <!-- 封面图 -->
          <div class="card-cover">
            <img :src="getImgUrl(course.cover) || defaultCover" alt="cover" />
            
            <!-- 🔒 锁定状态遮罩 -->
            <div v-if="course.is_locked" class="lock-overlay">
              <span class="lock-icon">🔒</span>
              <span class="lock-text">未开通</span>
            </div>
          </div>

          <!-- 内容 -->
          <div class="card-body">
            <h4>{{ course.name }}</h4>
            <p class="intro" :title="course.intro">{{ course.intro || '暂无简介' }}</p>
            
            <div class="meta">
              <!-- 状态标签 -->
              <span v-if="!course.is_locked" class="status-tag active">✅ 已授权</span>
              <span v-else class="status-tag locked">🚫 未授权</span>
            </div>
          </div>
          
          <!-- 底部按钮 (仅未锁定时可用) -->
          <div class="card-footer">
            <button v-if="!course.is_locked" class="btn-view">查看详情</button>
            <button v-else class="btn-disabled" disabled>联系管理员开通</button>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import TeacherSidebar from '@/components/TeacherSidebar.vue';
import { getMyCourses, type CourseItem } from '@/api/content';
import { getImgUrl } from '@/utils/index'; 

const courseList = ref<CourseItem[]>([]);
const defaultCover = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop';

onMounted(() => {
  fetchCourses();
});


const fetchCourses = async () => {
  try {
    const res = await getMyCourses();
    courseList.value = res;
  } catch (error) {
    console.error("加载课程资源失败", error);
  }
};
</script>

<style scoped lang="scss">
$primary-color: #00c9a7;
$bg-color: #f5f6fa;
$text-dark: #2d3436;
$text-gray: #a4b0be;

.dashboard-container { display: flex; width: 100vw; height: 100vh; background-color: $bg-color; font-family: 'Inter', sans-serif; overflow: hidden; }

.main-content { flex: 1; padding: 30px 40px; overflow-y: auto; 
  .top-bar { display: flex; align-items: center; margin-bottom: 20px;
    .breadcrumb { font-size: 14px; color: $text-gray; .current { color: $text-dark; font-weight: 600; } }
  }

  /* 网格布局 */
  .course-grid { 
    display: grid; 
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
    gap: 25px; 
    padding-bottom: 40px; 
  }

  /* === 卡片核心样式 === */
  .course-card { 
    background: white; 
    border-radius: 16px; 
    overflow: hidden; 
    box-shadow: 0 5px 20px rgba(0,0,0,0.02); 
    transition: all 0.3s; 
    border: 1px solid transparent;
    display: flex;
    flex-direction: column;

    /* 正常状态悬停 */
    &:hover:not(.locked) { 
      transform: translateY(-5px); 
      box-shadow: 0 10px 30px rgba(0,0,0,0.08); 
      border-color: $primary-color; 
    }

    /* 🔒 锁定状态样式 */
    &.locked {
      filter: grayscale(100%); /* 核心：整体变灰 */
      opacity: 0.7;            /* 稍微透明 */
      cursor: not-allowed;     /* 鼠标禁用 */
      
      .card-cover img {
        opacity: 0.5;
      }
    }

    .card-cover { 
      height: 160px; 
      position: relative; 
      background: #eee;
      
      img { width: 100%; height: 100%; object-fit: cover; }

      /* 锁图标遮罩 */
      .lock-overlay {
        position: absolute; inset: 0;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: rgba(0,0,0,0.1);
        color: #333;
        font-weight: bold;
        .lock-icon { font-size: 40px; margin-bottom: 5px; }
        .lock-text { font-size: 14px; background: rgba(255,255,255,0.8); padding: 2px 8px; border-radius: 4px; }
      }
    }

    .card-body { 
      padding: 20px; 
      flex: 1;
      h4 { font-size: 16px; color: $text-dark; margin: 0 0 8px; line-height: 1.4; height: 44px; overflow: hidden; }
      .intro { font-size: 13px; color: $text-gray; height: 40px; line-height: 1.5; overflow: hidden; margin-bottom: 15px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
      
      .meta {
        display: flex; justify-content: space-between; align-items: center;
        .status-tag { 
          font-size: 12px; padding: 2px 8px; border-radius: 4px; font-weight: 500;
          &.active { background: #e0f2f1; color: $primary-color; }
          &.locked { background: #f5f5f5; color: #999; border: 1px solid #ddd; }
        }
      }
    }

    .card-footer {
      padding: 15px 20px;
      border-top: 1px solid #f5f5f5;
      background: #fafafa;
      text-align: center;

      button { width: 100%; padding: 8px 0; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: none; }
      .btn-view { background: white; border: 1px solid $primary-color; color: $primary-color; &:hover { background: $primary-color; color: white; } }
      .btn-disabled { background: #eee; color: #aaa; cursor: not-allowed; }
    }
  }
}
</style>