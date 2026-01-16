<template>
  <div class="dashboard-container">
    <TeacherSidebar />

    <main class="main-content">
      <header class="top-bar">
        <div class="breadcrumb">
          <span>教学管理</span> / <span class="current">班级管理</span>
        </div>

        <div class="status-tabs">
          <span :class="{ active: currentTabStatus === 0 }" @click="switchTab(0)">进行中</span>
          <span :class="{ active: currentTabStatus === 1 }" @click="switchTab(1)">已归档</span>
        </div>
        
        <div class="actions">
          <button class="btn-primary" @click="openModal('create')">+ 新建班级</button>
        </div>
      </header>

      <!-- 班级列表 (表格形式) -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th width="70" style="text-align: center;">封面</th>
              <th width="150" style="text-align: center;">班级名称</th>
              <th>绑定课程包</th>
              <th width="80" style="text-align: center;">学生数</th>
              <th width="220" style="text-align: center;">教学周期</th>
              <th width="260" style="text-align: center;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cls in classList" :key="cls.id">
              <td>
                <div class="table-cover" :style="{ backgroundImage: `url(${cls.cover_image})` }">
                  <span v-if="!cls.cover_image">{{ cls.name.charAt(0) }}</span>
                </div>
              </td>
              <td>
                <div class="cls-name">{{ cls.name }}</div>
                <div class="cls-desc">{{ cls.description || '暂无描述' }}</div>
              </td>
              <td>
                <div class="tags">
                  <span v-if="cls.bound_course_names.length === 0" class="tag gray">未绑定</span>
                  <span v-else v-for="(cname, idx) in cls.bound_course_names" :key="idx" class="tag green">
                    {{ cname }}
                  </span>
                </div>
              </td>
              <td align="center">
                <span class="num-text">{{ cls.student_count }} 人</span>
              </td>
              <td class="date-col" align="center">
                <div class="date-box-inline"> 
                  <span>{{ formatDateShort(cls.start_date) }}</span>
                  <span class="date-sep">至</span>
                  <span>{{ formatDateShort(cls.end_date) }}</span>
                </div>
              </td>
              <td>
                <div class="action-btns" style="justify-content: center;">
                  <button class="btn-text primary" @click="handleEnterClass(cls)">进入班级</button>
                  <span style="color: #eee; margin: 0 8px;">|</span>
                  
                  <button class="btn-text edit" @click="openModal('edit', cls)">编辑</button>
                  <button 
                    v-if="currentTabStatus === 0" 
                    class="btn-text delete" 
                    @click="handleArchive(cls, 1)"
                  >归档</button>
                  <button 
                    v-else 
                    class="btn-text restore" 
                    @click="handleArchive(cls, 0)"
                  >恢复</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <!-- ✅ 修改后的学员列表侧边抽屉 -->
    <el-drawer
      v-model="showDrawer"
      direction="rtl"
      size="600px"
    >
      <!-- 自定义头部：包含标题和添加按钮 -->
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; padding-right: 20px;">
          <span style="font-weight: bold; font-size: 18px; color: #333;">【{{ activeClassName }}】学员名单</span>
          <!-- 此处 click 事件需对应你 script 中的添加逻辑 -->
          <button class="btn-primary" style="padding: 6px 12px; font-size: 12px;" @click="addStudentInDrawer">
            + 添加学员
          </button>
        </div>
      </template>

      <div v-loading="drawerLoading" style="padding: 0 10px;">
        <!-- 空状态 -->
        <div v-if="currentClassStudents.length === 0" style="text-align: center; margin-top: 100px; color: #999;">
          <p>📭 该班级暂无学生</p>
        </div>
        
        <!-- 学生表格 -->
        <table class="drawer-table" v-else>
          <thead>
            <tr>
              <th>学生</th>
              <th>学号</th>
              <th>手机号</th> <!-- ✅ 新增列 -->
              <th>加入时间</th>
              <th>操作</th>   <!-- ✅ 新增列 -->
            </tr>
          </thead>
          <tbody>
            <tr v-for="stu in currentClassStudents" :key="stu.id">
              <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                  <img :src="`https://api.dicebear.com/7.x/avataaars/svg?seed=${stu.id}`" style="width: 28px; border-radius: 50%;" />
                  <span>{{ stu.full_name || stu.username }}</span>
                </div>
              </td>
              <td>{{ stu.student_number || '-' }}</td>
              <!-- ✅ 显示手机号 (username) -->
              <td style="font-size: 13px; color: #666;">{{ stu.username }}</td> 
              <td style="font-size: 12px; color: #999;">{{ new Date(stu.joined_at).toLocaleDateString() }}</td>
              <td>
                <!-- ✅ 新增：移除按钮 -->
                <!-- 此处 click 事件需对应你 script 中的移除逻辑 -->
                <button class="btn-text delete" @click="handleRemoveStudent(stu.id)">移除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </el-drawer>

    <!-- 编辑/新建 弹窗 -->
    <div class="modal-overlay modal-class-edit" v-if="showModal" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ isEditMode ? '编辑班级信息' : '新建教学班级' }}</h3>
          <span class="close" @click="showModal = false">×</span>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>班级名称 <span class="required">*</span></label>
            <input type="text" v-model="form.name" placeholder="请输入班级名称" />
          </div>

          <div class="form-group">
            <label>班级封面</label>
            <div class="cover-selector">
              <div 
                v-for="(img, index) in coverOptions" 
                :key="index"
                class="cover-item"
                :class="{ active: form.coverImage === img }"
                @click="form.coverImage = img"
              >
                <img :src="img" />
                <div class="check-mark" v-if="form.coverImage === img">✓</div>
              </div>
            </div>
          </div>
          
          <!-- 多选课程绑定 -->
          <div class="form-group">
            <label>绑定课程资源 (支持多选)</label>
            <el-select 
              v-model="form.courseIds" 
              multiple 
              placeholder="请选择课程包" 
              style="width: 100%;"
              size="large"
              :teleported="true"
              popper-class="class-select-dropdown"
            >
              <el-option 
                v-for="c in courseLibrary" 
                :key="c.id" 
                :label="c.name" 
                :value="c.id" 
              />
            </el-select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>开课时间</label>
              <v-date-picker v-model="form.startDate" mode="dateTime" is24hr :model-config="dateConfig" color="teal" :popover="{ visibility: 'click', placement: 'top', keepVisibleOnInput: true }">
                <template #default="{ inputValue, inputEvents }">
                  <div class="input-with-icon">
                    <input :value="inputValue" v-on="inputEvents" placeholder="选择时间" readonly />
                    <span class="icon">⏰</span>
                  </div>
                </template>
              </v-date-picker>
            </div>
            <div class="form-group">
              <label>结课时间</label>
              <v-date-picker v-model="form.endDate" mode="dateTime" is24hr :model-config="dateConfig" color="teal" :popover="{ visibility: 'click', placement: 'top', keepVisibleOnInput: true }">
                <template #default="{ inputValue, inputEvents }">
                  <div class="input-with-icon">
                    <input :value="inputValue" v-on="inputEvents" placeholder="选择时间" readonly />
                    <span class="icon">🏁</span>
                  </div>
                </template>
              </v-date-picker>
            </div>
          </div>

          <div class="form-group">
            <label>描述</label>
            <input type="text" v-model="form.description" placeholder="简单描述一下..." />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showModal = false">取消</button>
          <button class="btn-confirm" @click="submitForm">保存</button>
        </div>
      </div>
    </div>
  </div>

  <!-- ================= 2. 添加学生弹窗 (必须补全这块) ================= -->
    <div class="modal-overlay modal-student-add" v-if="showStudentModal" @click.self="showStudentModal = false">
      <div class="modal-content" style="width: 480px;">
        
        <div class="modal-header">
          <div class="header-left">
            <span class="icon-bg" style="background: #e0f2f1; color: #00c9a7;">🎓</span>
            <h3>添加新学员</h3>
          </div>
          <span class="close-btn" @click="showStudentModal = false">×</span>
        </div>

        <div class="modal-body">
          <!-- 锁定显示当前班级 -->
          <div class="form-group">
            <label>目标班级</label>
            <input type="text" :value="activeClassName" disabled style="background:#f5f5f5; cursor:not-allowed; color:#999;" />
          </div>

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

          <div class="form-group">
            <label>手机号 (作为登录账号) <span class="required">*</span></label>
            <div class="input-with-icon">
              <input type="text" v-model="studentForm.username" placeholder="请输入11位手机号" />
              <span class="icon">📱</span>
            </div>
            <p class="hint" style="font-size:12px;color:#999;margin-top:5px">默认密码: 123456</p>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-text" @click="showStudentModal = false">取消</button>
          <button class="btn-submit" @click="submitAddStudent" :disabled="isLoading">
            {{ isLoading ? '提交中...' : '确认添加' }}
          </button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import TeacherSidebar from '@/components/TeacherSidebar.vue';
// 确保引入了所有需要的 API
import { 
  getMyClasses, 
  createClass, 
  updateClass, 
  getMyStudents, 
  removeStudentFromClass, 
  addStudentToClass, 
  updateClassStatus,
  type ClassItem, 
  type StudentItem
} from '@/api/course';
import { getMyCourses, type CourseItem } from '@/api/content';
import { uploadImage } from '@/api/common'; // 如果需要上传封面，记得引入这个

// --- 状态定义 ---
const classList = ref<ClassItem[]>([]);
const courseLibrary = ref<CourseItem[]>([]);
const showModal = ref(false); // 班级编辑/新建弹窗
const isEditMode = ref(false);
const currentId = ref<number | null>(null); // 编辑班级时的临时ID
const isLoading = ref(false); // ✅ 新增：通用加载状态(防止按钮重复点击)
const currentTabStatus = ref(0)

// 抽屉相关状态
const showDrawer = ref(false);
const drawerLoading = ref(false);
const activeClassName = ref('');
const currentClassId = ref<number | null>(null);
const currentClassStudents = ref<StudentItem[]>([]);

// ✅ 新增：添加学生弹窗的状态
const showStudentModal = ref(false);
const studentForm = reactive({ 
  classId: '', 
  username: '', 
  fullName: '', 
  studentNumber: '' 
});

// 班级表单数据
const form = reactive({
  name: '',
  description: '',
  courseIds: [] as number[],
  startDate: '',
  endDate: '',
  coverImage: ''
});

const coverOptions = [
  'https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=300&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=300&auto=format&fit=crop',
  'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop'
];

const dateConfig = { type: 'string', mask: 'YYYY-MM-DD HH:mm' };

const formatDateShort = (val: any) => {
  if (!val) return '--';
  return String(val).split('T')[0];
};

// --- 初始化 ---
onMounted(() => {
  fetchData();
});

const switchTab = (status: number) => {
  currentTabStatus.value = status
  fetchData() // 重新调用 API
}

const fetchData = async () => {
  try {
    const [classes, courses] = await Promise.all([
      getMyClasses({ status: currentTabStatus.value }), 
      getMyCourses()
    ]);
    classList.value = classes;
    courseLibrary.value = courses;
  } catch (e) { console.error(e); }
};

// 归档/恢复 处理函数
const handleArchive = async (cls: ClassItem, targetStatus: number) => {
  const actionText = targetStatus === 1 ? '归档' : '恢复';
  const confirmMsg = targetStatus === 1 
    ? `确定要归档【${cls.name}】吗？\n归档后班级将进入历史库，不再出现在工作台。`
    : `确定要恢复【${cls.name}】吗？`;

  if (!confirm(confirmMsg)) return;

  try {
    await updateClassStatus(cls.id, targetStatus);
    alert(`${actionText}成功`);
    fetchData(); // 刷新列表
  } catch (e) {
    console.error(e);
  }
};

// --- 班级管理逻辑 ---

const openModal = (type: 'create' | 'edit', data?: ClassItem) => {
  isEditMode.value = type === 'edit';
  if (type === 'edit' && data) {
    currentId.value = data.id;
    form.name = data.name;
    form.description = data.description || '';
    form.coverImage = data.cover_image || coverOptions[0];
    form.courseIds = data.bound_course_ids || [];
    form.startDate = data.start_date || '';
    form.endDate = data.end_date || '';
  } else {
    currentId.value = null;
    form.name = '';
    form.description = '';
    form.courseIds = [];
    form.startDate = '';
    form.endDate = '';
    form.coverImage = coverOptions[0];
  }
  showModal.value = true;
};

const submitForm = async () => {
  const payload = {
    name: form.name,
    description: form.description,
    course_ids: form.courseIds,
    start_date: formatDate(form.startDate),
    end_date: formatDate(form.endDate),
    cover_image: form.coverImage
  };

  isLoading.value = true;
  try {
    if (isEditMode.value && currentId.value) {
      await updateClass(currentId.value, payload);
      alert('修改成功');
    } else {
      await createClass(payload);
      alert('创建成功');
    }
    showModal.value = false;
    fetchData();
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

// --- 封面上传逻辑 (如果你模板里用了 triggerFileInput) ---
const fileInputRef = ref<HTMLInputElement | null>(null);
const triggerFileInput = () => fileInputRef.value?.click();
const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    try {
      const res = await uploadImage(input.files[0], 'courses');
      form.coverImage = res.url;
    } catch(e) { alert('上传失败'); }
  }
};

// --- 学员管理逻辑 (抽屉) ---

// 1. 进入班级
const handleEnterClass = async (cls: ClassItem) => {
  currentClassId.value = cls.id;
  activeClassName.value = cls.name;
  showDrawer.value = true;
  refreshDrawerStudents();
};

// 2. 刷新抽屉里的学生列表
const refreshDrawerStudents = async () => {
  if (!currentClassId.value) return;
  
  drawerLoading.value = true;
  try {
    // ✅ 核心修改：直接传 class_id 给后端，后端去查，不用前端 filter
    // 另外，我们希望在抽屉里显示所有学生，所以把 limit 设大一点（比如 100）
    const res = await getMyStudents({
      class_id: currentClassId.value,
      page: 1,
      limit: 100 
    });
    
    // ✅ 核心修改：适配新的返回结构 { total, items }
    // 如果 getMyStudents 返回的是 { total, items }
    if (res.items) {
      currentClassStudents.value = res.items;
    } else {
      // 兼容旧接口（虽然应该已经改了）
      currentClassStudents.value = Array.isArray(res) ? res : [];
    }
    
  } catch (error) {
    console.error("获取班级学生失败", error);
    currentClassStudents.value = [];
  } finally {
    drawerLoading.value = false;
  }
};

// 3. 移除学生
const handleRemoveStudent = async (studentId: number) => {
  if (!confirm('确定将该学生移出本班级吗？')) return;
  try {
    // 🔄 修改：这里必须用 currentClassId.value (抽屉对应的班级)，不能用 currentId (编辑表单用的)
    await removeStudentFromClass(currentClassId.value!, studentId);
    await refreshDrawerStudents();
    fetchData(); // 刷新外层人数
  } catch (error) {
    console.error(error);
  }
};

// 4. 打开添加学生弹窗
const addStudentInDrawer = () => {
  if (!currentClassId.value) return;
  // 自动填入当前班级ID
  studentForm.classId = String(currentClassId.value);
  showStudentModal.value = true;
};

// ✅ 新增：提交添加学生 (你之前漏了这个函数)
const submitAddStudent = async () => {
  if (!studentForm.username || !studentForm.fullName || !studentForm.studentNumber) {
    alert('请填写完整信息');
    return;
  }
  
  isLoading.value = true;
  try {
    await addStudentToClass(Number(studentForm.classId), {
      username: studentForm.username,
      full_name: studentForm.fullName,
      student_number: studentForm.studentNumber
    });

    alert('学员添加成功');
    showStudentModal.value = false;
    
    // 清空
    studentForm.username = '';
    studentForm.fullName = '';
    studentForm.studentNumber = '';

    // 刷新数据
    await refreshDrawerStudents();
    fetchData();
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

// 工具函数
const formatDate = (val: any) => {
  if (!val) return undefined;
  if (val instanceof Date) return val.toISOString();
  return val;
};
const getTodayString = () => {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hour = String(date.getHours()).padStart(2, '0');
  const min = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day} ${hour}:${min}`;
};
</script>

<style scoped lang="scss">
$sidebar-width: 240px;
$primary-color: #00c9a7;
$bg-color: #f5f6fa;

.dashboard-container { display: flex; width: 100vw; height: 100vh; background-color: $bg-color; font-family: 'Inter', sans-serif; overflow: hidden; }
.main-content { flex: 1; padding: 30px; overflow-y: auto; }

.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
  .breadcrumb { font-size: 14px; color: #888; .current { color: #333; font-weight: 600; } }
  .btn-primary { background: $primary-color; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
}

/* 表格样式 */
.table-container { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
.data-table { width: 100%; border-collapse: collapse; table-layout: fixed; 
  th { text-align: left; padding: 15px; color: #888; font-size: 13px; border-bottom: 1px solid #eee; }
  td { padding: 15px; border-bottom: 1px solid #f5f5f5; font-size: 14px; vertical-align: middle; }
  .table-cover { width: 50px; height: 50px; border-radius: 8px; background-color: #ddd; background-size: cover; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }
  .cls-name { font-weight: 600; color: #333; }
  .cls-desc { font-size: 12px; color: #999; margin-top: 4px; }
  .tags { display: flex; flex-wrap: wrap; gap: 5px; 
    .tag { padding: 2px 8px; border-radius: 4px; font-size: 12px; 
      &.green { background: #e0f2f1; color: $primary-color; } 
      &.gray { background: #f0f0f0; color: #999; }
    }
  }
  .btn-text { background: none; border: none; cursor: pointer; font-size: 13px; margin-right: 10px; 
    &.edit { color: $primary-color; } &.delete { color: #ff6b6b; }
    &.primary {
    color: $primary-color;
    font-weight: 700; /* 加粗一点，突出它是主要操作 */
    &:hover { text-decoration: underline; }
  }
  }
  .divider {
  color: #eee;
  margin: 0 8px;
}
}

/* 弹窗通用样式 */
.modal-overlay {
  position: fixed; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 100%; 
  background: rgba(0, 0, 0, 0.5); 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  backdrop-filter: blur(4px);
}

.modal-class-edit {
  z-index: 2000;
}

.modal-student-add {
  z-index: 2200;
}
.modal-content { 
  background: white; 
  width: 500px; 
  padding: 25px; 
  border-radius: 16px; 
  display: flex; 
  flex-direction: column; 
  gap: 15px; 
  
  /* ✅ 修改部分：头部与关闭按钮 */
  .modal-header { 
    position: relative; /* 给绝对定位做参考 */
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    margin-bottom: 5px;

    h3 { margin: 0; font-size: 18px; font-weight: bold; } 

    /* 注意：请确认你的 HTML 标签 class 是 "close" 还是 "close-btn" */
    /* 这里对应你提供的代码写的是 .close */
    .close { 
      position: absolute; /* 强制固定在右上角，防止被挤压 */
      right: 0;           /* 靠右 */
      top: -2px;          /* 靠上微调 */
      
      width: 30px;        /* ✅ 关键：设置固定的点击区域大小 */
      height: 30px;
      line-height: 30px;  /* 文字垂直居中 */
      text-align: center; /* 文字水平居中 */
      
      cursor: pointer; 
      font-size: 24px; 
      color: #999; 
      z-index: 10;        /* 确保在最上层 */
      transition: all 0.2s;

      /* 鼠标放上去的效果 */
      &:hover { 
        color: #333; 
        background-color: #f5f5f5; 
        border-radius: 50%;
      }
    } 
  }

  /* 下面的代码保持原样 */
  .form-group { label { display: block; font-size: 13px; margin-bottom: 5px; color: #666; font-weight: 600; } input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; outline: none; &:focus { border-color: $primary-color; } } }
  .form-row { display: flex; gap: 15px; .form-group { flex: 1; } .date-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; cursor: pointer; } }
  .modal-footer { display: flex; justify-content: flex-end; gap: 10px; button { padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; } .btn-cancel { background: #f5f5f5; color: #666; } .btn-confirm { background: $primary-color; color: white; } }
}
/* 修复 Element Plus Select 样式 */
.custom-select { width: 100%; }

/* 封面选择器样式 */
.cover-selector {
  display: flex; gap: 10px; margin-top: 5px;
  .cover-item {
    width: 60px; height: 40px; border-radius: 6px; overflow: hidden; cursor: pointer; position: relative; border: 2px solid transparent; transition: all 0.2s;
    img { width: 100%; height: 100%; object-fit: cover; }
    &:hover { transform: scale(1.05); }
    &.active { 
      border-color: $primary-color; 
      .check-mark { position: absolute; inset: 0; background: rgba(0, 201, 167, 0.4); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; } 
    }
  }
}

/* 修复日期输入框图标样式 */
.input-with-icon {
  position: relative;
  input { padding-right: 35px; width: 100%; border: 1px solid #e0e0e0; padding: 10px 12px; border-radius: 8px; outline: none; &:focus { border-color: $primary-color; } }
  .icon { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font-size: 16px; opacity: 0.6; pointer-events: none; }
}

/* ✅ 新增：进入班级按钮高亮 */
.btn-text.primary {
  color: $primary-color;
  font-weight: bold;
}

/* ✅ 新增：抽屉内部表格样式 */
.drawer-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  th { text-align: left; font-size: 12px; color: #999; padding: 10px; border-bottom: 1px solid #eee; }
  td { padding: 12px 10px; font-size: 14px; border-bottom: 1px solid #f9f9f9; }
}

/* 覆盖 Element Plus 抽屉标题加粗 */
:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 20px;
  font-weight: bold;
  color: #333;
  border-bottom: 1px solid #eee;
}

/* --- 抽屉内按钮样式优化 --- */

/* 1. 顶部“+ 添加学员”按钮 */
.btn-primary {
  /* 确保使用你的主色调 */
  background-color: $primary-color;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px; /* 更加圆润 */
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    filter: brightness(0.9);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 201, 167, 0.2);
  }

  &:active {
    transform: translateY(0);
  }
}

/* 2. 表格内的“移除”按钮 */
.btn-text.delete {
  background-color: #fff1f0; /* 极淡的红色背景 */
  color: #ff4d4f;           /* 标准警示红 */
  border: none;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background-color: #ff4d4f; /* 悬停变全红 */
    color: white;
  }
}

/* 3. 优化抽屉内表格的对齐与间距 */
.drawer-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 8px; /* 行间距，增加呼吸感 */
  
  th {
    padding: 12px;
    background-color: #f8f9fa;
    border-radius: 4px;
  }

  td {
    padding: 12px;
    background-color: transparent;
    border-bottom: 1px solid #f0f0f0;
  }
  
  /* 头像微调 */
  .drawer-user img {
    border: 1px solid #e0e0e0;
    padding: 2px;
    background: white;
  }
}

.class-select-dropdown,
.el-select-dropdown,
.el-popper {
  z-index: 2500 !important;
}

.date-col {
  .date-box-inline {
    display: flex;
    align-items: center;
    justify-content: center; 
    gap: 8px;               
    white-space: nowrap;    
    font-family: monospace; 
    color: #555;
    font-size: 13px;
  }

  .date-sep {
    color: #999;
    font-weight: bold;
    font-size: 12px;
  }
}

.data-table td {
  /* ... 原有样式 ... */
  text-align: center; /* 确保单元格内整体居中 */
}

.status-tabs {
  display: flex;
  background: #eee;
  padding: 3px;
  border-radius: 8px;
  margin-left: 30px; /* 放在面包屑右边 */
  
  span {
    padding: 6px 16px;
    font-size: 13px;
    cursor: pointer;
    border-radius: 6px;
    transition: all 0.2s;
    color: #666;

    &.active {
      background: white;
      color: $primary-color;
      font-weight: 600;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
  }
}

/* ✅ 恢复按钮样式 (使用紫色或蓝色) */
.btn-text.restore {
  background-color: #eef2ff; /* 极淡的蓝色/靛蓝色背景 */
  color: #5f98e2;           /* 现代感强的靛蓝色 */
  border: none;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 0; // 去掉末尾边距

  &:hover {
    background-color: #75a5e4; /* 悬停变全蓝 */
    color: white;
    box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2);
  }
}

/* 如果是已归档状态，可以给表格行加一个淡淡的置灰效果 */
.data-table tr.archived {
  opacity: 0.8;
  background-color: #fafafa;
}
</style>