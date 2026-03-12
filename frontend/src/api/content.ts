import request from '@/utils/request';

export interface CourseItem {
  id: number;
  name: string;
  cover?: string;
  intro?: string;
  created_at: string;
  is_locked: boolean;
  public_id: string;
  // 统计字段
  task_count?: number;
  total_duration?: number;
  lesson_count?: number;
  course_type?: string;
}

// 定义类型
export interface CourseLessonItem {
  id: number;
  title: string;
  type: string;
  duration: string;
  is_free: boolean;
  is_previewable?: boolean;  // 预览模式下标记是否可预览
  file_url: string | null;
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

export interface InteractiveAppItem {
  app_type: string;
  entry_url: string;
  relative_url: string;
  version?: string;
  available_lesson_ids?: number[];
  source: string;
}

// 1. 获取我的课程资源库（全部 + 锁定状态，用于资源库页面）
export function getMyCourses() {
  return request.get<any, CourseItem[]>('/content/courses/me');
}

// 2. 获取可选课程列表（仅已授权，用于创建班级下拉选择）
export function getAvailableCourses() {
  return request.get<any, CourseItem[]>('/content/courses/available');
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

export function getCourseInteractiveApp(id: string, appType = 'ppt-test', lessonId?: number) {
  return request.get<any, InteractiveAppItem>(`/content/courses/${id}/interactive-app`, {
    params: { app_type: appType, lesson_id: lessonId }
  });
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

export function getStudentCourseInteractiveApp(id: string, appType = 'ppt-test', lessonId?: number) {
  return request.get<any, InteractiveAppItem>(`/content/student/courses/${id}/interactive-app`, {
    params: { app_type: appType, lesson_id: lessonId }
  });
}

// ✅ 新增：[学生端] 更新学习进度
export function updateProgress(data: { lesson_id: number; status: number; last_position: number }) {
  return request.post('/content/student/progress', data);
}
