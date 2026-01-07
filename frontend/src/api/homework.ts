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
}

// ✅ 新增：获取我的作业任务列表
export function getMyHomeworkTodos() {
  return request.get<any, AssignmentCard[]>('/homeworks/my-todos');
}