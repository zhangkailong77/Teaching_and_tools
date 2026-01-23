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
          <button class="btn-outline" @click="openImportModal">📥 批量导入</button>
        </div>
      </header>

      <!-- 表格区域 -->
      <div class="table-container">
        <div class="table-wrapper">
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
            <tr v-for="student in students" :key="student.id">
              <td>
                <div class="user-info">
                  <img 
                    v-if="student.avatar" 
                    :src="getImgUrl(student.avatar)" 
                    class="avatar" 
                    alt="avatar"
                  />
                  <div v-else class="avatar text-avatar">
                    {{ getFirstChar(student.name) }}
                  </div>
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
                <button class="action-btn edit" @click="handleEdit(student)">编辑</button>
                <button class="action-btn warning" @click="handleResetPwd(student)">重置</button>
                <button class="action-btn delete" @click="handleRemove(student)">移除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- 分页 -->
      <div class="pagination-bar">
        <el-config-provider :locale="zhCn">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.limit"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </el-config-provider>
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

    <div class="modal-overlay" v-if="showEditModal" @click.self="showEditModal = false">
      <div class="modal-content" style="width: 500px;">
        <div class="modal-header">
          <div class="header-left">
            <span class="icon-bg" style="background: #e3f2fd; color: #0984e3;">✏️</span>
            <h3>编辑学员信息</h3>
          </div>
          <span class="close-btn" @click="showEditModal = false">×</span>
        </div>

        <div class="modal-body">
          <!-- 班级 (支持转班) -->
          <div class="form-group">
            <label>所属班级 (可转班)</label>
            <div class="select-wrapper">
              <select v-model="editForm.classId">
                <option v-for="cls in classList" :key="cls.id" :value="cls.id">
                  {{ cls.name }}
                </option>
              </select>
              <span class="arrow">▼</span>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>真实姓名 <span class="required">*</span></label>
              <input type="text" v-model="editForm.fullName" />
            </div>
            <div class="form-group">
              <label>学号</label>
              <input type="text" v-model="editForm.studentNumber" />
            </div>
          </div>

          <div class="form-group">
            <label>手机号 (登录账号) <span class="required">*</span></label>
            <input type="text" v-model="editForm.username" />
            <p class="hint" style="color: #ff9800;">⚠️ 修改手机号会改变学生的登录账号，请谨慎操作。</p>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-text" @click="showEditModal = false">取消</button>
          <button class="btn-submit" @click="submitEdit" :disabled="isEditLoading">
            {{ isEditLoading ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </div>
    </div>

    <div class="modal-overlay" v-if="showImportModal" @click.self="showImportModal = false">
      <div class="modal-content" style="width: 500px;">
        <div class="modal-header">
          <div class="header-left">
            <span class="icon-bg" style="background: #e3f2fd; color: #0984e3;">📂</span>
            <h3>批量导入学员</h3>
          </div>
          <span class="close-btn" @click="showImportModal = false">×</span>
        </div>

        <div class="modal-body">
          
          <!-- 结果展示区 (如果有结果) -->
          <div v-if="importResult" class="result-box">
            <div class="summary">
              <span class="success">成功: {{ importResult.success_count }}</span>
              <span class="error">失败: {{ importResult.error_count }}</span>
            </div>
            <!-- 错误日志 -->
            <div v-if="importResult.error_logs.length > 0" class="error-list">
              <p v-for="(log, idx) in importResult.error_logs" :key="idx">❌ {{ log }}</p>
            </div>
          </div>

          <!-- 导入表单 (如果没有结果，或者有错误需要重试) -->
          <div v-else>
            <!-- 1. 选班级 -->
            <div class="form-group">
              <label>导入到哪个班级 <span class="required">*</span></label>
              <div class="select-wrapper">
                <select v-model="importClassId">
                  <option disabled value="">请选择班级...</option>
                  <option v-for="cls in classList" :key="cls.id" :value="cls.id">
                    {{ cls.name }}
                  </option>
                </select>
                <span class="arrow">▼</span>
              </div>
            </div>

            <!-- 2. 下模板 -->
            <div class="form-group">
              <label>数据模板</label>
              <div class="template-box">
                <span>请按照模板格式填写姓名、手机号、学号</span>
                <a href="#" @click.prevent="downloadTemplate">⬇️ 下载标准模板</a>
              </div>
            </div>

            <!-- 3. 上传文件 -->
            <div class="form-group">
              <label>上传 Excel 文件</label>
              <div class="upload-zone" @click="triggerImportInput" :class="{ 'has-file': importFile }">
                <input type="file" ref="importInputRef" accept=".xlsx, .xls, .csv" style="display:none" @change="handleImportFileChange"/>
                <div class="zone-content">
                  <span class="icon">{{ importFile ? '📄' : '☁️' }}</span>
                  <p class="text">{{ importFile ? importFile.name : '点击或拖拽文件到这里' }}</p>
                  <p class="sub-text" v-if="!importFile">支持 .xlsx / .csv 格式</p>
                </div>
              </div>
            </div>
          </div>

        </div>

        <div class="modal-footer">
          <button class="btn-text" @click="showImportModal = false">取消</button>
          <!-- 只有选了班级和文件才亮 -->
          <button class="btn-submit" @click="submitImport" :disabled="isImporting || !importFile || !importClassId">
            {{ isImporting ? '导入中...' : '开始导入' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import { getMyCourses, type CourseItem } from '@/api/content';
import { getMyClasses, createClass, addStudentToClass, getMyStudents, batchImportStudents, updateStudent, removeStudentFromClass, resetStudentPassword, type ClassItem, type StudentItem, type ImportResult } from '@/api/course';
import TeacherSidebar from '@/components/TeacherSidebar.vue';
import { getImgUrl } from '@/utils/index'; 
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const route = useRoute();
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
const showEditModal = ref(false);
const isEditLoading = ref(false);

const editForm = reactive({
  id: 0,
  username: '',
  fullName: '',
  studentNumber: '',
  classId: '' as string | number // 允许转班
});

// --- 移除逻辑 ---
const handleRemove = async (stu: StudentItem) => {
  if (!confirm(`确定要将【${stu.name}】移出【${stu.class_name}】吗？\n该操作不会删除学生账号，仅解除班级关联。`)) return;
  
  try {
    // 注意：这里需要传入 class_id，现在后端列表接口已经返回了 class_id
    await removeStudentFromClass(stu.class_id, stu.id);
    alert('移除成功');
    fetchStudentList(); // 刷新列表
  } catch (error) {
    console.error(error);
  }
};

// --- 编辑逻辑 ---
const handleEdit = (stu: StudentItem) => {
  // 回显数据
  editForm.id = stu.id;
  editForm.username = stu.username;
  editForm.fullName = stu.full_name || '';
  editForm.studentNumber = stu.student_number || '';
  editForm.classId = stu.class_id;
  
  showEditModal.value = true;
};

const submitEdit = async () => {
  if (!editForm.username || !editForm.fullName) return alert('姓名和手机号必填');
  
  isEditLoading.value = true;
  try {
    await updateStudent(editForm.id, {
      username: editForm.username,
      full_name: editForm.fullName,
      student_number: editForm.studentNumber,
      class_id: Number(editForm.classId)
    });
    alert('修改成功');
    showEditModal.value = false;
    fetchStudentList(); // 刷新列表
  } catch (error) {
    console.error(error);
  } finally {
    isEditLoading.value = false;
  }
};

// ✅ 新增：批量导入相关状态
const showImportModal = ref(false);
const isImporting = ref(false);
const importClassId = ref(''); // 选中的班级
const importFile = ref<File | null>(null);
const importResult = ref<ImportResult | null>(null); // 存储后端返回的结果
const importInputRef = ref<HTMLInputElement | null>(null);

// ✅ 辅助：生成并下载模版 (生成一个简单的 CSV 文件供老师填)
const downloadTemplate = () => {
  const csvContent = "姓名,手机号,学号\n张三,13800138000,2025001\n李四,13900139000,2025002";
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", "学员导入模板.csv"); // Excel 也能打开 CSV
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 触发文件选择
const triggerImportInput = () => importInputRef.value?.click();

// 监听文件变化
const handleImportFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    importFile.value = input.files[0];
    importResult.value = null; // 重置上一次的结果
  }
};

// 提交导入
const submitImport = async () => {
  if (!importClassId.value) return alert('请先选择班级');
  if (!importFile.value) return alert('请先上传文件');

  isImporting.value = true;
  importResult.value = null;

  try {
    const res = await batchImportStudents(Number(importClassId.value), importFile.value);
    importResult.value = res; // 展示结果
    
    // 如果全部成功，刷新列表
    if (res.error_count === 0) {
      alert(`成功导入 ${res.success_count} 人！`);
      showImportModal.value = false;
      fetchStudentList();
    }
    // 如果有部分失败，不关闭弹窗，显示错误日志
    else {
      fetchStudentList(); // 哪怕部分成功，也刷新一下列表看看
    }
  } catch (error) {
    console.error(error);
    alert('导入失败，请检查文件格式');
  } finally {
    isImporting.value = false;
  }
};

const openImportModal = () => {
  importClassId.value = '';
  importFile.value = null;
  importResult.value = null;
  // 如果当前页面已经筛选了班级 (selectedClassId)，自动填入
  if (selectedClassId.value) {
    importClassId.value = String(selectedClassId.value);
  }
  showImportModal.value = true;
};

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

// ✅ 新增：处理分页事件的函数
const handleSizeChange = (val: number) => {
  pagination.limit = val;
  pagination.page = 1; // 切换每页条数后重置到第一页
  fetchStudentList();
};

const handlePageChange = (val: number) => {
  pagination.page = val;
  fetchStudentList();
};

// ✅ 新增：定义分页状态对象
const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
});

const fetchStudentList = async () => {
  isLoading.value = true;
  try {
    const res = await getMyStudents({
      page: pagination.page,
      limit: pagination.limit,
      class_id: selectedClassId.value || undefined, // 班级筛选
      keyword: searchText.value || undefined        // 搜索关键词
    });
    
    // 后端已经分页好了，直接赋值
    students.value = res.items.map(s => ({
      ...s,
      name: s.full_name || s.username, 
      code: s.student_number || '无学号',
      avatar: s.avatar,
      className: s.class_name,
      joinDate: new Date(s.joined_at).toLocaleDateString(),
      status: s.is_active ? 'active' : 'inactive',
      classColor: '#00c9a7',
      classBg: '#e0f2f1'
    }));
    
    // 更新总数
    pagination.total = res.total;
    
  } catch (error) {
    console.error("获取学生列表失败", error);
  } finally {
    isLoading.value = false;
  }
};

watch([selectedClassId, searchText], () => {
  pagination.page = 1;
  fetchStudentList();
});

const getFirstChar = (name?: string) => {
  return name ? name.charAt(0).toUpperCase() : '?';
};

onMounted(async () => {
  // 1. 先获取班级下拉列表（为了让下拉框能显示出班级名字）
  try {
    const res = await getMyClasses();
    classList.value = res;
  } catch (e) {
    console.error(e);
  }

  // 2. 检查 URL 是否带了 class_id 参数
  const queryClassId = route.query.class_id;
  
  if (queryClassId) {
    // 如果有参数，设置选中项
    // 💡 注意：这一步赋值会触发下面的 watch([selectedClassId], ...)，从而自动调用 fetchStudentList()
    selectedClassId.value = Number(queryClassId);
  } else {
    // 如果没有参数，手动加载一次全部列表
    fetchStudentList();
  }
});

// 1. 打开"添加学生"弹窗前，先去拉取最新的班级列表
const openAddStudentModal = async () => {
  try {
    const res = await getMyClasses();
    const classData = (res as any).data || res;
    classList.value = classData;
    if (classData.length > 0) studentForm.classId = classData[0].id;
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

// ✅ 新增：重置密码处理函数
const handleResetPwd = async (stu: StudentItem) => {
  // 二次确认，防止手滑
  if (!confirm(`确定要重置【${stu.name}】的密码吗？\n\n重置后密码将变为：123456`)) {
    return;
  }

  try {
    await resetStudentPassword(stu.id);
    alert('重置成功！请通知学生使用密码 123456 登录。');
  } catch (error) {
    console.error(error);
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
    background: white; 
    border-radius: 15px; 
    padding: 20px; 
    box-shadow: 0 5px 20px rgba(0,0,0,0.02); 
  
    flex: 1; 
    overflow: hidden; 
    display: flex;
    flex-direction: column;

    .table-wrapper {
      flex: 1;
      overflow-y: auto; /* 允许垂直滚动 */
    }
    
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
      .warning { color: #f39c12; }
    }
  }

  /* 分页 */
  .pagination-bar {
    display: flex;
    justify-content: center;
    padding: 20px 0;
    background: white;
    border-top: 1px solid #eee;
    margin-top: auto; /* 核心：利用 Flex 布局将分页栏推到底部 */
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

/* 在原有的 .avatar 样式基础上补充 */
.student-table {
  /* ... */
  .user-info {
    /* 确保 .avatar 有基础宽高 */
    .avatar { 
      width: 32px; 
      height: 32px; 
      border-radius: 50%; 
      object-fit: cover; 
      flex-shrink: 0;
    }
    
    /* ✅ 新增：文字头像样式 */
    .text-avatar {
      background-color: #e0f2f1; /* 浅青色 */
      color: $primary-color;     /* 深青色文字 */
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: bold;
    }
  }
}

/* 模板下载提示框 */
.template-box {
  background: #f8f9fa; border: 1px dashed #ddd; padding: 10px 15px; border-radius: 8px;
  display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #666;
  a { color: $primary-color; text-decoration: none; font-weight: 600; &:hover { text-decoration: underline; } }
}

/* 上传区域 */
.upload-zone {
  border: 2px dashed #e0e0e0; border-radius: 12px; height: 120px;
  display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s;
  &:hover { border-color: $primary-color; background-color: #f0fdfa; }
  &.has-file { border-color: $primary-color; background-color: #e6fffa; }
  
  .zone-content { text-align: center; }
  .icon { font-size: 28px; margin-bottom: 5px; display: block; }
  .text { font-size: 14px; font-weight: 600; color: #333; margin: 0; }
  .sub-text { font-size: 12px; color: #999; margin-top: 5px; }
}

/* 导入结果展示 */
.result-box {
  background: #fafafa; border-radius: 8px; padding: 15px;
  .summary { display: flex; gap: 20px; font-weight: bold; margin-bottom: 10px; font-size: 16px;
    .success { color: #52c41a; } .error { color: #ff4d4f; }
  }
  .error-list {
    max-height: 200px; overflow-y: auto; background: #fff; border: 1px solid #eee; padding: 10px; border-radius: 6px;
    p { color: #ff4d4f; font-size: 12px; margin-bottom: 4px; border-bottom: 1px dashed #f0f0f0; padding-bottom: 2px; }
  }
}
</style>