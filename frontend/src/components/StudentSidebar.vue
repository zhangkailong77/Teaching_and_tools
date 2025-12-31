<template>
  <aside class="sidebar">
    <div class="logo-area">
      <!-- 使用全局 Logo -->
      <img src="@/assets/logo.png" alt="Logo" class="logo-img" />
    </div>

    <div class="menu-group">
      <div class="menu-title">工作台</div>
      
      <!-- 1. 课程中心 (主页) -->
      <router-link to="/dashboard/student" class="menu-item" active-class="active" exact>
        <span class="icon">🏠</span> 课程中心
      </router-link>

      <!-- 后续功能预留链接 -->
      <a href="#" class="menu-item">
        <span class="icon">🔔</span> 消息通知
      </a>
      <a href="#" class="menu-item">
        <span class="icon">💻</span> 我的实训
      </a>
      <a href="#" class="menu-item">
        <span class="icon">📝</span> 作业任务
      </a>
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
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import request from '@/utils/request';

const router = useRouter();
const userStore = useUserStore();

// 退出登录逻辑 (复用之前写的，包含关闭实训环境)
const handleLogout = async () => {
  try {
    // 尝试关闭实训环境 (如果有)
    await request.post('/practice/stop-practice');
  } catch (error) {
    console.error('环境关闭失败或无运行环境');
  }
  userStore.logout();
  router.push('/login');
};
</script>

<style scoped lang="scss">
/* 这里的样式复用之前的，主色调保持青绿色 */
$sidebar-width: 240px;
$primary-color: #00c9a7; /* 学生端主色调 */
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
      display: flex; align-items: center; gap: 12px;
      padding: 12px 15px;
      color: $text-dark; text-decoration: none; font-size: 14px; font-weight: 500;
      border-radius: 10px; transition: all 0.3s;
      margin-bottom: 5px;

      &:hover { background-color: rgba(0, 201, 167, 0.1); color: $primary-color; }
      
      /* 路由激活样式 */
      &.active { 
        background-color: rgba(0, 201, 167, 0.1); 
        color: $primary-color; 
        border-right: 3px solid $primary-color; 
      }
      
      &.logout:hover { color: #e74c3c; background: rgba(231, 76, 60, 0.1); }
    }
  }
}
</style>