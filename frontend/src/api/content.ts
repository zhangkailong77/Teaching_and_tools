import request from '@/utils/request';

export interface CourseItem {
  id: number;
  name: string;
  cover?: string;
  intro?: string;
  created_at: string;
  is_locked: boolean;
}

// 1. 获取我的课程资源库
export function getMyCourses() {
  return request.get<any, CourseItem[]>('/content/courses/me');
}