import request from '@/utils/request';

export interface CourseItem {
  id: number;
  name: string;
  cover?: string;
  intro?: string;
  created_at: string;
}

// 1. 获取我的课程资源库
export function getMyCourses() {
  return request.get<any, CourseItem[]>('/content/courses/me');
}

// 2. 创建新的课程包
export function createCourse(data: { name: string; cover?: string; intro?: string }) {
  return request.post<any, CourseItem>('/content/courses/', data);
}

// 3. 删除课程包
export function deleteCourse(id: number) {
  return request.delete(`/content/courses/${id}`);
}