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
        <div class="actions">
          <button class="btn-primary" @click="showModal = true">+ 新建课程包</button>
        </div>
      </header>

      <!-- 课程卡片网格 -->
      <div class="course-grid">
        <!-- 1. 新建卡片 (快捷入口) -->
        <div class="course-card create-card" @click="showModal = true">
          <span class="plus-icon">+</span>
          <span>创建新课程</span>
        </div>

        <!-- 2. 真实数据循环 -->
        <div class="course-card" v-for="course in courseList" :key="course.id">
          <!-- 封面图 -->
          <div class="card-cover">
            <img :src="course.cover || defaultCover" alt="cover" />
            <div class="overlay">
              <button class="btn-icon">✎</button>
              <button class="btn-icon delete" @click.stop="handleDelete(course.id)">🗑</button>
            </div>
          </div>
          <!-- 内容 -->
          <div class="card-body">
            <h4>{{ course.name }}</h4>
            <p class="intro">{{ course.intro || '暂无简介' }}</p>
            <div class="meta">
              <span>📅 {{ formatDate(course.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- ================= 弹窗: 新建课程 ================= -->
    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>新建课程资源</h3>
          <span class="close-btn" @click="showModal = false">×</span>
        </div>

        <div class="modal-body">
          <!-- 封面上传 -->
          <div class="form-group">
            <label>课程封面</label>
            <div class="upload-box" @click="triggerFileInput">
              <img v-if="courseForm.cover" :src="courseForm.cover" class="preview-img" />
              <div v-else class="placeholder">
                <span class="icon">📷</span>
                <span>点击上传封面</span>
              </div>
              <!-- 隐藏 input -->
              <input type="file" ref="fileInputRef" accept="image/*" style="display:none" @change="handleFileChange" />
            </div>
          </div>

          <div class="form-group">
            <label>课程名称 <span class="required">*</span></label>
            <input type="text" v-model="courseForm.name" placeholder="例如：ComfyUI 进阶工作流" />
          </div>

          <div class="form-group">
            <label>课程简介</label>
            <textarea v-model="courseForm.intro" rows="3" placeholder="这门课主要讲什么..."></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-text" @click="showModal = false">取消</button>
          <button class="btn-submit" @click="submitCreate" :disabled="isLoading">
            {{ isLoading ? '创建中...' : '立即创建' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import { getMyCourses, createCourse, deleteCourse, type CourseItem } from '@/api/content';
import { uploadImage } from '@/api/common';
import TeacherSidebar from '@/components/TeacherSidebar.vue';

const router = useRouter();
const userStore = useUserStore();

const showModal = ref(false);
const isLoading = ref(false);
const courseList = ref<CourseItem[]>([]);
const fileInputRef = ref<HTMLInputElement | null>(null);

// 表单数据
const courseForm = reactive({
  name: '',
  intro: '',
  cover: ''
});

const defaultCover = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop';

onMounted(() => {
  fetchCourses();
});

const fetchCourses = async () => {
  try {
    const res = await getMyCourses();
    courseList.value = res;
  } catch (error) {
    console.error(error);
  }
};

// 上传图片逻辑
const triggerFileInput = () => fileInputRef.value?.click();

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    try {
      // 传入 'courses' 类型，存到 static/uploads/courses/
      const res = await uploadImage(file, 'courses');
      courseForm.cover = res.url;
    } catch (error) {
      alert('上传失败');
    }
  }
};

// 提交创建
const submitCreate = async () => {
  if (!courseForm.name) return alert('请输入课程名称');
  
  isLoading.value = true;
  try {
    await createCourse(courseForm);
    alert('创建成功');
    showModal.value = false;
    // 重置
    courseForm.name = '';
    courseForm.intro = '';
    courseForm.cover = '';
    // 刷新
    fetchCourses();
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

// 删除课程
const handleDelete = async (id: number) => {
  if (!confirm('确定要删除这个课程包吗？')) return;
  try {
    await deleteCourse(id);
    fetchCourses();
  } catch (error) {
    console.error(error);
  }
};

// 简单的日期格式化
const formatDate = (isoStr: string) => {
  return new Date(isoStr).toLocaleDateString();
};

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};
</script>

<style scoped lang="scss">
/* 全局变量 */
$sidebar-width: 240px;
$primary-color: #00c9a7;
$bg-color: #f5f6fa;
$text-dark: #2d3436;
$text-gray: #a4b0be;

.dashboard-container { display: flex; width: 100vw; height: 100vh; background-color: $bg-color; font-family: 'Inter', sans-serif; overflow: hidden; }

/* Sidebar (复用) */
.sidebar { width: $sidebar-width; background: white; display: flex; flex-direction: column; padding: 30px; border-right: 1px solid #eee;
  .logo-area { display: flex; align-items: center; gap: 10px; margin-bottom: 40px; .logo-img { height: 40px; width: auto; max-width: 100%; object-fit: contain; } }
  .menu-group { margin-bottom: 30px; &.bottom { margin-top: auto; margin-bottom: 0; }
    .menu-item { display: flex; align-items: center; gap: 12px; padding: 12px 15px; color: $text-dark; text-decoration: none; font-size: 14px; font-weight: 500; border-radius: 10px; transition: all 0.3s; margin-bottom: 5px;
      &:hover { background-color: rgba(0, 201, 167, 0.1); color: $primary-color; } &.active { background-color: rgba(0, 201, 167, 0.1); color: $primary-color; border-right: 3px solid $primary-color; } } } }

/* Main Content */
.main-content { flex: 1; padding: 30px 40px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px;
  .top-bar { display: flex; justify-content: space-between; align-items: center; .breadcrumb { font-size: 14px; color: $text-gray; .current { color: $text-dark; font-weight: 600; } } .btn-primary { background: $primary-color; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; transition: filter 0.2s; &:hover { filter: brightness(0.9); } } }

  /* 卡片网格布局 */
  .course-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 25px; padding-bottom: 40px; }

  /* 课程卡片样式 */
  .course-card { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 5px 20px rgba(0,0,0,0.02); transition: transform 0.3s; cursor: pointer; border: 1px solid transparent;
    &:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.05); border-color: $primary-color; }
    
    /* 创建新课程卡片 */
    &.create-card { display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px dashed #ddd; min-height: 280px; color: $text-gray;
      .plus-icon { font-size: 40px; margin-bottom: 10px; } &:hover { border-color: $primary-color; color: $primary-color; } }

    .card-cover { height: 160px; position: relative;
      img { width: 100%; height: 100%; object-fit: cover; }
      .overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; justify-content: center; align-items: center; gap: 10px; opacity: 0; transition: opacity 0.2s; }
      &:hover .overlay { opacity: 1; }
      .btn-icon { width: 36px; height: 36px; border-radius: 50%; border: none; background: white; cursor: pointer; font-size: 16px; &:hover { background: $primary-color; color: white; } &.delete:hover { background: #e74c3c; } }
    }

    .card-body { padding: 15px;
      h4 { font-size: 16px; color: $text-dark; margin: 0 0 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .intro { font-size: 12px; color: $text-gray; height: 36px; line-height: 1.5; overflow: hidden; margin-bottom: 10px; }
      .meta { font-size: 12px; color: #ccc; } }
  }
}

/* Modal 样式 (复用之前的高级风格) */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 999; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(4px); }
.modal-content { background: white; width: 450px; border-radius: 16px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); display: flex; flex-direction: column; gap: 15px; animation: popUp 0.3s ease;
  .modal-header { display: flex; justify-content: space-between; align-items: center; h3 { margin: 0; font-size: 18px; } .close-btn { cursor: pointer; font-size: 24px; color: #999; } }
  .modal-body { display: flex; flex-direction: column; gap: 15px;
    .form-group { label { font-size: 13px; font-weight: 600; display: block; margin-bottom: 6px; color: #555; } input, textarea { width: 100%; padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; outline: none; &:focus { border-color: $primary-color; } } }
    
    /* 封面上传框 */
    .upload-box { width: 100%; height: 150px; border: 2px dashed #ddd; border-radius: 10px; display: flex; align-items: center; justify-content: center; cursor: pointer; overflow: hidden; transition: all 0.3s;
      &:hover { border-color: $primary-color; background: #f0fdfa; }
      .preview-img { width: 100%; height: 100%; object-fit: cover; }
      .placeholder { display: flex; flex-direction: column; align-items: center; color: #999; font-size: 13px; .icon { font-size: 24px; margin-bottom: 5px; } } }
  }
  .modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; button { padding: 10px 20px; border-radius: 8px; font-size: 14px; cursor: pointer; border: none; font-weight: 600; } .btn-text { background: transparent; color: #666; } .btn-submit { background: $primary-color; color: white; &:hover { filter: brightness(0.9); } } }
}
@keyframes popUp { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>