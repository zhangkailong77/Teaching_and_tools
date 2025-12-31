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
  bound_course_covers: string[];
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
  class_name: string;
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
export function getMyStudents() {
  return request.get<any, StudentItem[]>('/classes/my-students');
}

// ✅ 新增：将学生移出班级
export function removeStudentFromClass(classId: number, studentId: number) {
  return request.delete(`/classes/${classId}/students/${studentId}`);
}



// ------------------------------学生端-----------------------------
// ✅ 新增：[学生端] 获取我加入的班级及课程信息
export function getMyEnrolledClasses() {
  return request.get<any, ClassItem[]>('/classes/my-enrolled-classes');
}