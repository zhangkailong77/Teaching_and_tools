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

  // 作业信息
  assignment?: {
    assignment_id: number;
    status: 'none' | 'pending' | 'submitted' | 'graded' | 'expired';
    deadline: string | null;
    score: number | null;
  };
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

// ✅ 新增：作业模板类型定义
export interface CourseTaskItem {
  id: number;
  title: string;
  content: string; // 可能包含 HTML 标签
  sort_order: number;
  created_at: string;
}

// ✅ 新增：获取课程作业列表
export function getCourseTasks(id: string) {
  return request.get<any, CourseTaskItem[]>(`/content/courses/${id}/tasks`);
}

export interface ClassTaskStatus {
  class_id: number;
  class_name: string;
  deadline?: string; // 可能为空
  is_published: boolean;
}

// 1. 获取发布状态列表
export function getTaskPublishStatus(taskId: number) {
  return request.get<any, ClassTaskStatus[]>(`/content/tasks/${taskId}/publish_status`);
}

// 2. 提交发布配置
export function publishTaskToClasses(taskId: number, configs: { class_id: number; deadline?: string }[]) {
  return request.post(`/content/tasks/${taskId}/publish`, { configs });
}




// --------------------【学生端】--------------------
// ✅ 新增：[学生端] 获取课程详情
export function getStudentCourseDetail(id: string) {
  return request.get<any, CourseItem>(`/content/student/courses/${id}`);
}

// ✅ 新增：[学生端] 获取章节目录
export function getStudentCourseChapters(id: string) {
  return request.get<any, CourseChapterItem[]>(`/content/student/courses/${id}/chapters`);
}

// ✅ 新增：[学生端] 更新学习进度
export function updateProgress(data: { lesson_id: number; status: number; last_position: number }) {
  return request.post('/content/student/progress', data);
}