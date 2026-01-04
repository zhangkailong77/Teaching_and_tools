import request from '@/utils/request';

// 定义教师档案的数据结构 (对应后端的 Schema)
export interface TeacherProfile {
  id?: number;
  user_id?: number;
  real_name: string;
  gender: string;
  phone: string;
  school: string;
  college: string;
  title: string;
  intro: string;
  avatar: string;
}

// 1. 获取我的档案
export function getMyTeacherProfile() {
  return request.get<any, TeacherProfile>('/profiles/teacher/me');
}

// 2. 更新我的档案
export function updateMyTeacherProfile(data: Partial<TeacherProfile>) {
  return request.put<any, TeacherProfile>('/profiles/teacher/me', data);
}

// ✅ 新增：学生档案定义 (对应后端 StudentProfileOut)
export interface StudentProfile {
  id: number;
  user_id: number;
  real_name: string;
  student_number: string;
  gender: string;
  phone: string;
  avatar: string;
  intro: string;
  
  // 后端计算的只读字段
  class_name: string;
  course_count: number;
  course_names: string[];
}

// ✅ 新增：获取我的学生档案
export function getMyStudentProfile() {
  return request.get<any, StudentProfile>('/profiles/student/me');
}

// ✅ 新增：更新我的学生档案
export function updateMyStudentProfile(data: Partial<StudentProfile>) {
  return request.put<any, StudentProfile>('/profiles/student/me', data);
}