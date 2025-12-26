import request from '@/utils/request';

// 定义类型
export interface ClassItem {
  id: number;
  name: string;
  description?: string;
  student_count?: number;
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
export function createClass(data: { name: string; description?: string }) {
  return request.post<any, ClassItem>('/classes/', data);
}

// 3. 向指定班级添加学生 (核心功能)
export function addStudentToClass(classId: number, data: { username: string, full_name: string, student_number: string }) {
  return request.post(`/classes/${classId}/students`, data);
}

// 4. ✅ 新增：获取我的所有学生
export function getMyStudents() {
  return request.get<any, StudentItem[]>('/classes/my-students');
}