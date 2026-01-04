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
        <!-- ✅ 编辑按钮 -->
        <span class="tool-icon edit-btn" @click="openProfileModal" title="编辑资料">✎</span>
      </div>

      <div class="profile-summary">
        <div class="avatar-large">
          <img 
              v-if="userStore.userInfo?.avatar" 
              :src="getImgUrl(userStore.userInfo.avatar)" 
              class="real-avatar" 
              alt="avatar" 
          />
          <div v-else class="text-avatar">
              {{ getFirstChar(userStore.userInfo?.full_name || userStore.userInfo?.username) }}
          </div>
          <div class="status-ring"></div>
        </div>
        <h3>Good Morning, {{ studentProfile.real_name || userStore.userInfo?.username }}</h3>
        <p class="user-class-info">
          {{ studentProfile.class_name || '暂未入班' }}
        </p>

        <p class="slogan">坚持学习，达成目标</p>
        
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

    <!-- ================= 学生资料编辑弹窗 ================= -->
    <div class="modal-overlay" v-if="showProfileModal" @click.self="showProfileModal = false">
      <div class="modal-content" style="width: 550px;">
        <div class="modal-header">
          <div class="header-left">
            <span class="icon-bg" style="background: #e0f2f1; color: #00c9a7;">🎓</span>
            <h3>我的学籍档案</h3>
          </div>
          <span class="close-btn" @click="showProfileModal = false">×</span>
        </div>

        <div class="modal-body">
          
          <!-- 头像上传 -->
          <div class="avatar-upload-wrapper">
            <div class="avatar-edit" @click="triggerFileInput">
              <img 
                v-if="profileForm.avatar" 
                :src="getImgUrl(profileForm.avatar)" 
                class="real-avatar" 
                alt="avatar" 
              />
              <!-- 2. 否则显示文字头像 (优先取编辑框里的名字，没有再取账号) -->
              <div v-else class="text-avatar">
                  {{ getFirstChar(profileForm.real_name || userStore.userInfo?.username) }}
              </div>
              <div class="overlay"><span>📷</span></div>
            </div>
            <input type="file" ref="fileInputRef" accept="image/*" style="display:none" @change="handleFileChange" />
          </div>

          <!-- 只读信息区 (灰色背景) -->
          <div class="info-card-readonly">
            <div class="info-item">
              <label>所属班级</label>
              <span>{{ studentProfile.class_name }}</span>
            </div>
            <div class="info-item">
              <label>学号</label>
              <span>{{ studentProfile.student_number || '未录入' }}</span>
            </div>
            <div class="info-item">
              <label>已修课程</label>
              <span>{{ studentProfile.course_count }} 门</span>
            </div>
          </div>

          <!-- 编辑表单 -->
          <div class="form-row">
            <div class="form-group">
              <label>真实姓名</label>
              <input 
                type="text" 
                v-model="profileForm.real_name" 
                disabled 
                class="is-disabled"
              />
            </div>
            <div class="form-group">
              <label>性别</label>
              <el-select v-model="profileForm.gender" class="custom-select" placeholder="请选择">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
                <el-option label="保密" value="保密" />
              </el-select>
            </div>
          </div>

          <div class="form-group">
            <label>手机号</label>
            <input 
              type="text" 
              v-model="profileForm.phone" 
              disabled 
              class="is-disabled"
            />
          </div>

          <div class="form-group">
            <label>学习宣言 (简介)</label>
            <textarea v-model="profileForm.intro" rows="2" placeholder="写一句话鼓励自己..."></textarea>
          </div>

        </div>

        <div class="modal-footer">
          <button class="btn-text" @click="showProfileModal = false">取消</button>
          <button class="btn-submit" @click="submitProfile" :disabled="isSubmitLoading">保存修改</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import request from '@/utils/request';
import StudentSidebar from '@/components/StudentSidebar.vue';
import { getImgUrl } from '@/utils/index';
import { getMyEnrolledClasses, type ClassItem } from '@/api/course';
import { uploadImage } from '@/api/common';
// ✅ 引入新写的 API
import { getMyStudentProfile, updateMyStudentProfile, type StudentProfile } from '@/api/profile';

const router = useRouter();
const userStore = useUserStore();

const studentProfile = ref<Partial<StudentProfile>>({});
// 编辑表单数据
const profileForm = reactive<Partial<StudentProfile>>({
  real_name: '',
  gender: '保密',
  phone: '',
  intro: '',
  avatar: ''
});
// 弹窗控制
const showProfileModal = ref(false);
const isSubmitLoading = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);

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

const getFirstChar = (name?: string) => {
  return name ? name.charAt(0).toUpperCase() : 'S';
};

onMounted(() => {
  userStore.fetchUserInfo();
  fetchMyCourses();
  fetchProfile();
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

// 1. 获取档案
const fetchProfile = async () => {
  try {
    const res = await getMyStudentProfile();
    studentProfile.value = res;

    // ✅ 关键修复：刷新页面后，把档案里的头像和姓名同步给 userStore
    // 因为右侧边栏显示的是 userStore 里的数据
    if (userStore.userInfo) {
      if (res.avatar) {
        userStore.userInfo.avatar = res.avatar;
      }
      if (res.real_name) {
        userStore.userInfo.full_name = res.real_name;
      }
    }
  } catch (error) {
    console.error("加载档案失败", error);
  }
};

// 2. 打开编辑弹窗
const openProfileModal = () => {
  Object.assign(profileForm, studentProfile.value);
  if (userStore.userInfo?.username) {
    profileForm.phone = userStore.userInfo.username;
  }

  showProfileModal.value = true;
};

// 3. 提交修改
const submitProfile = async () => {
  isSubmitLoading.value = true;
  try {
    const res = await updateMyStudentProfile(profileForm);
    studentProfile.value = res;
    
    // ✅ 关键新增：同步更新右侧边栏显示的数据
    if (userStore.userInfo) {
      // 1. 更新头像
      userStore.userInfo.avatar = res.avatar;
      // 2. 更新姓名 (如果改了姓名，这里也需要同步显示)
      if (res.real_name) {
        userStore.userInfo.full_name = res.real_name;
      }
    }

    showProfileModal.value = false;
    alert('个人资料已更新');
  } catch (error) {
    console.error(error);
  } finally {
    isSubmitLoading.value = false;
  }
};

// 4. 头像上传 (复用之前的逻辑，稍作调整)
const triggerFileInput = () => fileInputRef.value?.click();
const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    try {
      const res = await uploadImage(input.files[0], 'avatars');
      profileForm.avatar = res.url; // 仅更新表单里的头像，保存后才生效
    } catch(e) { alert('上传失败'); }
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
      width: 80px; 
  height: 80px; 
  margin: 0 auto 15px; 
  position: relative; 
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e0f2f1; /* 边框色 */
  transition: all 0.3s;

  &:hover {
    border-color: $primary-color;
    .avatar-overlay { opacity: 1; }
  }

  /* 图片头像 */
  .real-avatar {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  /* ✅ 新增：文字头像样式 */
  .text-avatar {
    width: 100%;
    height: 100%;
    background-color: #e0f2f1; /* 浅青色背景 */
    color: $primary-color;     /* 深青色文字 */
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;           /* 大字体 */
    font-weight: bold;
  }

  /* 遮罩层 */
  .avatar-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s;
    span { font-size: 24px; }
  }
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

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 999; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(4px); }

.modal-content { background: white; width: 550px; border-radius: 16px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); display: flex; flex-direction: column; gap: 20px; animation: popUp 0.3s ease;
  .modal-header { display: flex; justify-content: space-between; align-items: center; 
    .header-left { display: flex; gap: 10px; align-items: center; .icon-bg { width: 36px; height: 36px; background: #e0f2f1; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; } h3 { margin: 0; font-size: 18px; font-weight: 700; color: $text-dark; } }
    .close-btn { font-size: 24px; cursor: pointer; color: #999; &:hover { color: $text-dark; } }
  }

  .modal-body { display: flex; flex-direction: column; gap: 18px;
    .form-group { label { font-size: 13px; font-weight: 600; display: block; margin-bottom: 8px; color: #555; } input, textarea { width: 100%; padding: 10px 12px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 14px; outline: none; transition: all 0.3s; &:focus { border-color: $primary-color; box-shadow: 0 0 0 4px rgba(0,201,167,0.1); } } }
    .form-row { display: flex; gap: 20px; .form-group { flex: 1; } }
    
    /* 修复弹窗内的头像上传样式 */
    .avatar-upload-wrapper { display: flex; flex-direction: column; align-items: center; margin-bottom: 10px;
      .avatar-edit { width: 80px; height: 80px; border-radius: 50%; position: relative; cursor: pointer; overflow: hidden; border: 2px solid #e0f2f1; transition: all 0.3s;
        img { width: 100%; height: 100%; object-fit: cover; }
        .text-avatar {
          width: 100%;
          height: 100%;
          background-color: #e0f2f1; /* 浅青色背景 */
          color: $primary-color;     /* 深青色文字 */
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 32px;
          font-weight: bold;
        }
        .overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s; span { color: white; font-size: 12px; font-weight: 600; } }
        &:hover { border-color: $primary-color; .overlay { opacity: 1; } } }
    }

    /* 只读信息卡片 */
    .info-card-readonly { background-color: #f8f9fa; border-radius: 10px; padding: 15px; display: flex; justify-content: space-between; margin-bottom: 10px; border: 1px dashed #e0e0e0;
      .info-item { text-align: center; label { font-size: 12px; color: #a4b0be; display: block; margin-bottom: 4px; } span { font-size: 14px; font-weight: 600; color: #2d3436; } }
    }
  }

  .modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 10px;
    button { padding: 12px 24px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; }
    .btn-text { background: transparent; color: #666; &:hover { background: #f5f5f5; } }
    .btn-submit { background: $primary-color; color: white; box-shadow: 0 4px 12px rgba(0,201,167,0.3); &:hover { filter: brightness(0.9); transform: translateY(-1px); } &:disabled { opacity: 0.6; cursor: not-allowed; } }
  }
}

/* 下拉框修正 */
.custom-select { width: 100%; }
.custom-select :deep(.el-input__wrapper) { box-shadow: 0 0 0 1px #e0e0e0 inset !important; padding: 4px 12px; }
.custom-select :deep(.el-input__wrapper.is-focus) { box-shadow: 0 0 0 1px #00c9a7 inset !important; }

@keyframes popUp { from { transform: scale(0.9) translateY(20px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
</style>