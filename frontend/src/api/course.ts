import request from '@/utils/request';

// 定义类型
export interface ClassItem {
  id: number;
  name: string;
  description?: string;
  student_count?: number;
  cover_image?: string;
  start_date?: string;
  end_date?: string;
  bound_course_names: string[];
  bound_course_ids: number[];
  bound_course_public_ids: string[];
  bound_course_covers: string[];
  bound_course_progress: number[];
  teacher_name?: string;
  teacher_title?: string;
  teacher_avatar?: string;
  styleColor?: string;
  pending_count: number;
  status: number;
  // 前端辅助字段
  displayTitle?: string;
  isSplit?: boolean;
  displaySubtitle?: string;
}


// ✅ 新增：图表数据项接口
export interface ChartItem {
  name: string;
  value: number;
  extra?: string[]; // 用于存储课程名列表
}

// 统计数据结构 (对应后端 DashboardStats)
export interface DashboardStats {
  // 模块1: 学生
  total_students: number;
  student_distribution: ChartItem[];

  // 模块3: 执教
  teaching_class_count: number;
  teaching_distribution: ChartItem[];

  // 模块4: 待办
  total_pending: number;
  task_distribution: {
    homework: number;
    exam: number;
  };
}
// 获取统计数据 (顶部卡片)
export function getDashboardStats() {
  return request.get<any, DashboardStats>('/classes/stats');
}

// 定义后端返回的学生结构
export interface StudentItem {
  id: number;
  username: string;
  name: string;  // full_name 的别名
  code: string;  // student_number 的别名
  student_number: string;
  avatar?: string;
  className: string;  // class_name 的别名
  class_name: string;
  class_id: number;
  joined_at: string;
  joinDate: string;  // joined_at 的别名
  is_active: boolean;
  status: string;  // 'active' 或其他的别名
  progress: number;
  // 前端辅助字段 (颜色等)
  classColor?: string;
  classBg?: string;
}

// 1. 获取老师创建的所有班级 (用于下拉框选择)
export function getMyClasses(params?: { status?: number }) {
  return request.get<any, ClassItem[]>('/classes/', { params });
}

// 2. 创建新班级 (为了让你能先建个班，否则没法加学生)
export function createClass(data: {
  name: string; 
  description?: string ;
  cover_image?: string;
  start_date?: string;
  end_date?: string;
  course_ids?: number[];
}) {
  return request.post<any, ClassItem>('/classes/', data);
}

// ✅ 新增：更新班级
export function updateClass(id: number, data: any) {
  return request.put<any, ClassItem>(`/classes/${id}`, data);
}

// 3. 向指定班级添加学生 (核心功能)
export function addStudentToClass(classId: number, data: { username: string, full_name: string, student_number: string }) {
  return request.post(`/classes/${classId}/students`, data);
}

// 4. ✅ 新增：获取我的所有学生
export interface StudentPageResult {
  total: number;
  items: StudentItem[];
}

export function getMyStudents(params?: { 
  class_id?: number | string; 
  keyword?: string; 
  page?: number; 
  limit?: number; 
}) {
  return request<any, StudentPageResult>({
    url: '/classes/my-students',
    method: 'get',
    params
  });
}

// ✅ 新增：将学生移出班级
export function removeStudentFromClass(classId: number, studentId: number) {
  return request.delete(`/classes/${classId}/students/${studentId}`);
}

// 新增更新接口
export function updateStudent(studentId: number, data: {
  username: string;
  full_name: string;
  student_number: string;
  class_id: number;
}) {
  return request.put(`/classes/students/${studentId}`, data);
}

// ✅ 新增：批量导入返回结果类型
export interface ImportResult {
  total_processed: number;
  success_count: number;
  error_count: number;
  error_logs: string[];
}

// ✅ 新增：批量导入接口
export function batchImportStudents(classId: number, file: File) {
  const formData = new FormData();
  formData.append('file', file); // 注意：后端参数名为 file
  
  // 上传文件通常需要较长时间，设置超时为 2分钟
  return request.post<any, ImportResult>(`/classes/${classId}/students/batch`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000 
  });
}


// ✅ 新增：日程项类型
export interface ScheduleItem {
  id: number;
  type: 'exam' | 'homework';
  title: string;
  time: string;
  class_name: string;
  status: string;
}

// ✅ 新增：获取日程接口
export function getTeacherSchedule() {
  return request<any, ScheduleItem[]>({
    url: '/classes/schedule',
    method: 'get'
  })
}

// ✅ 重置学生密码
export function resetStudentPassword(studentId: number) {
  return request.put(`/users/${studentId}/reset-password`);
}

// 更新班级状态 (归档/恢复)
export function updateClassStatus(classId: number, status: number) {
  return request.put(`/classes/${classId}/status`, null, { params: { status } });
}

// ------------------------------学生端-----------------------------
// ✅ 新增：[学生端] 获取我加入的班级及课程信息
export function getMyEnrolledClasses() {
  return request.get<any, ClassItem[]>('/classes/my-enrolled-classes');
}

export interface ClassmateItem {
  name: string;
  avatar?: string;
}

// ✅ 新增：获取同班同学列表
export function getClassmates(classId: number) {
  return request.get<any, ClassmateItem[]>(`/classes/${classId}/classmates`);
}