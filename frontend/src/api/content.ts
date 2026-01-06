import request from '@/utils/request';

export interface CourseItem {
  id: number;
  name: string;
  cover?: string;
  intro?: string;
  created_at: string;
  is_locked: boolean;
  public_id: string
}

// 定义类型
export interface CourseLessonItem {
  id: number;
  title: string;
  type: string;
  duration: string;
  is_free: boolean;
  file_url: string;
  status: number;       // 0:未开始, 1:进行中, 2:已完成
  last_position: number;
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
export function getCourseDetail(id: string) {
  return request.get<any, CourseItem>(`/content/courses/${id}`);
}


// ✅ 新增：获取章节大纲
export function getCourseChapters(courseId: string) {
  return request.get<any, CourseChapterItem[]>(`/content/courses/${courseId}/chapters`);
}




// --------------------【学生端】--------------------
// ✅ 新增：[学生端] 获取课程详情
export function getStudentCourseDetail(id: number) {
  return request.get<any, CourseItem>(`/content/student/courses/${id}`);
}

// ✅ 新增：[学生端] 获取章节目录
export function getStudentCourseChapters(id: number) {
  return request.get<any, CourseChapterItem[]>(`/content/student/courses/${id}/chapters`);
}

// ✅ 新增：[学生端] 更新学习进度
export function updateProgress(data: { lesson_id: number; status: number; last_position: number }) {
  return request.post('/content/student/progress', data);
}