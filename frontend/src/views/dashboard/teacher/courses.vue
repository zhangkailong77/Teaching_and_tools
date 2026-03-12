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
          :class="{ 'preview': course.is_locked }"
        >
          <!-- 封面图 -->
          <div class="card-cover">
            <img :src="getImgUrl(course.cover) || defaultCover" alt="cover" />

          </div>

          <!-- 内容 -->
          <div class="card-body">
            <h4>{{ course.name }}</h4>
            <p class="intro" :title="course.intro">{{ course.intro || '暂无简介' }}</p>

            <div class="meta">
              <!-- 状态标签 -->
              <span v-if="!course.is_locked" class="status-tag active">✅ 已授权</span>
              <span v-else class="status-tag preview">未授权，可预览</span>
            </div>
          </div>

          <!-- 底部按钮 -->
          <div class="card-footer">
            <button v-if="!course.is_locked" class="btn-view" @click="router.push('/dashboard/teacher/courses/' + course.public_id)">
              <span>查看详情</span>
            </button>
            <button v-else class="btn-preview" @click="router.push('/dashboard/teacher/courses/' + course.public_id)">
              <span>预览课程</span>
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'; 
import TeacherSidebar from '@/components/TeacherSidebar.vue';
import { getMyCourses, type CourseItem } from '@/api/content';
import { getImgUrl } from '@/utils/index'; 

const router = useRouter();
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
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 30px rgba(0,0,0,0.08);
      border-color: $primary-color;
    }

    /* 预览状态样式 */
    &.preview {
      /* 默认无边框，悬停时显示 */
      border-color: transparent;

      &:hover {
        border-color: #1565c0;
      }
    }

    .card-cover {
      height: 160px;
      position: relative;
      background: #eee;

      img { width: 100%; height: 100%; object-fit: cover; }
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
          &.preview { background: #e3f2fd; color: #1565c0; }
        }
      }
    }

    .card-footer {
      padding: 15px 20px;
      border-top: 1px solid #f5f5f5;
      background: #fafafa;
      text-align: center;

      button { width: 100%; padding: 8px 0; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; }
      .btn-view { background: white; border: 1px solid $primary-color; color: $primary-color; &:hover { background: $primary-color; color: white; } }
      .btn-preview { background: white; border: 1px solid #1565c0; color: #1565c0; &:hover { background: #1565c0; color: white; } }
    }
  }
}
</style>