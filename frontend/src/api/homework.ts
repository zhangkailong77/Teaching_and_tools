import request from '@/utils/request';

// 提交内容结构
export interface SubmissionData {
  content: string; // 富文本或单纯的文字描述
  // 如果有图片，通常是先上传图片拿到URL，然后拼接到 content 里，或者单独传 attachments 字段
  // 这里简化处理，假设 content 包含了图片链接
}

// 提交作业接口
export function submitHomework(assignmentId: number, data: SubmissionData) {
  return request.post(`/homeworks/${assignmentId}/submit`, data);
}

export interface AssignmentCard {
  id: number;
  title: string;
  course_name: string;
  lesson_title: string;
  deadline: string;
  status: number; // 0, 1, 2
  score: number;
  course_cover?: string;
}

// ✅ 新增：获取我的作业任务列表
export function getMyHomeworkTodos() {
  return request.get<any, AssignmentCard[]>('/homeworks/my-todos');
}

// ✅ 新增：获取仪表盘聚合统计数据
export function getStudentDashboardStats() {
  return request.get<any, {
    pending_count: number;
    week_submitted_count: number;
    score_trend: { title: string; score: number; date: string }[];
  }>('/homeworks/dashboard-stats'); // 确保这里的路径和后端一致
}


// =======================
// 教师端接口
// =======================

export interface HomeworkStatsV2 {
  pending_count: number;
  pie_data: { submitted: number; graded: number; unsubmitted: number };
  rank_data: { class_name: string; rate: number }[];
}

export interface TeacherAssignmentItem {
  id: number;
  title: string;
  course_name: string;
  deadline: string;
  stats: {
    total: number;
    graded: number;
    submitted: number;
    unsubmitted: number;
  };
}

export interface ClassHomeworkGroup {
  class_id: number;
  class_name: string;
  pending_count: number;
  assignments: TeacherAssignmentItem[];
  isExpanded?: boolean; // 前端辅助字段：是否展开
}

// 1. 获取首页统计 (新版)
export function getTeacherHomeworkStats() {
  return request.get<any, HomeworkStatsV2>('/homeworks/teacher/stats');
}

// 2. 获取作业列表 (新版 - 分组)
export function getTeacherHomeworkList() {
  return request.get<any, ClassHomeworkGroup[]>('/homeworks/teacher/list');
}


export interface SubmissionItem {
  student_id: number;
  student_name: string;
  student_number: string;
  avatar?: string;
  status: number; // 0:未交, 1:已交, 2:已批
  submission_id?: number;
  content?: string;
  score?: number;
  feedback?: string;
  submitted_at?: string;
}

export interface GradingData {
  assignment_title: string;
  assignment_content: string;
  students: SubmissionItem[];
}

// 获取批改列表
export function getAssignmentSubmissions(assignmentId: number) {
  return request.get<any, GradingData>(`/homeworks/${assignmentId}/submissions`);
}

// 提交评分
export function submitGrade(submissionId: number, data: { score: number; feedback: string }) {
  return request.post(`/homeworks/submissions/${submissionId}/grade`, data);
}

// ✅ 新增：获取批改详情
export interface SubmissionResult {
  submission_id: number;
  status: number;
  score: number;
  feedback: string;
  content: string; // 可能是带高亮的 HTML
  annotations: { id: string; text: string }[];
  assignment_title: string;
  assignment_requirement: string;
  submitted_at: string;
  graded_at: string;
}

export function getSubmissionResult(assignmentId: number) {
  return request.get<any, SubmissionResult>(`/homeworks/${assignmentId}/result`);
}


// 定义发布自定义作业的参数类型
export interface CustomHomeworkData {
  title: string;
  content: string;
  class_ids: number[];
  deadline: string | null; // 后端接收 datetime 字符串
  attachments: string[];   // 附件 URL 列表
  max_score: number;
}

// ✅ 新增：发布自定义作业
export const createCustomHomework = (data: CustomHomeworkData) => {
  return request({
    url: '/homeworks/custom', // 对应后端路由
    method: 'post',
    data
  })
}