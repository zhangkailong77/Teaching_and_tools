import request from '@/utils/request';

export interface CourseItem {
  id: number;
  name: string;
  cover?: string;
  intro?: string;
  created_at: string;
  is_locked: boolean;
}

// 定义类型
export interface CourseLessonItem {
  id: number;
  title: string;
  type: string;
  duration: string;
  is_free: boolean;
  file_url: string;
}

export interface CourseChapterItem {
  id: number;
  title: string;
  isOpen: boolean;
  lessons: CourseLessonItem[];
}

// 1. 获取我的课程资源库
export function getMyCourses() {
  return request.get<any, CourseItem[]>('/content/courses/me');
}


// ✅ 新增：获取单门课程详情
export function getCourseDetail(id: number) {
  return request.get<any, CourseItem>(`/content/courses/${id}`);
}


// ✅ 新增：获取章节大纲
export function getCourseChapters(courseId: number) {
  return request.get<any, CourseChapterItem[]>(`/content/courses/${courseId}/chapters`);
}