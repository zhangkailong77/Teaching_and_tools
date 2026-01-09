<!-- src/components/TeacherSidebar.vue -->
<template>
  <aside class="sidebar">
    <div class="logo-area">
      <img src="@/assets/logo.png" alt="Logo" class="logo-img" />
    </div>

    <div class="menu-group">
      <div class="menu-title">教学管理</div>
      
      <!-- router-link 会自动给当前路由加上 active 类，非常方便 -->
      <router-link to="/dashboard/teacher" class="menu-item" active-class="active" exact>
        <span class="icon">📚</span> 工作台
      </router-link>

      <router-link to="/dashboard/teacher/classes" class="menu-item" active-class="active">
        <span class="icon">🏫</span> 班级管理
      </router-link>

      <router-link to="/dashboard/teacher/students" class="menu-item" active-class="active">
        <span class="icon">👥</span> 学生名单
      </router-link>

      <router-link to="/dashboard/teacher/courses" class="menu-item" active-class="active">
        <span class="icon">📦</span> 课程资源
      </router-link>

      <router-link to="/dashboard/teacher/homeworks" class="menu-item" active-class="active">
        <span class="icon">✍️</span> 作业管理
        <span class="badge" v-if="userStore.pendingHomeworkCount > 0">
          {{ userStore.pendingHomeworkCount }}
        </span>
      </router-link>
      
      <a href="#" class="menu-item">
        <span class="icon">📊</span> 考试中心
      </a>
    </div>

    <div class="menu-group bottom">
      <div class="menu-title">系统设置</div>
      <a href="#" class="menu-item"><span class="icon">⚙️</span> 设置</a>
      <a href="#" class="menu-item logout" @click.prevent="handleLogout">
        <span class="icon">🚪</span> 退出登录
      </a>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import { onMounted, ref } from 'vue'; 

const router = useRouter();
const userStore = useUserStore();

onMounted(() => {
  userStore.refreshPendingCount();
});

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};
</script>

<style scoped lang="scss">
/* 侧边栏样式 */
$sidebar-width: 240px;
$primary-color: #00c9a7;
$text-dark: #2d3436;
$text-gray: #a4b0be;

.sidebar {
  width: $sidebar-width;
  background: white;
  display: flex;
  flex-direction: column;
  padding: 30px;
  border-right: 1px solid #eee;
  flex-shrink: 0; 

  .logo-area {
    display: flex; align-items: center; gap: 10px; margin-bottom: 40px;
    .logo-img { height: 40px; width: auto; max-width: 100%; object-fit: contain; }
  }

  .menu-group {
    margin-bottom: 30px;
    &.bottom { margin-top: auto; margin-bottom: 0; }
    .menu-title { font-size: 12px; color: $text-gray; margin-bottom: 15px; font-weight: 600; }
    
    .menu-item {
      display: flex; align-items: center; gap: 12px; padding: 12px 15px;
      color: $text-dark; text-decoration: none; font-size: 14px; font-weight: 500;
      border-radius: 10px; transition: all 0.3s; margin-bottom: 5px; position: relative;
      
      &:hover { background-color: rgba(0, 201, 167, 0.1); color: $primary-color; }
      
      /* active 类由 router-link 自动添加 */
      &.active { 
        background-color: rgba(0, 201, 167, 0.1); 
        color: $primary-color; 
        border-right: 3px solid $primary-color; 
      }
      
      &.logout:hover { color: #e74c3c; background: rgba(231, 76, 60, 0.1); }
      .badge { background: #e74c3c; color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px; margin-left: auto; }
    }
  }
}
</style>