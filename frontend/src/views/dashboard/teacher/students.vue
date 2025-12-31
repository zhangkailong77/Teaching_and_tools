<template>
  <div class="dashboard-container">
    
    <!-- 1. 左侧 Sidebar (同步你的 index.vue 样式) -->
    <TeacherSidebar />

    <!-- 2. 中间主内容区 (表格布局) -->
    <main class="main-content">
      <header class="top-bar">
        <div class="breadcrumb">
          <span>教学管理</span> / <span class="current">学生名单</span>
        </div>
        <div class="actions">
          <el-select 
            v-model="selectedClassId" 
            placeholder="全部班级" 
            class="class-filter"
            size="default"
            clearable
          >
            <!-- 手动加一个“全部班级”选项，或者利用 clearable 清空 -->
            <el-option label="全部班级" value="" />
            
            <el-option 
              v-for="cls in classList" 
              :key="cls.id" 
              :label="cls.name" 
              :value="cls.id" 
            />
          </el-select>

          <div class="search-box">
            <span class="icon">🔍</span>
            <input type="text" v-model="searchText" placeholder="搜索姓名或学号..." />
          </div>
          <button class="btn-primary" @click="openAddStudentModal">+ 添加学生</button>
        </div>
      </header>

      <!-- 表格区域 -->
      <div class="table-container">
        <table class="student-table">
          <thead>
            <tr>
              <th>学生信息</th>
              <th>学号</th>
              <th>所属班级</th>
              <th>学习进度</th>
              <th>加入时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.id">
              <td>
                <div class="user-info">
                  <img :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=${student.id}`" alt="" class="avatar">
                  <span class="name">{{ student.name }}</span>
                </div>
              </td>
              <td class="code">{{ student.code }}</td>
              <td>
                <!-- 这里为了好看，使用了主题色的变体，实际可调整 -->
                <span class="class-tag" :style="{ color: student.classColor, background: student.classBg }">
                  {{ student.className }}
                </span>
              </td>
              <td>
                <div class="progress-bar">
                  <div class="fill" :style="{ width: student.progress + '%' }"></div>
                </div>
                <span class="progress-num">{{ student.progress }}%</span>
              </td>
              <td class="date">{{ student.joinDate }}</td>
              <td>
                <span class="status-badge" :class="student.status">
                  {{ student.status === 'active' ? '正常' : '休学' }}
                </span>
              </td>
              <td>
                <button class="action-btn edit">编辑</button>
                <button class="action-btn delete">移除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination">
        <span>共 4 条数据</span>
        <div class="pages">
          <button disabled>&lt;</button>
          <button class="active">1</button>
          <button>2</button>
          <button>3</button>
          <button>&gt;</button>
        </div>
      </div>

    </main>

    <!-- 弹窗 1: 添加学生 -->
    <div class="modal-overlay" v-if="showStudentModal" @click.self="showStudentModal = false">
      <div class="modal-content">
        
        <!-- 标题栏 -->
        <div class="modal-header">
          <div class="header-left">
            <span class="icon-bg">🎓</span>
            <h3>添加新学员</h3>
          </div>
          <span class="close-btn" @click="showStudentModal = false">×</span>
        </div>

        <!-- 表单内容 -->
        <div class="modal-body">
          
          <!-- 班级选择 (置顶) -->
          <div class="form-group">
            <label>归属班级 <span class="required">*</span></label>
            <div class="select-wrapper">
              <select v-model="studentForm.classId">
                <option disabled value="">请选择班级...</option>
                <option v-for="cls in classList" :key="cls.id" :value="cls.id">
                  {{ cls.name }}
                </option>
              </select>
              <span class="arrow">▼</span>
            </div>
            <p class="hint" v-if="classList.length === 0">⚠️ 暂无班级，请先点击右上角“新建班级”</p>
          </div>

          <!-- 姓名 & 学号 (双列布局) -->
          <div class="form-row">
            <div class="form-group">
              <label>真实姓名 <span class="required">*</span></label>
              <input type="text" v-model="studentForm.fullName" placeholder="例：张三" />
            </div>
            <div class="form-group">
              <label>学号 <span class="required">*</span></label>
              <input type="text" v-model="studentForm.studentNumber" placeholder="例：2023001" />
            </div>
          </div>

          <!-- 手机号 -->
          <div class="form-group">
            <label>手机号 (作为登录账号) <span class="required">*</span></label>
            <div class="input-with-icon">
              <input type="text" v-model="studentForm.username" placeholder="请输入11位手机号" />
              <span class="icon">📱</span>
            </div>
            <p class="info-text">💡 初始密码默认为: <strong>123456</strong></p>
          </div>

        </div>

        <!-- 底部按钮 -->
        <div class="modal-footer">
          <button class="btn-text" @click="showStudentModal = false">取消</button>
          <button class="btn-submit" @click="submitAddStudent" :disabled="isLoading">
            {{ isLoading ? '提交中...' : '确认添加' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import { getMyCourses, type CourseItem } from '@/api/content';
import { getMyClasses, createClass, addStudentToClass, getMyStudents, type ClassItem, type StudentItem } from '@/api/course';
import TeacherSidebar from '@/components/TeacherSidebar.vue';

const router = useRouter();
const userStore = useUserStore();

// --- 状态管理 ---
const searchText = ref('');
const isLoading = ref(false);
const showStudentModal = ref(false);
const showClassModal = ref(false);
const classList = ref<ClassItem[]>([]); // 存储从后端拉取的班级列表
const selectedClassId = ref<number | string>(''); 
const courseLibrary = ref<CourseItem[]>([]);

// 表单数据
const studentForm = reactive({ 
  classId: '', 
  username: '',
  fullName: '',      // ✅ 新增
  studentNumber: ''  // ✅ 新增
});

const dateConfig = {
  mode: 'dateTime',       // ✅ 关键：开启时间选择模式
  mask: 'YYYY-MM-DD HH:mm', // 输入框显示的格式
};

// 修改 formatDate 函数
const formatDate = (val: any) => {
  if (!val) return undefined;
  if (val instanceof Date) {
    return val.toISOString(); 
  }
  return val;
};

const students = ref<StudentItem[]>([]);

const filteredStudents = computed(() => {
  let data = students.value;

  // 1. 先按班级筛选
  if (selectedClassId.value !== '') {
    // 找到当前选中的班级对象
    const targetClass = classList.value.find(c => c.id === Number(selectedClassId.value));
    if (targetClass) {
      // 对比班级名称 (因为 fetchStudentList 里把后端 class_name 映射为了 className)
      data = data.filter(s => s.className === targetClass.name);
    }
  }

  // 2. 再按关键字搜索
  if (searchText.value) {
    const lowerText = searchText.value.toLowerCase(); // 建议转小写比较
    data = data.filter(s => 
      s.name.includes(searchText.value) || 
      s.code.includes(searchText.value) ||
      // 建议顺便把手机号(username)也加入搜索
      s.username.includes(searchText.value)
    );
  }
  
  return data;
});

const fetchStudentList = async () => {
  try {
    const res = await getMyStudents();
    // 为数据添加一些前端显示的颜色 (模拟)
    students.value = res.map(s => ({
      ...s,
      // 这里的 name 映射后端返回的 full_name
      name: s.full_name || s.username, 
      code: s.student_number || '无学号',
      className: s.class_name,
      joinDate: new Date(s.joined_at).toLocaleDateString(), // 格式化时间
      status: s.is_active ? 'active' : 'inactive',
      // 给班级标签随机配个色，或者固定色
      classColor: '#00c9a7',
      classBg: '#e0f2f1'
    }));
  } catch (error) {
    console.error("获取学生列表失败", error);
  }
};

onMounted(() => {
  // 拉取班级列表 (给弹窗用)
  getMyClasses().then(res => classList.value = res);
  // 拉取学生列表 (给表格用)
  fetchStudentList();
});

// 1. 打开“添加学生”弹窗前，先去拉取最新的班级列表
const openAddStudentModal = async () => {
  try {
    const res = await getMyClasses();
    classList.value = res;
    // 如果只有一个班，自动选中
    if (res.length > 0) studentForm.classId = res[0].id;
    showStudentModal.value = true;
  } catch (error) {
    console.error(error);
  }
};

// 2. 提交添加学生
const submitAddStudent = async () => {
  // 校验必填
  if (!studentForm.classId || !studentForm.username || !studentForm.fullName || !studentForm.studentNumber) {
    alert('请填写完整信息（姓名、学号、手机号）');
    return;
  }
  
  isLoading.value = true;
  try {
    await addStudentToClass(Number(studentForm.classId), {
      username: studentForm.username,
      full_name: studentForm.fullName,
      student_number: studentForm.studentNumber
    });

    alert('添加成功！');
    showStudentModal.value = false;
    // 清空表单
    studentForm.username = '';
    studentForm.fullName = '';
    studentForm.studentNumber = '';

    fetchStudentList(); // 刷新学生列表
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped lang="scss">
/* --- 全局变量 (同步你的 index.vue) --- */
$sidebar-width: 240px;
$primary-purple: #00c9a7; /* ✅ 更新为青绿色 */
$primary-color: #00c9a7;
$bg-color: #f5f6fa;
$text-dark: #2d3436;
$text-gray: #a4b0be;

.dashboard-container {
  display: flex; width: 100vw; height: 100vh; background-color: $bg-color; font-family: 'Inter', sans-serif; overflow: hidden;
}

/* --- Sidebar (同步样式) --- */
.sidebar {
  width: $sidebar-width; background: white; display: flex; flex-direction: column; padding: 30px; border-right: 1px solid #eee;
  
  .logo-area { 
    display: flex; align-items: center; gap: 10px; margin-bottom: 40px; 
    /* ✅ 同步图片样式 */
    .logo-img {
      height: 40px; 
      width: auto; 
      max-width: 100%; 
      object-fit: contain;
    }
  }
  
  .menu-group {
    margin-bottom: 30px; &.bottom { margin-top: auto; margin-bottom: 0; }
    .menu-title { font-size: 12px; color: $text-gray; margin-bottom: 15px; font-weight: 600; }
    .menu-item {
      display: flex; align-items: center; gap: 12px; padding: 12px 15px; color: $text-dark; text-decoration: none; font-size: 14px; font-weight: 500; border-radius: 10px; transition: all 0.3s; margin-bottom: 5px; position: relative;
      &:hover { background-color: rgba(0, 201, 167, 0.1); color: $primary-purple; }
      &.active { background-color: rgba(0, 201, 167, 0.1); color: $primary-purple; border-right: 3px solid $primary-purple; }
      &.logout:hover { color: #e74c3c; background: rgba(231, 76, 60, 0.1); }
      .badge { background: #e74c3c; color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px; margin-left: auto; }
    }
  }
}

/* --- Main Content (表格特有样式) --- */
.main-content {
  flex: 1; padding: 30px 40px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px;

  /* 顶部操作栏 */
  .top-bar {
    display: flex; justify-content: space-between; align-items: center;
    .breadcrumb { font-size: 14px; color: $text-gray; .current { color: $text-dark; font-weight: 600; } }
    .actions {
      display: flex; gap: 15px;
      .search-box {
        background: white; padding: 8px 15px; border-radius: 8px; display: flex; align-items: center; gap: 10px; border: 1px solid #eee;
        input { border: none; outline: none; font-size: 13px; width: 200px; }
      }
      button { padding: 8px 16px; border-radius: 8px; font-size: 13px; cursor: pointer; border: none; font-weight: 500; }
      
      /* ✅ 修复 Button Hover 警告 */
      .btn-primary { 
        background: $primary-purple; 
        color: white; 
        transition: filter 0.2s;
        &:hover { filter: brightness(0.9); } 
      }
      
      .btn-outline { background: white; border: 1px solid #ddd; color: $text-dark; &:hover { border-color: $primary-purple; color: $primary-purple; } }
    }
  }

  /* 表格容器 */
  .table-container {
    background: white; border-radius: 15px; padding: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.02); min-height: 500px;
    
    .student-table {
      width: 100%; border-collapse: collapse;
      th { text-align: left; color: $text-gray; font-size: 12px; font-weight: 500; padding: 15px; border-bottom: 1px solid #eee; }
      td { padding: 15px; font-size: 14px; color: $text-dark; border-bottom: 1px solid #f9f9f9; vertical-align: middle; }
      tbody tr:hover { background-color: #f8f9fc; }

      .user-info {
        display: flex; align-items: center; gap: 10px;
        .avatar { width: 32px; height: 32px; border-radius: 50%; }
        .name { font-weight: 600; }
      }
      .code { font-family: monospace; color: $text-gray; }
      .class-tag { font-size: 12px; padding: 4px 8px; border-radius: 6px; font-weight: 500; }
      
      .progress-bar {
        width: 100px; height: 6px; background: #eee; border-radius: 3px; display: inline-block; margin-right: 8px;
        .fill { height: 100%; background: $primary-purple; border-radius: 3px; }
      }
      .progress-num { font-size: 12px; color: $text-gray; }
      
      .status-badge {
        font-size: 12px; padding: 4px 10px; border-radius: 12px;
        &.active { background: #e3f9f5; color: #00b894; }
        &.inactive { background: #ffebee; color: #e74c3c; }
      }

      .action-btn { background: none; border: none; font-size: 12px; cursor: pointer; margin-right: 10px; }
      .edit { color: $primary-purple; }
      .delete { color: #e74c3c; }
    }
  }

  /* 分页 */
  .pagination {
    display: flex; justify-content: space-between; align-items: center; color: $text-gray; font-size: 13px;
    .pages button {
      width: 30px; height: 30px; border: 1px solid #eee; background: white; margin-left: 5px; border-radius: 6px; cursor: pointer;
      &.active { background: $primary-purple; color: white; border-color: $primary-purple; }
      &:disabled { opacity: 0.5; cursor: not-allowed; }
    }
  }
}

/* ================= 弹窗样式 (Modal) ================= */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(20, 20, 25, 0.6); /* 深色半透明背景 */
  z-index: 999;
  display: flex; justify-content: center; align-items: center;
  backdrop-filter: blur(8px); /* 磨砂玻璃效果 */
  animation: fadeIn 0.2s ease-out;
}

.modal-content {
  background: white;
  width: 480px; /* 稍微宽一点 */
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  animation: popUp 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28); /* 弹性弹出动画 */
  display: flex; flex-direction: column; gap: 20px;

  /* --- 头部 --- */
  .modal-header {
    display: flex; justify-content: space-between; align-items: center;
    .header-left {
      display: flex; align-items: center; gap: 12px;
      .icon-bg {
        width: 36px; height: 36px; background: #e0f2f1; border-radius: 10px;
        display: flex; align-items: center; justify-content: center; font-size: 18px;
      }
      h3 { margin: 0; font-size: 18px; font-weight: 700; color: $text-dark; }
    }
    .close-btn {
      font-size: 24px; color: #ccc; cursor: pointer; line-height: 1; transition: color 0.2s;
      &:hover { color: $text-dark; }
    }
  }

  /* --- 表单主体 --- */
  .modal-body {
    display: flex; flex-direction: column; gap: 18px;

    .form-row {
      display: flex; gap: 20px;
      .form-group { flex: 1; }
    }

    .form-group {
      display: flex; flex-direction: column; gap: 8px;
      label {
        font-size: 13px; font-weight: 600; color: #555;
        .required { color: #ff4d4f; margin-left: 4px; }
      }

      input, select {
        width: 100%; padding: 12px 15px;
        background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 10px;
        font-size: 14px; color: $text-dark; transition: all 0.3s;
        
        &:hover { background: #fff; border-color: #ccc; }
        &:focus { 
          background: #fff; 
          border-color: $primary-color; 
          box-shadow: 0 0 0 4px rgba($primary-color, 0.1); /* 聚焦光环 */
          outline: none;
        }
      }

      /* 自定义 Select 下拉箭头 */
      .select-wrapper {
        position: relative;
        select { appearance: none; cursor: pointer; }
        .arrow {
          position: absolute; right: 15px; top: 50%; transform: translateY(-50%);
          font-size: 10px; color: #999; pointer-events: none;
        }
      }

      /* 带图标的输入框 */
      .input-with-icon {
        position: relative;
        input { padding-right: 40px; }
        .icon {
          position: absolute; right: 15px; top: 50%; transform: translateY(-50%);
          font-size: 16px; opacity: 0.5;
        }
      }

      .info-text { font-size: 12px; color: #888; margin-top: 4px; }
      .hint { font-size: 12px; color: #ff9800; margin-top: 4px; }
    }
  }

  /* --- 底部按钮 --- */
  .modal-footer {
    display: flex; justify-content: flex-end; gap: 15px; margin-top: 10px;
    
    button {
      padding: 12px 24px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s;
    }

    .btn-text {
      background: transparent; border: none; color: #666;
      &:hover { background: #f5f5f5; color: #333; }
    }

    .btn-submit {
      background: $primary-color; color: white; border: none;
      box-shadow: 0 4px 12px rgba($primary-color, 0.3);
      &:hover { filter: brightness(0.9); transform: translateY(-1px); }
      &:active { transform: translateY(0); }
      &:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
    }
  }
}

/* 动画定义 */
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes popUp { 
  0% { opacity: 0; transform: scale(0.9) translateY(20px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.class-filter {
  width: 160px; /* 固定宽度，不用太宽 */
  margin-right: 12px; /* 和搜索框保持间距 */

  /* 深度选择器：修改内部输入框样式，使其跟你的搜索框风格一致 */
  :deep(.el-input__wrapper) {
    box-shadow: 0 0 0 1px #eee inset !important; /* 浅边框 */
    border-radius: 8px; /* 圆角 */
    padding: 4px 12px;
    background-color: white;
    
    /* 悬停时 */
    &:hover {
      box-shadow: 0 0 0 1px #ccc inset !important;
    }
    
    /* 聚焦时 (变青绿色) */
    &.is-focus {
      box-shadow: 0 0 0 1px $primary-color inset !important;
    }
  }
}
</style>