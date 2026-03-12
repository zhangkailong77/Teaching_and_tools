<template>
  <div class="dashboard-container">
    
    <!-- 1. 左侧 Sidebar (教师版) -->
    <TeacherSidebar />

    <!-- 2. 中间主内容区 -->
    <main class="main-content">
      <header class="top-bar">
        <div class="welcome-text">
          <h2>工作台</h2>
          <p>管理您的课程内容与教学进度</p>
        </div>
        <!-- 教师特有的核心操作 -->
        <button class="create-btn" @click="openCreateClassModal">
          + 创建班级
        </button>
      </header>

      <!-- 数据概览卡片 -->
      <DashboardStats :data="stats" />

      <!-- 实训平台入口 -->
      <TrainingPlatforms />

      <!-- 执教课程列表 -->
      <div class="section-title">
        <h3>我管理的班级与课程</h3>
        <div class="filter-tabs">
          <span :class="{ active: currentFilter === 0 }" @click="currentFilter = 0">进行中</span>
          <span :class="{ active: currentFilter === 1 }" @click="currentFilter = 1">已归档</span>
        </div>
      </div>

      <div class="course-list">
        <!-- ✅ 遍历 classList -->
        <div class="course-item" v-for="(item, index) in displayList" :key="`${item.id}-${index}`">
          
          <!-- 封面图 (如果没有图，显示首字母) -->
          <div class="course-img" :style="{ backgroundImage: `url(${item.cover_image || ''})`, backgroundColor: item.styleColor }">
            <span v-if="!item.cover_image">{{ item.displayTitle.charAt(0) }}</span>
          </div>
          
          <div class="course-info">
            <h4>{{ item.displayTitle }}</h4>
            <div class="details-row">
              <!-- 只有拆分后的卡片才显示“课程包”字样，未绑定的显示警告 -->
              <span v-if="!item.isSplit" class="course-tag warning" style="font-size: 12px;">
                ⚠️ 暂未安排教学内容
              </span>

              <span>👥 {{ item.student_count }} 人</span>
              <span class="divider">|</span>
              <!-- 时间 -->
              <span :class="{ 'overdue-text': isOverdue(item.end_date) && item.status === 0 }">
              📅 {{ formatDuration(item.start_date, item.end_date) }}
              <el-tooltip content="教学周期已结束，建议完成作业和考试后归档" placement="top" v-if="isOverdue(item.end_date) && item.status === 0">
                <el-icon class="warning-icon"><Warning /></el-icon>
              </el-tooltip>
            </span>
            </div>
          </div>

          <div class="class-display">
            <span class="name">{{ item.displaySubtitle }}</span>
          </div>


          <div class="course-actions">
            <button class="btn-outline" @click="goCourseware(item)">课件</button>
            <button class="btn-outline btn-badge-wrapper" @click="goHomework(item)">
              作业
              <span v-if="item.pending_count > 0" class="badge-dot">{{ item.pending_count }}</span>
            </button>
            
            <button class="btn-primary" @click="goStudents(item)">进入班级</button>
          </div>
        </div>

        <!-- 空状态提示 -->
        <div v-if="classList.length === 0" class="empty-state">
          暂无班级，请点击右上角创建
        </div>
      </div>
    </main>

    <!-- 3. 右侧个人中心 -->
    <aside class="right-panel">
      <div class="header-tools">
        <!-- 点击编辑按钮 -->
        <span class="tool-icon edit-btn" @click="openProfileModal" title="编辑资料">✎</span>
      </div>

      <div class="profile-summary">
        <div class="avatar-large">
          <!-- 如果没有头像，使用 DiceBear 生成一个 -->
          <img :src="getImgUrl(profile.avatar) || defaultAvatar" alt="avatar" />
        </div>
        
        <!-- 显示真实姓名，没有则显示账号 -->
        <h3>{{ profile.real_name || userStore.userInfo?.username }}</h3>
        
        <!-- 显示职称，没有则显示默认 -->
        <p class="role-badge">{{ profile.title || '教师' }}</p>

        <!-- 显示学校信息 -->
        <div class="school-info" v-if="profile.school">
          <span>🏛️ {{ profile.school }}</span>
          <span v-if="profile.college"> · {{ profile.college }}</span>
        </div>
      </div>

      <div class="schedule-section">
        <div class="rec-header">
          <h4>近期日程</h4>
          <!-- 可选：加个查看全部 -->
          <!-- <span class="view-all">全部</span> -->
        </div>
        
        <div class="schedule-list">
          <!-- 空状态 -->
          <div v-if="scheduleList.length === 0" class="empty-schedule">
             🎉 近期无紧急事项
          </div>

          <!-- 遍历日程 -->
          <div class="schedule-item" v-for="s in scheduleList" :key="s.id">
            <!-- 左侧日期块 -->
            <div class="date-box" :class="s.type">
              <span class="day">{{ formatScheduleDate(s.time).day }}</span>
              <span class="month">{{ formatScheduleDate(s.time).month }}</span>
            </div>
            <!-- 右侧信息 -->
            <div class="s-info">
              <div class="tag-row">
                <span class="tag" :class="s.type">{{ s.type === 'exam' ? '考试' : '作业' }}</span>
                <span class="time">{{ formatTimeOnly(s.time) }}</span>
              </div>
              <div class="title" :title="s.title">{{ s.title }}</div>
              <div class="class-name">{{ s.class_name }}</div>
            </div>
          </div>
        </div>
      </div>

      <AnnouncementWidget />
    </aside>

    <!-- ================= 编辑资料弹窗 ================= -->
    <div class="modal-overlay" v-if="showProfileModal" @click.self="showProfileModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <div class="header-left">
            <span class="icon-bg">👤</span>
            <h3>编辑个人资料</h3>
          </div>
          <span class="close-btn" @click="showProfileModal = false">×</span>
        </div>

        <div class="modal-body">
          <div class="avatar-upload-wrapper">
            <!-- 点击触发 triggerFileInput -->
            <div class="avatar-edit" @click="triggerFileInput">
              <!-- 显示当前表单里的头像，如果没有就显示默认图 -->
              <img :src="getImgUrl(profileForm.avatar) || defaultAvatar" alt="Avatar" />
              <div class="overlay">
                <span>📷 更换</span>
              </div>
            </div>
            
            <!-- 隐藏的 input，绑定了 ref="fileInputRef" 和 @change="handleFileChange" -->
            <input 
              type="file" 
              ref="fileInputRef" 
              accept="image/*" 
              style="display: none" 
              @change="handleFileChange"
            />
            <p class="avatar-tip">点击头像可上传新图片 (支持 JPG/PNG)</p>
          </div>
          <!-- 两列布局 -->
          <div class="form-row">
            <div class="form-group">
              <label>真实姓名</label>
              <input type="text" v-model="profileForm.real_name" placeholder="请输入姓名" />
            </div>
            <div class="form-group">
              <label>性别</label>
              <el-select 
                v-model="profileForm.gender" 
                placeholder="请选择" 
                size="large"
                class="custom-select"
              >
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
                <el-option label="保密" value="保密" />
              </el-select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>职称</label>
              <input type="text" v-model="profileForm.title" placeholder="例如：高级讲师" />
            </div>
            <div class="form-group">
              <label>联系电话</label>
              <input type="text" v-model="profileForm.phone" placeholder="请输入手机号" />
            </div>
          </div>

          <div class="form-group">
            <label>学校</label>
            <input type="text" v-model="profileForm.school" placeholder="例如：某某大学" />
          </div>

          <div class="form-group">
            <label>二级学院</label>
            <input type="text" v-model="profileForm.college" placeholder="例如：艺术设计学院" />
          </div>

          <div class="form-group">
            <label>个人简介</label>
            <textarea v-model="profileForm.intro" rows="3" placeholder="简单介绍一下自己..."></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-text" @click="showProfileModal = false">取消</button>
          <button class="btn-submit" @click="submitProfile" :disabled="isLoading">
            {{ isLoading ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ⬇️ 插入这段代码：新建班级弹窗 -->
    <div class="modal-overlay" v-if="showClassModal" @click.self="showClassModal = false">
      <div class="modal-content" style="width: 550px;"> <!-- 稍微宽一点放双列 -->
        
        <div class="modal-header">
          <div class="header-left">
            <span class="icon-bg" style="background: #e3f2fd; color: #0984e3;">📂</span>
            <h3>新建教学班级</h3>
          </div>
          <span class="close-btn" @click="showClassModal = false">×</span>
        </div>

        <div class="modal-body">
          
          <!-- 1. 班级名称 -->
          <div class="form-group">
            <label>班级名称 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="classForm.name" 
              placeholder="例如：2025 AI实训一班" 
            />
          </div>

          <!-- 2. 日期选择 (双列布局) -->
          <div class="form-row">
            <div class="form-group">
              <label>开课时间</label>
              <!-- ✅ 修改点：新增 :popover 配置 -->
              <!-- visibility: 'click' 表示点击输入框显示 -->
              <!-- hideOnContentClick: false 表示点击日历内部(选日期)时不关闭 -->
              <v-date-picker 
                v-model="classForm.startDate" 
                mode="dateTime" 
                is24hr
                :model-config="dateConfig" 
                color="teal"
                :popover="{ visibility: 'click', placement: 'bottom', keepVisibleOnInput: true }"
              >
                <template #default="{ inputValue, inputEvents }">
                  <div class="input-with-icon">
                    <input 
                      :value="inputValue" 
                      v-on="inputEvents" 
                      placeholder="选择日期和时间" 
                      readonly 
                      style="cursor: pointer;"
                    />
                    <span class="icon">⏰</span>
                  </div>
                </template>
                <template #footer>
                  <div class="picker-footer">
                    <button class="btn-today" @click="classForm.startDate = getTodayString()">此刻</button>
                  </div>
                </template>
              </v-date-picker>
            </div>

            <!-- 结课日期 -->
            <div class="form-group">
              <label>结课时间</label>
              <!-- ✅ 修改点：同样加上 :popover 配置 -->
              <v-date-picker 
                v-model="classForm.endDate" 
                mode="dateTime" 
                is24hr
                :model-config="dateConfig" 
                color="teal"
                :popover="{ visibility: 'click', placement: 'bottom', keepVisibleOnInput: true }"
              >
                <template #default="{ inputValue, inputEvents }">
                  <div class="input-with-icon">
                    <input 
                      :value="inputValue" 
                      v-on="inputEvents" 
                      placeholder="选择日期和时间" 
                      readonly 
                      style="cursor: pointer;"
                    />
                    <span class="icon">🏁</span>
                  </div>
                </template>
                <template #footer>
                  <div class="picker-footer">
                    <button class="btn-today" @click="classForm.endDate = getTodayString()">此刻</button>
                  </div>
                </template>
              </v-date-picker>
            </div>
          </div>

          <!-- 3. 班级封面 -->
          <div class="form-group">
            <label>班级封面</label>
            <div class="cover-selector">
              <div 
                v-for="(img, index) in coverOptions" 
                :key="index"
                class="cover-item"
                :class="{ active: classForm.coverImage === img }"
                @click="classForm.coverImage = img"
              >
                <img :src="img" />
                <div class="check-mark" v-if="classForm.coverImage === img">✓</div>
              </div>
            </div>
          </div>

          <!-- 4. 绑定课程资源 -->
          <div class="form-group">
            <label>绑定课程教材(支持多选)</label>
            <el-select 
              v-model="classForm.courseIds" 
              multiple
              placeholder="选择课程资源包" 
              size="large" 
              class="custom-select"
              :teleported="true"
              popper-class="class-select-dropdown"
            >
              <el-option 
                v-for="course in courseLibrary" 
                :key="course.id" 
                :label="course.name" 
                :value="course.id" 
              />
            </el-select>
            <p class="hint" v-if="courseLibrary.length === 0" style="font-size:12px;color:#999;margin-top:5px">
              暂无课程包，请先去 <a href="#" @click.prevent="router.push('/dashboard/teacher/courses')">资源库</a> 创建
            </p>
          </div>

          <!-- 5. 描述 -->
          <div class="form-group">
            <label>描述</label>
            <input type="text" v-model="classForm.description" placeholder="简单描述一下..." />
          </div>

        </div>

        <div class="modal-footer">
          <button class="btn-text" @click="showClassModal = false">取消</button>
          <button class="btn-submit" @click="submitCreateClass">立即创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import { getMyTeacherProfile, updateMyTeacherProfile, type TeacherProfile } from '@/api/profile';
import { uploadImage } from '@/api/common';
import TeacherSidebar from '@/components/TeacherSidebar.vue';
import { getMyClasses, createClass, getDashboardStats, getTeacherSchedule, updateClassStatus, type ClassItem, type ScheduleItem } from '@/api/course';
import { getMyCourses, getAvailableCourses, type CourseItem } from '@/api/content';
import { getImgUrl } from '@/utils/index';
import DashboardStats from './components/DashboardStats.vue'
import TrainingPlatforms from './components/TrainingPlatforms.vue'
import {
  Warning
} from '@element-plus/icons-vue'
import AnnouncementWidget from './components/AnnouncementWidget.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter();
const userStore = useUserStore();
const showProfileModal = ref(false);
const isLoading = ref(false);
const profile = ref<Partial<TeacherProfile>>({});
const profileForm = reactive<Partial<TeacherProfile>>({
  real_name: '',
  gender: '保密',
  title: '',
  phone: '',
  school: '',
  college: '',
  intro: ''
});
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';
// 1. 封面图选项 (新增)
const coverOptions = [
  'https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=300&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=300&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop'
];

const stats = ref<any>({ 
  total_students: 0, student_distribution: [], 
  my_resource_count: 0, platform_resource_count: 0,
  teaching_class_count: 0, teaching_distribution: [],
  total_pending: 0, task_distribution: { homework: 0, exam: 0 }
});
const classList = ref<ClassItem[]>([]); 
const courseLibrary = ref<CourseItem[]>([]); 

const showClassModal = ref(false); 

// ✅ 【新增】新建班级的表单数据
const classForm = reactive({ 
  name: '', 
  description: '', 
  courseIds: [] as number[],
  startDate: '', 
  endDate: '',
  coverImage: coverOptions[0] // 默认选中第一张
});
const dateConfig = { type: 'string', mask: 'YYYY-MM-DD HH:mm' };

const getTodayString = () => {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hour = String(date.getHours()).padStart(2, '0');
  const min = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hour}:${min}`;
};

const scheduleList = ref<ScheduleItem[]>([]);

onMounted(async () => {
  userStore.fetchUserInfo();
  loadProfile();
  loadDashboardData();
});

const loadProfile = async () => {
  try {
    const res = await getMyTeacherProfile();
    profile.value = res;
  } catch (error) {
    console.error("加载档案失败", error);
  }
};

// 定义一个扩展的接口，方便 TS 检查
interface TeachingCard extends ClassItem {
  displayTitle: string;
  displaySubtitle: string;
  bindingCourseId?: number;
  isSplit: boolean;
}

// 修改 loadDashboardData
const loadDashboardData = async () => {
  try {
    const [statsRes, classesRes, scheduleRes] = await Promise.all([
      getDashboardStats(),
      getMyClasses({ status: currentFilter.value }),
      getTeacherSchedule() 
    ]);

    stats.value = statsRes;
    scheduleList.value = scheduleRes;
    
    const tempDisplayList: any[] = []; 

    classesRes.forEach(cls => {
      if (cls.bound_course_names && cls.bound_course_names.length > 0) {
        cls.bound_course_names.forEach((cName, index) => {
          const cId = cls.bound_course_ids ? cls.bound_course_ids[index] : undefined;
          const cPublicId = cls.bound_course_public_ids ? cls.bound_course_public_ids[index] : undefined;

          tempDisplayList.push({
            ...cls,
            styleColor: getRandomColor(),
            displayTitle: cName,
            displaySubtitle: cls.name,
            bindingCourseId: cId,
            bindingCoursePublicId: cPublicId,
            isSplit: true
          });
        });
      } 
      // B. 如果没绑定课程，就显示原始班级卡片
      else {
        tempDisplayList.push({
          ...cls,
          styleColor: getRandomColor(),
          displayTitle: cls.name,       
          displaySubtitle: '未绑定课程', 
          isSplit: false
        });
      }
    });

    classList.value = tempDisplayList;

  } catch (error) {
    console.error("加载数据失败", error);
  }
};

// 打开编辑弹窗
const openProfileModal = () => {
  // 把当前展示的数据复制给表单
  Object.assign(profileForm, profile.value);
  showProfileModal.value = true;
};

// 提交修改
const submitProfile = async () => {
  isLoading.value = true;
  try {
    const res = await updateMyTeacherProfile(profileForm);
    // 更新展示数据
    profile.value = res;
    showProfileModal.value = false;
    alert('个人资料已更新');
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

// --- ✅ 新增：头像上传逻辑开始 ---

// 1. 获取文件输入框的 DOM 引用
const fileInputRef = ref<HTMLInputElement | null>(null);

// 2. 点击头像时，模拟点击隐藏的文件输入框
const triggerFileInput = () => {
  fileInputRef.value?.click();
};

// 3. 监听文件选择变化，并上传
const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  
  // 确保用户真的选了文件
  if (input.files && input.files[0]) {
    const file = input.files[0];
    
    // (可选) 校验图片大小，例如限制 2MB
    if (file.size > 2 * 1024 * 1024) {
      alert('图片大小不能超过 2MB');
      return;
    }

    try {
      // 调用我们封装好的 API，传入 'avatars' 类型
      const res = await uploadImage(file, 'avatars');
      
      // 后端返回了 url，直接赋值给表单，这样图片就会立刻变了
      profileForm.avatar = res.url; 
      
    } catch (error) {
      console.error('上传失败', error);
      alert('头像上传失败，请重试');
    } finally {
      // 清空 input，防止用户重复选同一张图时不触发 change 事件
      input.value = '';
    }
  }
};
// --- ✅ 头像上传逻辑结束 ---

// ✅ 【新增】打开新建班级弹窗（先拉取课程包列表）
const openCreateClassModal = async () => {
  try {
    const res = await getAvailableCourses(); // 只获取已授权课程
    courseLibrary.value = res;
  } catch (e) { console.error(e); }
  showClassModal.value = true;
};

// ✅ 【新增】提交创建班级
const submitCreateClass = async () => {
  if (!classForm.name) return;
  try {
    await createClass({
      name: classForm.name,
      description: classForm.description,
      // ✅ 提交封面
      cover_image: classForm.coverImage, 
      start_date: formatDate(classForm.startDate),
      end_date: formatDate(classForm.endDate),
      course_ids: classForm.courseIds
    });
    alert('创建成功');
    showClassModal.value = false;
    // 重置表单
    classForm.name = '';
    classForm.description = '';
    classForm.courseIds = [];
    classForm.startDate = '';
    classForm.endDate = '';
    
    loadDashboardData();
  } catch (error) {
    console.error(error);
  }
};

// ✅ 【新增】辅助工具函数
const formatDate = (val: any) => {
  if (!val) return undefined;
  if (val instanceof Date) return val.toISOString();
  return val;
};

// ✅ 新增：格式化课程周期显示
const formatDuration = (start?: string, end?: string) => {
  if (!start) return '时间待定';
  
  // 截取日期部分 (YYYY-MM-DD)
  const s = start.split('T')[0];
  
  // 如果有结束时间
  if (end) {
    const e = end.split('T')[0];
    return `${s} 至 ${e}`;
  }
  
  // 如果只有开始时间
  return `${s} 开课`;
};

const getRandomColor = () => {
  const colors = ['#6c5ce7', '#0984e3', '#00b894', '#e17055', '#fdcb6e'];
  return colors[Math.floor(Math.random() * colors.length)];
};

// 1. 定义分类状态
const currentFilter = ref(0); 

const displayList = computed(() => {
  return classList.value.filter(item => item.status === currentFilter.value);
});

const isOverdue = (endDate?: string) => {
  if (!endDate) return false;
  return new Date(endDate).getTime() < new Date().getTime();
};

// ✅ 4. 新增：处理归档/恢复操作
const handleStatusChange = async (item: any) => {
  const isArchiving = item.status === 0;
  const actionText = isArchiving ? '归档' : '恢复';
  
  try {
    await ElMessageBox.confirm(
      isArchiving 
        ? `确定要归档【${item.displaySubtitle}】吗？归档后该班级将移至已归档列表。`
        : `确定要恢复【${item.displaySubtitle}】的教学状态吗？`,
      '状态确认',
      { confirmButtonText: `确认${actionText}`, type: isArchiving ? 'warning' : 'info' }
    );

    // 调用之前在班级管理写好的接口
    const targetStatus = isArchiving ? 1 : 0;
    await updateClassStatus(item.id, targetStatus);
    
    ElMessage.success(`班级${actionText}成功`);
    
    // 重新加载工作台数据
    loadDashboardData();
  } catch (e) {
    // 取消操作
  }
};

// 3. 定义跳转函数
const goCourseware = (item: any) => {
  if (item.bindingCoursePublicId) {
    router.push(`/dashboard/teacher/courses/${item.bindingCoursePublicId}`);
  } 
  else if (item.bindingCourseId) {
    router.push(`/dashboard/teacher/courses/${item.bindingCourseId}`);
  }
  else {
    router.push(`/dashboard/teacher/courses`);
  }
};

const goHomework = (item: any) => {
  // 跳转到作业管理，并带上班级 ID 参数
  router.push(`/dashboard/teacher/homeworks?class_id=${item.id}`);
};

const goStudents = (item: any) => {
  // 跳转到学生名单，并带上班级 ID 参数
  router.push(`/dashboard/teacher/students?class_id=${item.id}`);
};

// ✅ 新增：格式化日程日期 (Dec 25)
const formatScheduleDate = (dateStr: string) => {
  const d = new Date(dateStr);
  const month = d.toLocaleString('en-US', { month: 'short' }); 
  const day = d.getDate();
  return { month, day };
}

// ✅ 新增：格式化时间 (19:30)
const formatTimeOnly = (dateStr: string) => {
  return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

watch(currentFilter, () => {
  loadDashboardData();
});
</script>

<style scoped lang="scss">
$sidebar-width: 240px;
$right-panel-width: 300px;
$primary-purple: #00c9a7; 
$primary-color: #00c9a7;
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

      .class-display {
        display: flex;
        flex-direction: column; /* 上下排列：上面是“所属班级”小字，下面是班级大字 */
        align-items: flex-end;  /* 靠右对齐，靠近按钮 */
        margin-right: 30px;     /* 和按钮保持距离 */
        min-width: 120px;       /* 防止太窄 */

        .label {
          font-size: 12px;
          color: #a4b0be;
          margin-bottom: 2px;
        }

        .name {
          font-size: 12px;
          font-weight: bold;
          color: $primary-color; /* 使用你的青绿色 */
          background: rgba(0, 201, 167, 0.1); /* 淡绿色背景 */
          padding: 4px 12px;
          border-radius: 6px;
        }
      }
      
      .course-info {
      flex: 1;
      /* 稍微调整下间距 */
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 8px;
      h4 { font-size: 15px; margin: 0; } /* 标题稍微大一点 */
      .details-row { margin: 0; color: #666; font-size: 13px; }
    }

    .course-item {
      align-items: center; /* 关键：让封面、文字、班级、按钮垂直居中对齐 */
    }

      .course-actions {
        display: flex; gap: 10px;
        button { padding: 8px 16px; border-radius: 8px; font-size: 13px; cursor: pointer; font-weight: 500; }
        .btn-outline { background: transparent; border: 1px solid #eee; color: $text-dark; &:hover { border-color: $primary-purple; color: $primary-purple; } }
        /* 修改后的代码 (无警告) */
        .btn-primary { 
          background: $primary-purple; 
          color: white; 
          border: none; 
          transition: filter 0.2s; /* 加个过渡动画更丝滑 */
          
          &:hover { 
            /* 不改变背景色值，而是直接调低亮度，效果是一样的 */
            filter: brightness(0.9); 
          } 
        }
      }
    }
  }
}

/* Right Panel */
.right-panel {
  width: $right-panel-width; background: white; padding: 30px; display: flex; flex-direction: column; gap: 30px; border-left: 1px solid #eee;
  .header-tools { 
    text-align: right; 
    color: $text-gray; 
    
    /* ✅ 新增：编辑按钮样式 */
    .edit-btn { 
      font-size: 18px; 
      cursor: pointer; 
      transition: color 0.2s; 
      margin-left: 10px;
      &:hover { color: $primary-purple; }
    }
  }
  .profile-summary {
    text-align: center;
    .avatar-large img { 
      width: 80px; height: 80px; border-radius: 50%; 
      /* ✅ 修改：边框颜色改浅一点，更协调 */
      border: 4px solid #e0f2f1; 
    }
    h3 { font-size: 18px; margin: 10px 0 5px; }
    .role-badge { display: inline-block; background: $primary-purple; color: white; padding: 4px 12px; border-radius: 12px; font-size: 10px; }
    
    /* ✅ 新增：学校信息样式 */
    .school-info { font-size: 12px; color: $text-gray; margin-top: 8px; }
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

/* ================= 编辑资料弹窗 ================= */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5); z-index: 999;
  display: flex; justify-content: center; align-items: center;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white; width: 500px; border-radius: 16px; padding: 25px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  animation: popUp 0.3s ease;
  display: flex; flex-direction: column; gap: 15px;

  .modal-header {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;
    .header-left {
      display: flex; align-items: center; gap: 10px;
      .icon-bg { width: 32px; height: 32px; background: #e0f2f1; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
      h3 { margin: 0; font-size: 18px; color: $text-dark; }
    }
    .close-btn { font-size: 24px; cursor: pointer; color: #999; &:hover { color: $text-dark; } }
  }

  .modal-body {
    display: flex; flex-direction: column; gap: 15px;
    
    .form-row { display: flex; gap: 15px; .form-group { flex: 1; } }

    .form-group {
      label { font-size: 13px; font-weight: 600; color: #555; display: block; margin-bottom: 6px; }
      input, select, textarea {
        width: 100%; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 14px; outline: none; color: $text-dark;
        &:focus { border-color: $primary-purple; box-shadow: 0 0 0 3px rgba(0, 201, 167, 0.1); }
      }
    }

    select {
      /* 核心：去掉浏览器默认丑陋的下拉箭头和边框 */
      appearance: none; 
      -webkit-appearance: none;
      -moz-appearance: none;

      /* 使用 SVG 作为背景图来实现自定义箭头 (灰色简约箭头) */
      background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23a4b0be' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
      background-repeat: no-repeat;
      background-position: right 12px center; /* 箭头靠右居中 */
      background-size: 16px; /* 箭头大小 */
      
      padding-right: 35px; /* 给箭头留出空间，防止文字盖住箭头 */
      cursor: pointer;
    }
  }

  .modal-footer {
    display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px;
    button { padding: 10px 20px; border-radius: 8px; font-size: 14px; cursor: pointer; border: none; font-weight: 600; }
    .btn-text { background: transparent; color: #666; &:hover { background: #f5f5f5; } }
    .btn-submit { 
      background: $primary-purple; color: white; 
      transition: filter 0.2s;
      &:hover { filter: brightness(0.9); }
      &:disabled { opacity: 0.6; cursor: not-allowed; }
    }
  }
}

@keyframes popUp {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

/* 头像上传样式 */
.avatar-upload-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;

  .avatar-edit {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    position: relative;
    cursor: pointer;
    overflow: hidden;
    border: 2px solid #e0f2f1;
    transition: all 0.3s;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    /* 悬停时的遮罩层 */
    .overlay {
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex; justify-content: center; align-items: center;
      opacity: 0;
      transition: opacity 0.3s;
      
      span { color: white; font-size: 12px; font-weight: 600; }
    }

    &:hover {
      border-color: $primary-color;
      .overlay { opacity: 1; }
    }
  }

  .avatar-tip {
    font-size: 12px;
    color: #a4b0be;
    margin-top: 8px;
  }
}

/* 班级列表里的标签样式 */
.course-tag { 
  background: #e0f2f1; color: $primary-color; padding: 2px 8px; border-radius: 4px; font-weight: 500; font-size: 12px;
  &.warning { background: #fff3e0; color: #ff9800; } 
}

/* 详情行样式 */
.details-row { margin-top: 5px; font-size: 12px; color: #666; .divider { margin: 0 8px; color: #ddd; } }

/* 封面图文字居中 */
.course-img {
  /* 确保原来的样式里有这些，如果没有就加上 */
  display: flex; align-items: center; justify-content: center; 
  color: white; font-weight: bold; font-size: 24px;
  background-size: cover; background-position: center;
}

/* 空状态 */
.empty-state { text-align: center; padding: 40px; color: #999; border: 2px dashed #eee; border-radius: 15px; width: 100%; }

/* 封面选择器 */
.cover-selector {
  display: flex; gap: 10px; margin-top: 5px;
  .cover-item {
    width: 60px; height: 40px; border-radius: 6px; overflow: hidden; cursor: pointer; position: relative; border: 2px solid transparent; transition: all 0.2s;
    img { width: 100%; height: 100%; object-fit: cover; }
    &:hover { transform: scale(1.05); }
    &.active { border-color: $primary-color; .check-mark { position: absolute; inset: 0; background: rgba(0, 201, 167, 0.4); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; } }
  }
}

/* 日历底部按钮 */
.picker-footer {
  padding: 10px; border-top: 1px solid #eee; display: flex; justify-content: center;
  .btn-today { background: transparent; border: none; color: $primary-color; font-size: 13px; font-weight: 600; cursor: pointer; padding: 4px 12px; border-radius: 6px; transition: background 0.2s; &:hover { background: rgba(0, 201, 167, 0.1); } }
}

.class-badge {
  display: inline-block;
  background-color: #f0f2f5;
  color: #606266;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #e0e0e0;
}

.time-row {
  margin-top: 8px;
  font-size: 12px;
  color: #a4b0be;
}

/* ✅ P3: 按钮微标样式 */
.btn-badge-wrapper {
  position: relative;
  .badge-dot {
    position: absolute;
    top: -5px;
    right: -5px;
    background-color: #ff4d4f;
    color: white;
    font-size: 10px;
    height: 16px;
    min-width: 16px;
    padding: 0 4px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid white;
    font-weight: bold;
  }
}

/* ✅ P2: 日程表样式优化 */
.schedule-list {
  display: flex; flex-direction: column; gap: 15px;
  
  .empty-schedule {
    text-align: center; color: #999; font-size: 13px; padding: 20px 0;
  }

  .schedule-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding-bottom: 12px; border-bottom: 1px dashed #f5f5f5;
    &:last-child { border-bottom: none; }

    .date-box { 
      background: #f5f6fa; padding: 6px 10px; border-radius: 8px; text-align: center; min-width: 48px;
      /* 不同类型不同颜色 */
      &.exam { background: #e3f2fd; color: #0984e3; }
      &.homework { background: #fff3e0; color: #e67e22; }

      .day { display: block; font-weight: bold; font-size: 16px; line-height: 1.2; }
      .month { font-size: 10px; text-transform: uppercase; opacity: 0.8; }
    }

    .s-info { 
      flex: 1; overflow: hidden;
      .tag-row {
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;
        .tag { font-size: 10px; padding: 1px 4px; border-radius: 4px; font-weight: bold; }
        .tag.exam { background: rgba(9, 132, 227, 0.1); color: #0984e3; }
        .tag.homework { background: rgba(230, 126, 34, 0.1); color: #e67e22; }
        .time { font-size: 11px; color: #999; }
      }
      .title { font-size: 13px; font-weight: 600; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 2px; }
      .class-name { font-size: 11px; color: #999; }
    }
  }
}

.overdue-text {
  color: #ff9f43; /* 警示橙色 */
  font-weight: 600;
  .warning-icon {
    margin-left: 4px;
    vertical-align: middle;
    cursor: help;
  }
}

/* 归档按钮样式 */
.btn-archive {
  padding: 8px !important;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #909399 !important;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.05) !important;
    color: $primary-color !important;
    border-color: $primary-color !important;
  }
}

.filter-tabs span.active {
  background: white;
  color: $primary-color; /* 确保使用你的青绿色 */
  font-weight: 600;
}
</style>