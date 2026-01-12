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
}

// 统计数据结构 (对应后端 DashboardStats)
export interface DashboardStats {
  total_students: number;
  total_classes: number;
  pending_homeworks: number;
}

// 获取统计数据 (顶部卡片)
export function getDashboardStats() {
  return request.get<any, DashboardStats>('/classes/stats');
}

// 定义后端返回的学生结构
export interface StudentItem {
  id: number;
  username: string;
  full_name: string;
  student_number: string;
  avatar?: string;
  class_name: string;
  class_id: number;
  joined_at: string;
  is_active: boolean;
  progress: number;
  // 前端辅助字段 (颜色等)
  classColor?: string;
  classBg?: string;
}

// 1. 获取老师创建的所有班级 (用于下拉框选择)
export function getMyClasses() {
  return request.get<any, ClassItem[]>('/classes/');
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