<template>
  <div class="site-wrapper">
    <!-- 1. 导航栏 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="logo">
          <img src="@/assets/logo.png" alt="Logo" class="logo-img" />
        </div>
        <div class="nav-links">
          <a href="#hero" @click.prevent="scrollToSection('hero')">首页</a>
          <a href="#features" @click.prevent="scrollToSection('features')">功能</a>
          <a href="#story" @click.prevent="scrollToSection('story')">关于我们</a>
          <a href="#contact" @click.prevent="scrollToSection('contact')">联系</a>
        </div>
        <div class="nav-actions">
          <button class="lang-switcher" aria-label="Switch language">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            <span>中文</span>
            <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </button>
        </div>
      </div>
    </nav>

    <!-- 2. 英雄区 -->
    <section id="hero" class="hero-section">
      <div class="hero-grid">
        <!-- 左侧图片拼贴区 - 重构为CSS Grid布局 -->
        <div class="collage-area" aria-hidden="true">
          <!-- 左列：短 + 长 -->
          <div class="collage-column col-left">
            <div class="image-card card-1">
              <img src="@/assets/img1.png" alt="shopee" />
            </div>
            <div class="image-card card-3">
              <img src="@/assets/img3.png" alt="comfyui" />
            </div>
          </div>

          <!-- 右列：长 + 短 -->
          <div class="collage-column col-right">
            <div class="image-card card-2">
              <img src="@/assets/img4.png" alt="data" />
            </div>
            <div class="image-card card-4">
              <img src="@/assets/img2.png" alt="tiktok" />
            </div>
          </div>

          <!-- 徽章：悬浮在底部中间 -->
          <div class="stat-badge">
            <span class="num">80+</span>
            <span class="lab">Course Resources</span>
          </div>
        </div>

        <!-- 右侧内容 -->
        <div class="hero-content">
          <div class="content-wrapper">
            <!-- <div class="tag">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              Award-Winning Platform
            </div> -->
            <h1 class="main-title">
              {{ isRegister ? 'JOIN THE' : 'WELCOME TO' }} <br />
              <span class="highlight">TEACHING PLATFORM</span>
            </h1>
            <p class="hero-desc">
              探索充满激情的顶级教学体验。新鲜的教学理念、永恒的知识传承，为您打造难忘的学习之旅。
            </p>

            <!-- 登录表单卡片 -->
            <div class="login-box">
              <form @submit.prevent="handleSubmit" class="login-form">
                <div class="input-group">
                  <label for="username" class="sr-only">用户名</label>
                  <div class="input-wrapper">
                    <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                      <circle cx="12" cy="7" r="4"/>
                    </svg>
                    <input
                      id="username"
                      v-model="formData.username"
                      type="text"
                      placeholder="请输入用户名"
                      :disabled="loading"
                    />
                  </div>
                </div>

                <div class="input-group">
                  <label for="password" class="sr-only">密码</label>
                  <div class="input-wrapper">
                    <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    </svg>
                    <input
                      id="password"
                      v-model="formData.password"
                      :type="showPassword ? 'text' : 'password'"
                      placeholder="请输入密码"
                      :disabled="loading"
                    />
                    <button
                      type="button"
                      class="password-toggle"
                      @click="showPassword = !showPassword"
                      :aria-label="showPassword ? '隐藏密码' : '显示密码'"
                    >
                      <svg v-if="showPassword" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                        <line x1="1" y1="1" x2="23" y2="23"/>
                      </svg>
                      <svg v-else class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  class="btn-primary-lg"
                  :disabled="loading"
                >
                  <span v-if="!loading">
                    {{ isRegister ? '立即注册' : '立即登录' }}
                  </span>
                  <span v-else class="loading">
                    <svg class="spinner" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-dasharray="31.4 31.4"/>
                    </svg>
                    处理中...
                  </span>
                </button>
              </form>

              <!-- 角色选择器 -->
              <div class="role-selector">
                <button
                  class="role-tab"
                  :class="{ active: formData.role === 'student' }"
                  @click="formData.role = 'student'"
                  :aria-pressed="formData.role === 'student'"
                >
                  <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                    <path d="M6 12v5c3 3 9 3 12 0v-5"/>
                  </svg>
                  学生端
                </button>
                <button
                  class="role-tab"
                  :class="{ active: formData.role === 'teacher' }"
                  @click="formData.role = 'teacher'"
                  :aria-pressed="formData.role === 'teacher'"
                >
                  <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  教师端
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 3. 功能展示区 -->
    <!-- <section id="features" class="features-section">
      <div class="section-divider">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
        </svg>
      </div>
      <h2 class="section-title">平台特色</h2>
      <p class="section-subtitle">最前沿的技术，支撑最高品质的教育内容</p>

      <div class="feature-grid">
        <div
          v-for="(feature, index) in features"
          :key="index"
          class="feature-card"
          :style="{ '--delay': `${index * 0.1}s` }"
        >
          <div class="f-img">
            <img :src="feature.image" :alt="feature.title" loading="lazy" @error="handleImageError" />
          </div>
          <div class="f-info">
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.desc }}</p>
          </div>
          <div class="f-badge">Pro</div>
        </div>
      </div>

      <button class="btn-outline-lg">
        查看全部功能
        <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
    </section> -->

    <!-- 4. 关于我们区 -->
    <!-- <section id="story" class="story-section">
      <div class="story-container">
        <div class="story-visual">
          <img
            src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=800&q=80"
            alt="团队协作"
            loading="lazy"
            @error="handleImageError"
          />
          <div class="quote-card">
            <svg class="quote-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"/>
            </svg>
            <p>教育不是灌输，而是点燃火焰。我们致力于为每位教师提供最坚实的火种。</p>
            <strong>— CEO, Marco Bellini</strong>
          </div>
        </div>
        <div class="story-content">
          <div class="tag">关于我们</div>
          <h2 class="story-title">始于2008年的教育理想</h2>
          <p>
            创立于纽约市中心，La Maison 平台最初只是一个小小的愿景：通过技术打破教育的藩篱。
            在 Marco Bellini 教授的指导下，我们的实验室将最前沿的 AI 与人性化的教学法相结合。
          </p>
          <div class="stats-row">
            <div class="stat-item">
              <strong>15+</strong>
              <span>年教学经验</span>
            </div>
            <div class="stat-item">
              <strong>50K+</strong>
              <span>活跃用户</span>
            </div>
            <div class="stat-item">
              <strong>3</strong>
              <span>国际奖项</span>
            </div>
          </div>
        </div>
      </div>
    </section> -->
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

// 图片加载错误处理
const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement;
  target.style.display = 'none';
  // 可选：在这里添加默认占位图逻辑
};

const toggleMode = () => {
  isRegister.value = !isRegister.value;
};

// 平滑滚动到指定区域
const scrollToSection = (sectionId: string) => {
  const element = document.getElementById(sectionId);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

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

// 特性数据
const features = [
  {
    title: '智能课程推荐',
    desc: '基于AI算法分析学习习惯，为您量身定制最优学习路径',
    image: 'https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&w=200&q=80'
  },
  {
    title: '实时互动课堂',
    desc: '支持千人同时在线，零延迟的师生互动体验',
    image: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=200&q=80'
  },
  {
    title: '作业智能批改',
    desc: '自动批改客观题，AI辅助分析主观题得分点',
    image: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=200&q=80'
  },
  {
    title: '学习数据看板',
    desc: '可视化展示学习进度、知识掌握程度和提升建议',
    image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=200&q=80'
  }
];
</script>

<style scoped lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700;800;900&family=Noto+Serif+SC:wght@700;900&display=swap');

// 变量定义
$teal: #1f856f;
$teal-light: #2da88a;
$teal-dark: #00a58c;
$bg-cream: #f8f7f5;
$bg-hero: #f5f3ef; // hero区域稍深的米色
$black: #1a1a1a;
$gray-500: #6b7280;
$gray-400: #9ca3af;
$gray-100: #f3f4f6;
$gray-200: #e5e7eb;
$gray-300: #d1d5db;
$gray-700: #374151;
$white: #ffffff;
$border: 2px solid $black;
$shadow: 6px 6px 0px $black;
$shadow-hover: 8px 8px 0px $black;
$shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.08); // 柔和阴影

* {
  box-sizing: border-box;
}

// 图片漂浮动画
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

html {
  scroll-behavior: smooth;
}

.site-wrapper {
  background-color: $white;
  color: $black;
  font-family: 'Noto Sans SC', sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}

// 辅助类 - 屏幕阅读器
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

// 图标通用样式
.icon {
  width: 1em;
  height: 1em;
  flex-shrink: 0;
}

// 导航栏
.navbar {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  margin: 0;
  padding: 12px 40px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);

  @media (max-width: 768px) {
    padding: 12px 24px;
  }

  .nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 24px;
    gap: 16px;

    @media (max-width: 768px) {
      flex-wrap: wrap;
      padding: 12px 16px;
    }
  }

  .logo {
  display: flex;
  align-items: center;
  gap: 0px;        // 【参数：Logo图片和文字之间的间距】
  cursor: pointer;

  .logo-img {
    // 建议以高度为准，宽度设为 auto 保持比例不失真
    height: 40px;   
    width: auto;    
    object-fit: contain;
  }
  }

  .nav-links {
    display: flex;
    gap: 8px;

    @media (max-width: 768px) {
      order: 3;
      width: 100%;
      justify-content: center;
      padding-top: 12px;
      border-top: 1px solid $gray-100;
    }

    a {
      text-decoration: none;
      color: $gray-500;
      font-weight: 500;
      padding: 8px 16px;
      border-radius: 6px;
      transition: all 0.2s ease;
      white-space: nowrap;

      &:hover {
        color: $black;
        background: $gray-100;
      }
    }
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
  }

  .lang-switcher {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    color: $gray-500;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      color: $black;
      background: $gray-100;
    }

    .chevron {
      width: 14px;
      height: 14px;
    }
  }
}

// 通用按钮
.btn-primary-sm {
  background: $teal;
  color: $white;
  border: none;
  padding: 10px 20px;
  font-weight: 600;
  font-size: 0.875rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(31, 133, 111, 0.25);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  &:hover {
    background: $teal-light;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(31, 133, 111, 0.35);
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(31, 133, 111, 0.2);
  }

  &:focus-visible {
    outline: 2px solid $teal;
    outline-offset: 2px;
  }
}

.btn-primary-lg {
  width: 100%;
  background: $teal;
  color: $white;
  border: none;
  padding: 14px 20px;
  font-weight: 600;
  font-size: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 14px rgba(31, 133, 111, 0.3);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: $teal-light;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(31, 133, 111, 0.4);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(31, 133, 111, 0.25);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  &:focus-visible {
    outline: 2px solid $teal;
    outline-offset: 2px;
  }
}

.btn-outline-lg {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: $white;
  border: 1px solid $gray-200;
  padding: 14px 32px;
  font-weight: 600;
  font-size: 0.875rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
  }

  .arrow-icon {
    width: 18px;
    height: 18px;
    transition: transform 0.2s;
  }

  &:hover .arrow-icon {
    transform: translateX(4px);
  }
}

// 英雄区 - 核心优化区域
.hero-section {
  padding: 100px 80px 60px;
  min-height: 100vh;
  display: flex;
  align-items: center;
  background-color: $white;
  position: relative;
  overflow: hidden;

  // 左下角浅青色装饰
  &::before {
    content: '';
    position: absolute;
    bottom: -100px;
    left: -100px;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba($teal, 0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
  }

  @media (max-width: 1200px) {
    padding: 100px 40px 60px;
  }

  @media (max-width: 768px) {
    padding: 90px 24px 40px;

    &::before {
      width: 200px;
      height: 200px;
      bottom: -50px;
      left: -50px;
    }
  }
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center; // 改为居中对齐
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 48px;
  }
}

// 拼贴区域 - 重构为CSS Grid
.collage-area {
  display: flex;       // 改用 Flex 布局实现双列
  gap: 16px;           // 【参数1：左右两列的水平间距】
  position: relative;
  max-width: 550px;
  margin: 0 auto;
  align-items: flex-start; // 顶部对齐

  .collage-column {
    display: flex;
    flex-direction: column;
    flex: 1;           // 两列平分宽度
    gap: 16px;         // 【参数2：上下图片之间的垂直间距】
  }

  // 右列整体下移，制造参考图中的错位感
  .col-right {
    margin-top: 40px;  // 【参数3：控制左右两列的错开高度】
  }

  .image-card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    transition: transform 0.4s ease, box-shadow 0.4s ease;
    animation: float 6s ease-in-out infinite;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.5s ease;
    }

    &:hover {
      transform: translateY(-8px);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);

      img {
        transform: scale(1.05);
      }
    }
  }

  // 每张图片有不同的动画延迟
  .card-1 {
    animation-delay: 0s;
  }

  .card-2 {
    animation-delay: -1.5s;
  }

  .card-3 {
    animation-delay: -3s;
  }

  .card-4 {
    animation-delay: -4.5s;
  }

  /* --- 高度比例调节参数 (aspect-ratio) --- */

  .card-1 { aspect-ratio: 1.2 / 1; } // 左上：较扁
  .card-3 { aspect-ratio: 0.8 / 1; } // 左下：较长 (填补下方空间)

  .card-2 { aspect-ratio: 0.8 / 1; } // 右上：较长
  .card-4 { aspect-ratio: 1.3 / 1; } // 右下：较扁

  /* --- 徽章定位 --- */
  .stat-badge {
    position: absolute;
    bottom: -20px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, #1f856f 0%, #2da88a 100%);
    color: #fff;
    padding: 15px 25px;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(31, 133, 111, 0.35);
    z-index: 10;
    text-align: center;
    min-width: 150px;
    animation: badgePulse 2s ease-in-out infinite, badgeFloat 3s ease-in-out infinite;

    // 呼吸灯边框效果
    &::before {
      content: '';
      position: absolute;
      inset: -2px;
      border-radius: 14px;
      background: linear-gradient(135deg, rgba(45, 168, 138, 0.8), rgba(31, 133, 111, 0.4), rgba(45, 168, 138, 0.8));
      z-index: -1;
      animation: borderGlow 2s linear infinite;
      opacity: 0.7;
    }

    .num {
      display: block;
      font-size: 2rem;
      font-weight: 900;
      line-height: 1;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      animation: textPulse 2s ease-in-out infinite;
    }

    .lab {
      display: block;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      margin-top: 5px;
      opacity: 0.9;
      letter-spacing: 1px;
    }
  }
}

// 徽章脉冲动画
@keyframes badgePulse {
  0%, 100% {
    transform: translateX(-50%) scale(1);
    box-shadow: 0 8px 24px rgba(31, 133, 111, 0.35);
  }
  50% {
    transform: translateX(-50%) scale(1.03);
    box-shadow: 0 12px 36px rgba(31, 133, 111, 0.5);
  }
}

// 徽章漂浮动画
@keyframes badgeFloat {
  0%, 100% {
    transform: translateX(-50%) translateY(0);
  }
  50% {
    transform: translateX(-50%) translateY(-5px);
  }
}

// 边框呼吸灯效果
@keyframes borderGlow {
  0% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.4;
  }
}

// 数字脉冲效果
@keyframes textPulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.85;
  }
}

// 右侧内容区
.hero-content {
  display: flex;
  justify-content: center;
  align-items: center;
  
  .content-wrapper {
    width: 100%;
    max-width: 480px;
    display: flex;
    flex-direction: column;
    align-items: flex-end; // 桌面端右对齐
    text-align: right;

    @media (max-width: 1024px) {
      align-items: center;
      text-align: center;
    }
  }
}

.tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: $border;
  padding: 6px 14px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 24px;
  border-radius: 20px;
  background: $white;
  width: fit-content;

  .icon {
    color: $teal;
  }
}

.main-title {
  // --- 关键修改：换成 Inter 或系统默认无衬线字体 ---
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  
  font-size: clamp(3.5rem, 8vw, 4rem); 
  font-weight: 900;                    
  line-height: 0.9;                    
  margin-bottom: 20px;
  
  // --- 关键修改：应用负字间距，还原图中“挤压感” ---
  letter-spacing: -0.05em; 
  
  text-align: right;
  // --- 关键修改：颜色换成图中那种深鸦青色，质感更好 ---
  color: #111827; 

  .highlight {
    display: block;
    white-space: nowrap;
    margin-top: 10px;                  

    // 第二行也自动继承上面的无衬线字体
    color: $teal;
    font-size: clamp(1.8rem, 3vw, 2.5rem); 
    font-weight: 800;                  
    
    // --- 关键修改：第二行也要紧凑，但比第一行稍微松一点点 ---
    letter-spacing: -0.02em;               

    position: relative;
    &::after {
      content: '';
      position: absolute;
      bottom: 4px;                    
      left: 0;
      right: 0;
      height: 10px;                   
      background: rgba($teal, 0.15);
      z-index: -1;
      transform: skewX(-12deg);
    }
  }
}

.hero-desc {
  font-size: 1.1rem;
  line-height: 1.7;
  max-width: 480px;
  margin-bottom: 32px;
  color: $gray-500;
}

// 登录框 - 优化间距
.login-box {
  background: $white;
  padding: 32px;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 420px;

  @media (max-width: 640px) {
    padding: 24px;
  }
}

.login-form {
  .input-group {
    margin-bottom: 16px;
  }

  .input-wrapper {
    display: flex;
    align-items: center;
    border: 1px solid $gray-200;
    border-radius: 12px;
    background: $white;
    transition: all 0.2s;

    &:focus-within {
      border-color: $teal;
      box-shadow: 0 0 0 3px rgba($teal, 0.1);
    }
  }

  .input-icon {
    width: 20px;
    height: 20px;
    margin: 0 12px;
    color: $gray-400;
    flex-shrink: 0;
  }

  input {
    flex: 1;
    padding: 14px 14px 14px 0;
    border: none;
    background: transparent;
    font-family: inherit;
    font-size: 0.95rem;
    font-weight: 500;
    outline: none;
    min-width: 0;

    &::placeholder {
      color: $gray-400;
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }

  .password-toggle {
    padding: 8px 12px;
    background: transparent;
    border: none;
    cursor: pointer;
    color: $gray-400;
    transition: color 0.2s;
    display: flex;
    align-items: center;

    &:hover {
      color: $black;
    }

    .icon {
      width: 20px;
      height: 20px;
    }
  }
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .spinner {
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 角色选择器
.role-selector {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid $gray-100;

  @media (max-width: 480px) {
    flex-direction: column;
    gap: 8px;
  }
}

.role-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: 1px solid $gray-200;
  border-radius: 12px;
  background: $white;
  font-weight: 500;
  font-size: 0.875rem;
  color: $gray-500;
  cursor: pointer;
  transition: all 0.2s;

  .icon {
    width: 18px;
    height: 18px;
    transition: color 0.2s;
  }

  &:hover {
    border-color: $gray-300;
    color: $gray-700;
    transform: translateY(-1px);
  }

  &.active {
    background: $teal;
    border-color: $teal;
    color: $white;
    box-shadow: 0 4px 14px rgba(31, 133, 111, 0.3);

    .icon {
      color: $white;
    }
  }

  &:focus-visible {
    outline: 2px solid $teal;
    outline-offset: 2px;
  }
}

// 功能区
.features-section {
  padding: 100px 80px;
  text-align: center;
  background: $bg-cream;

  @media (max-width: 768px) {
    padding: 60px 24px;
    background: $white;
  }

  .section-divider {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    margin-bottom: 20px;
    background: $white;
    border: $border;
    border-radius: 50%;
    box-shadow: $shadow;
    transition: transform 0.2s;

    &:hover {
      transform: translateY(-2px);
    }

    svg {
      width: 28px;
      height: 28px;
      color: $teal;
    }
  }

  .section-title {
    font-family: 'Noto Serif SC', serif;
    font-size: clamp(1.75rem, 3vw, 2.5rem);
    font-weight: 900;
    margin-bottom: 12px;
  }

  .section-subtitle {
    color: $gray-500;
    margin-bottom: 60px;
  }
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  text-align: left;
  max-width: 1000px;
  margin: 0 auto 40px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: $white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease forwards;
  animation-delay: var(--delay);
  opacity: 0;
  will-change: transform, opacity;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  }

  &:focus-within {
    outline: 2px solid $teal;
    outline-offset: 2px;
  }

  .f-img {
    width: 72px;
    height: 72px;
    border-radius: 12px;
    overflow: hidden;
    flex-shrink: 0;
    background: $gray-100;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .f-info {
    flex: 1;
    min-width: 0;

    h3 {
      font-weight: 700;
      font-size: 1.1rem;
      font-weight: 700;
      margin-bottom: 6px;
    }

    p {
      font-size: 0.85rem;
      color: $gray-500;
      line-height: 1.6;
      margin: 0;
    }
  }

  .f-badge {
    font-weight: 900;
    color: $teal;
    font-size: 0.75rem;
    padding: 4px 10px;
    background: rgba($teal, 0.1);
    border-radius: 4px;
    flex-shrink: 0;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 使命区
.story-section {
  padding: 100px 80px;
  background: $gray-100;

  @media (max-width: 768px) {
    padding: 60px 24px;
    background: $white;
  }
}

.story-container {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 80px;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 60px;
  }
}

.story-visual {
  position: relative;

  img {
    width: 100%;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    transition: transform 0.3s ease;

    &:hover {
      transform: translate(-4px, -4px);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
  }

  .quote-card {
    position: absolute;
    bottom: -40px;
    right: -40px;
    background: $white;
    padding: 28px;
    width: 320px;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

    @media (max-width: 1024px) {
      position: relative;
      bottom: auto;
      right: auto;
      width: 90%;
      margin: -40px auto 0;
    }

    @media (max-width: 640px) {
      width: 95%;
      padding: 20px;
    }

    .quote-icon {
      width: 32px;
      height: 32px;
      color: $teal;
      margin-bottom: 12px;
    }

    p {
      font-size: 0.95rem;
      line-height: 1.7;
      font-style: italic;
      margin-bottom: 16px;
      color: $gray-500;
    }

    strong {
      color: $teal;
      font-size: 0.9rem;
    }
  }
}

.story-content {
  .story-title {
    font-family: 'Noto Serif SC', serif;
    font-size: clamp(1.75rem, 3vw, 2.5rem);
    font-weight: 900;
    margin: 24px 0;
    line-height: 1.3;
  }

  p {
    line-height: 1.8;
    color: $gray-500;
    margin-bottom: 40px;
  }
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-item {
    text-align: center;
    padding: 20px 16px;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    transition: all 0.2s;
    background: $white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }

    strong {
      display: block;
      font-size: 1.5rem;
      font-weight: 900;
      color: $teal;
      line-height: 1;
    }

    span {
      display: block;
      margin-top: 8px;
      font-size: 0.7rem;
      font-weight: 700;
      color: $gray-400;
      letter-spacing: 0.5px;
    }
  }
}

// 响应式设计优化
@media (max-width: 1200px) {
  .hero-grid {
    gap: 48px;
  }

  .collage-area {
    gap: 16px;
    
    .stat-badge {
      margin-right: 20px;
    }
  }
}

@media (max-width: 1024px) {
  .collage-area {
    .card-2 {
      margin-top: 20px;
    }
    
    .card-3 {
      margin-left: 20px;
    }
  }
}

// 减少动画偏好
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
</style>