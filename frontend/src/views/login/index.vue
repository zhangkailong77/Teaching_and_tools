<template>
  <div class="page-container">
    <!-- 1. 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-links">
        <a href="#">首页</a>
        <a href="#">关于</a>
        <a href="#">Blog</a>
        <a href="#">Pages</a>
        <a href="#">Contact</a>
      </div>
      <div class="nav-auth">
        <div class="lang-select">中文 <span>v</span></div>
        <a href="#" :class="{ active: !isRegister }" @click.prevent="isRegister = false">登录</a>
        <!-- <a href="#" class="btn-pill" :class="{ active: isRegister }" @click.prevent="isRegister = true">注册</a> -->
      </div>
    </nav>

    <!-- 2. 主内容区 -->
    <main class="main-content">
      <!-- 左侧文字区 -->
      <div class="left-section">
        <h1>
          {{ isRegister ? 'Join Us' : 'Sign In to' }} <br />
          <span class="highlight">Teaching Platform</span>
        </h1>
        <p class="sub-text">
          {{ isRegister ? 'Already have an account?' : 'If you don’t have an account' }}
          <br />
          you can <a href="#" class="link-register" @click.prevent="isRegister = !isRegister">
            {{ isRegister ? 'Login here!' : 'Register here!' }}
          </a>
        </p>
        
        <!-- 装饰用的背景光晕 -->
        <div class="blur-blob"></div>
      </div>

      <!-- 右侧表单区 -->
      <div class="right-section">
        <form @submit.prevent="handleSubmit" class="login-card">
          
          <!-- 用户名/邮箱输入 -->
          <div class="input-wrapper">
            <input 
              v-model="formData.username" 
              type="text" 
              placeholder="Enter Username" 
              required
            />
            <span class="icon suffix">✕</span> <!-- 模拟清除按钮 -->
          </div>

          <!-- 密码输入 -->
          <div class="input-wrapper">
            <input 
              v-model="formData.password" 
              :type="showPassword ? 'text' : 'password'" 
              placeholder="Password" 
              required
            />
            <!-- 眼睛图标 (SVG) -->
            <span class="icon suffix clickable" @click="showPassword = !showPassword">
              <svg v-if="!showPassword" viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
              <svg v-else viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
            </span>
          </div>

          <div class="form-footer">
            <a href="#" class="forgot-pwd">welcome!</a>
          </div>

          <!-- 登录按钮 -->
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? 'Processing...' : (isRegister ? 'Register' : 'Sign In') }}
          </button>

          <!-- 分割线 -->
          <div class="divider">
            <span>And continue with role</span>
          </div>

          <!-- 角色选择 (替代原来的 Radio) -->
          <div class="role-buttons">
            <div 
              class="role-btn" 
              :class="{ active: formData.role === 'student' }"
              @click="formData.role = 'student'"
            >
              学生端
            </div>
            <div 
              class="role-btn" 
              :class="{ active: formData.role === 'teacher' }"
              @click="formData.role = 'teacher'"
            >
              教师端
            </div>
          </div>

        </form>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import type { UserRole } from '@/types/user';

const router = useRouter();
const userStore = useUserStore();

const isRegister = ref(false);
const showPassword = ref(false);
const loading = ref(false);

const formData = reactive({
  username: '',
  password: '',
  role: 'student' as UserRole
});

const handleSubmit = async () => {
  loading.value = true;
  try {
    if (isRegister.value) {
      await userStore.userRegister(formData);
      alert('注册成功，请登录');
      isRegister.value = false;
    } else {
      await userStore.userLogin(formData);
      if (formData.role === 'teacher') {
        router.push('/dashboard/teacher');
      } else {
        router.push('/dashboard/student');
      }
    }
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped lang="scss">
/* 引入谷歌字体 (Inter) - 这里用系统字体代替，实际项目中可在 index.html 引入 */
$font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
$primary-green: #1f856f; /* 图中的绿色 */
$bg-color: #f8f9fc;
$input-bg: #eef2f6;
$text-dark: #111827;
$text-gray: #6b7280;

.page-container {
  min-height: 100vh;
  background-color: $bg-color;
  font-family: $font-family;
  overflow: hidden; /* 防止光晕溢出 */
  position: relative;
  display: flex;
  flex-direction: column;
}

/* --- 1. Navbar --- */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 60px;
  position: relative;
  z-index: 10;

  a {
    text-decoration: none;
    color: $text-dark;
    font-size: 14px;
    margin: 0 15px;
    font-weight: 500;
    transition: color 0.3s;
    &:hover { color: $primary-green; }
  }

  .nav-auth {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .lang-select {
      font-size: 14px; 
      margin-right: 20px; 
      cursor: pointer;
      display: flex; align-items: center; gap: 4px;
      span { font-size: 10px; color: $text-gray; }
    }

    .active { color: #4b5563; font-weight: 600; }
    
    .btn-pill {
      background: white;
      padding: 8px 24px;
      border-radius: 30px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.05);
      &.active {
        box-shadow: inset 0 0 0 1px $primary-green;
        color: $primary-green;
      }
    }
  }
}

/* --- 2. Main Content --- */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10%;
  position: relative;
}

/* 左侧 */
.left-section {
  max-width: 500px;
  position: relative;
  z-index: 5;

  h1 {
    font-size: 4rem;
    line-height: 1.1;
    font-weight: 800;
    color: $text-dark;
    margin-bottom: 20px;
    
    .highlight {
      display: block;
    }
  }

  .sub-text {
    font-size: 1.1rem;
    color: $text-gray;
    line-height: 1.6;

    .link-register {
      color: #5d5fef; /* 链接那个紫色 */
      font-weight: 600;
      text-decoration: none;
    }
  }

  /* 模仿图中左下的紫色光晕 */
  .blur-blob {
    position: absolute;
    top: 50%;
    left: -50%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(169, 172, 255, 0.4) 0%, rgba(255,255,255,0) 70%);
    filter: blur(60px);
    z-index: -1;
    pointer-events: none;
  }
}

/* 右侧表单区 */
.right-section {
  width: 400px;
  position: relative;
  z-index: 10;
}

.login-card {
  /* 这里虽然没有明显的卡片背景，但为了布局对齐 */
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-wrapper {
  position: relative;
  
  input {
    width: 100%;
    padding: 18px 20px;
    padding-right: 45px; /* 给图标留位置 */
    border: none;
    border-radius: 12px;
    background-color: $input-bg;
    font-size: 14px;
    color: $text-dark;
    outline: none;
    transition: box-shadow 0.3s;

    &::placeholder {
      color: #9ca3af;
      font-weight: 500;
    }

    &:focus {
      box-shadow: 0 0 0 2px rgba(31, 133, 111, 0.2);
    }
  }

  .icon {
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    color: #9ca3af;
    display: flex;
    align-items: center;
    
    &.clickable { cursor: pointer; &:hover { color: $text-dark; } }
  }
}

.form-footer {
  text-align: right;
  .forgot-pwd {
    font-size: 12px;
    color: #9ca3af;
    text-decoration: none;
    &:hover { color: $primary-green; }
  }
}

.submit-btn {
  width: 100%;
  padding: 18px;
  background-color: $primary-green;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(31, 133, 111, 0.2);
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 25px rgba(31, 133, 111, 0.3);
  }
  &:active {
    transform: translateY(0);
  }
  &:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
}

.divider {
  text-align: center;
  position: relative;
  margin: 10px 0;
  
  &::before, &::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 30%;
    height: 1px;
    background-color: #e5e7eb;
  }
  &::before { left: 0; }
  &::after { right: 0; }

  span {
    background-color: $bg-color;
    padding: 0 10px;
    color: #9ca3af;
    font-size: 12px;
  }
}

.role-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;

  .role-btn {
    flex: 1;
    background: white;
    border: 1px solid #eee;
    padding: 12px;
    text-align: center;
    border-radius: 10px;
    cursor: pointer;
    font-size: 14px;
    color: $text-dark;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    transition: all 0.3s;

    &:hover {
      border-color: $primary-green;
      color: $primary-green;
    }

    &.active {
      background-color: $primary-green;
      color: white;
      border-color: $primary-green;
      box-shadow: 0 5px 15px rgba(31, 133, 111, 0.2);
    }
    
    &.disabled {
      opacity: 0.5;
      cursor: not-allowed;
      &:hover { border-color: #eee; color: $text-dark; }
    }
  }
}

/* 移动端适配 */
@media (max-width: 900px) {
  .main-content {
    flex-direction: column;
    justify-content: center;
    gap: 40px;
    text-align: center;
  }
  
  .navbar { padding: 20px; .nav-links { display: none; } }
  
  .left-section h1 { font-size: 2.5rem; }
  
  .right-section { width: 100%; max-width: 400px; }
}
</style>