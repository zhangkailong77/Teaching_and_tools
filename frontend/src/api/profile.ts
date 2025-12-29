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