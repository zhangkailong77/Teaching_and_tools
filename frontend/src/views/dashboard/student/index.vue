<template>
  <div class="dashboard-container">
    
    <StudentSidebar />

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
        <div class="course-card" v-for="(course, index) in courseList" :key="index">
          
          <!-- 封面区域 -->
          <div class="card-cover" :style="{ backgroundColor: course.color, backgroundImage: `url(${getImgUrl(course.cover)})`, backgroundSize: 'cover' }">
            <span class="fav-icon">❤</span>
            <!-- 如果没有封面图，显示课程类型的标签 -->
            <div class="course-tag" v-if="!course.cover">FRONTEND</div>
          </div>
          
          <div class="card-body">
            <!-- 课程名称 -->
            <h4 :title="course.name">{{ course.name }}</h4>
            
            <!-- 显示所属班级 (新增) -->
            <p style="font-size: 12px; color: #a4b0be; margin-bottom: 10px;">
              班级: {{ course.className }}
            </p>

            <!-- 进度条 -->
            <div class="progress-wrapper">
              <div class="progress-bg">
                <div class="progress-fill" :style="{ width: course.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ course.progress }}%</span>
            </div>

            <div class="teacher-info">
              <img 
                v-if="course.teacherAvatar" 
                :src="getImgUrl(course.teacherAvatar)" 
                class="avatar-img" 
                alt="T"
              />

              <div v-else class="avatar">
                {{ course.teacherName?.charAt(0) }}
              </div>
              
              <div class="details">
                <div class="name">{{ course.teacherName }}</div>
                <div class="role">{{ course.teacherTitle || '讲师' }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="courseList.length === 0" style="grid-column: 1/-1; text-align: center; padding: 40px; color: #999;">
          📭 你还没有加入任何班级或班级暂无课程
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
import request from '@/utils/request';
import StudentSidebar from '@/components/StudentSidebar.vue';
import { getImgUrl } from '@/utils/index';
import { getMyEnrolledClasses, type ClassItem } from '@/api/course';

const router = useRouter();
const userStore = useUserStore();
// 定义状态
const isLoading = ref(false);
const comfyUrl = ref(''); // 用来存后端返回的 URL

interface StudentCourseCard {
  id: number;
  name: string;
  className: string;
  cover: string;
  progress: number;
  color: string;
  teacherName?: string;
  teacherTitle?: string;
  teacherAvatar?: string;
}

// ✅ 【新增】真实数据列表
const courseList = ref<StudentCourseCard[]>([]);

// ✅ 【新增】随机颜色工具函数
const getRandomColor = () => {
  const colors = ['#2d3436', '#f1c40f', '#3498db', '#e74c3c', '#9b59b6', '#2ecc71'];
  return colors[Math.floor(Math.random() * colors.length)];
};

onMounted(() => {
  userStore.fetchUserInfo();
  fetchMyCourses();
});

const fetchMyCourses = async () => {
  try {
    const res = await getMyEnrolledClasses();
    const tempList: StudentCourseCard[] = [];

    res.forEach(cls => {
      // 如果班级绑定了课程，把每一门课都拆出来变成一个卡片
      if (cls.bound_course_names && cls.bound_course_names.length > 0) {
        cls.bound_course_names.forEach((cName, index) => {
          const specificCover = cls.bound_course_covers && cls.bound_course_covers[index] 
                                ? cls.bound_course_covers[index] 
                                : cls.cover_image;

          tempList.push({
            id: cls.bound_course_ids ? cls.bound_course_ids[index] : index,
            name: cName,
            className: cls.name,
            
            cover: specificCover || '', // ✅ 使用精准封面
            
            progress: 0,
            color: getRandomColor(),
            teacherName: cls.teacher_name, 
            teacherTitle: cls.teacher_title,
            teacherAvatar: cls.teacher_avatar
          });
        });
      } else {
        // 如果没绑课，显示一个占位卡片
        tempList.push({
          id: cls.id,
          name: '暂未安排课程',
          className: cls.name,
          cover: cls.cover_image || '',
          progress: 0,
          color: getRandomColor(),
          teacherName: '班主任'
        });
      }
    });

    courseList.value = tempList;
  } catch (error) {
    console.error("加载课程失败", error);
  }
};

// 退出登录
const handleLogout = async () => {
  // 为了用户体验，不管后端关闭成不成功，前端都要能退出去
  // 所以我们用 try-catch 包裹，但不阻断跳转
  try {
    // 只有当是学生时才尝试关闭环境
    // (虽然老师调这个接口也没事，后端会判断，但前端省一次请求也好)
    await request.post('/practice/stop-practice');
    console.log('实训环境关闭请求已发送');
  } catch (error) {
    console.error('环境关闭失败，可能是网络问题', error);
  }

  // 原有的退出逻辑
  userStore.logout();
  router.push('/login');
};

const openSystemB = async () => {
  // 1. 【关键】点击瞬间，先打开一个新标签页
  // 这样浏览器就不会拦截了，因为它认为是你自己点的
  const newWindow = window.open('', '_blank');

  // 2. 给这个新窗口写一点提示文字，告诉用户别关
  if (newWindow) {
    newWindow.document.write(`
      <div style="text-align:center; padding-top:20%; font-family:sans-serif;">
        <h1>🚀 正在连接云端实训台...</h1>
        <p>系统正在唤醒 GPU 资源，这可能需要 30-60 秒，请勿关闭本窗口。</p>
        <div style="margin-top:20px; font-size: 24px;">⏳</div>
      </div>
    `);
  }

  // 加个按钮 loading 状态 (可选)
  const btnText = document.querySelector('.action-btn');
  if(btnText) btnText.innerHTML = '正在启动云显卡... ⏳';

  try {
    // 3. 后台慢慢请求接口 (这时候新窗口在转圈等待)
    const res = await request.post<any, any>('/practice/start-practice', {}, { 
      timeout: 120000 
    });
    
    // 4. 【关键】拿到 URL 后，把刚才那个窗口的地址替换掉
    if (res.url && newWindow) {
        newWindow.location.href = res.url;
    } else if (newWindow) {
        // 如果没返回 url，就关掉窗口
        newWindow.close();
        alert('启动异常，未获取到地址');
    }

  } catch (error) {
    // 5. 如果报错了，把那个新窗口关掉，并提示错误
    if (newWindow) newWindow.close();
    alert('启动失败，请联系管理员');
    console.error(error);
  } finally {
    if(btnText) btnText.innerHTML = '启动 ComfyUI 环境 <span class="arrow">▶</span>';
  }
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
    justify-content: flex-start; 
    margin-bottom: 40px;

    .logo-img {
      height: 40px; 
      width: auto; 
      max-width: 100%; 
      object-fit: contain;
    }
    
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

    min-height: 220px; 
    display: flex;
    flex-direction: column;
    justify-content: center;

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
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; padding-bottom: 20px;
    
    .course-card {
      background: white;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 5px 20px rgba(0, 0, 0, 0.02);
      transition: all 0.3s;
      border: 1px solid transparent;
      
      /* ✅ 关键 1: 开启 Flex 纵向布局，为了让底部对齐 */
      display: flex;
      flex-direction: column; 
      height: 100%; /* 撑满 Grid 这一行的高度 */

      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        border-color: $primary-color;
      }

      /* ✅ 关键 2: 封面高度固定为 160px (与教师端保持一致) */
      .card-cover {
        height: 160px; /* 固定高度 */
        width: 100%;
        position: relative;
        background-position: center;
        background-size: cover;
        flex-shrink: 0; /* 防止被挤压 */
        
        .fav-icon { position: absolute; top: 10px; right: 10px; color: white; cursor: pointer; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .course-tag { position: absolute; bottom: 10px; left: 10px; font-size: 10px; background: rgba(0,0,0,0.6); color: white; padding: 2px 8px; border-radius: 4px; backdrop-filter: blur(4px); }
      }

      /* ✅ 关键 3: 内容区域自适应填充 */
      .card-body {
        padding: 20px;
        flex: 1; /* 占据剩余所有空间 */
        display: flex;     /* 内部也用 Flex */
        flex-direction: column; /* 纵向排列 */

        h4 { 
          font-size: 16px; color: $text-dark; margin: 0 0 5px 0; 
          line-height: 1.4;
          /* 限制标题最多 2 行，防止太高 */
          display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }
        
        /* 班级名称样式微调 */
        p { font-size: 12px; color: #a4b0be; margin-bottom: 15px; }

        .progress-wrapper {
          margin-bottom: 20px; 
          display: flex; align-items: center; gap: 10px;
          .progress-bg { flex: 1; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }
          .progress-fill { height: 100%; background: $primary-color; border-radius: 3px; }
          .progress-text { font-size: 12px; color: $text-gray; }
        }

        /* ✅ 关键 4: 讲师信息强制沉底 */
        .teacher-info {
          margin-top: auto; /* 这是实现底部对齐的神奇代码 */
          padding-top: 15px;
          border-top: 1px solid #f5f5f5; /* 加一条分割线更清晰 */
          display: flex; align-items: center; gap: 10px;
          
          .avatar { 
            width: 30px; height: 30px; border-radius: 50%; background: #eee; 
            display: flex; align-items: center; justify-content: center; 
            font-size: 12px; color: #666; font-weight: bold;
          }
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

/* 老师头像图片样式 */
.avatar-img {
  width: 30px; 
  height: 30px; 
  border-radius: 50%; 
  object-fit: cover; /* 防止图片变形 */
  border: 1px solid #eee;
}
</style>