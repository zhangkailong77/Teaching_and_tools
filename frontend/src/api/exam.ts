import request from '@/utils/request'

// 题目类型枚举
export enum QuestionType {
  SINGLE = 'single',
  MULTIPLE = 'multiple',
  JUDGE = 'judge',
  BLANK = 'blank',
  ESSAY = 'essay'
}

export interface QuestionOption {
  label: string; // A, B, C...
  text: string;
}

export interface QuestionItem {
  id?: number;
  type: QuestionType;
  content: string;
  options?: QuestionOption[];
  answer: string | string[]; // 单选是 "A", 多选是 ["A","B"]
  analysis?: string;
  difficulty: number; // 1, 2, 3
  tags?: string[];
  updated_at?: string;
}


// 定义分页返回结构
export interface QuestionPageResult {
  total: number;
  items: QuestionItem[];
}

// 1. 获取题目列表
export function getQuestions(params: { 
  type?: string; 
  difficulty?: number; 
  keyword?: string; 
  tag?: string;
  skip?: number;
  limit?: number; 
}) {
  return request<any, QuestionPageResult>({ // ✅ 泛型指定返回结构
    url: '/exam/questions',
    method: 'get',
    params
  })
}

// 2. 创建题目
export function createQuestion(data: QuestionItem) {
  return request({
    url: '/exam/questions',
    method: 'post',
    data
  })
}

// 3. 删除题目
export function deleteQuestion(id: number) {
  return request({
    url: `/exam/questions/${id}`,
    method: 'delete'
  })
}

// 4. 更新题目
export function updateQuestion(id: number, data: QuestionItem) {
  return request({
    url: `/exam/questions/${id}`,
    method: 'put',
    data
  })
}

// 批量导入题目
export function batchImportQuestions(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return request({
    url: '/exam/questions/batch',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000 // 导入可能较慢，设置1分钟超时
  });
}


export interface QuestionStats {
  total: number;
  type_counts: Record<string, number>; // { single: 10, multiple: 5 }
  difficulty_counts: Record<string, number>; // { '1': 5, '2': 3 }
}

// 5. 获取题库统计
export function getQuestionStats() {
  return request({
    url: '/exam/questions/stats',
    method: 'get'
  })
}


// ✅ 新增：获取所有标签
export function getAllTags() {
  return request<any, string[]>({
    url: '/exam/questions/tags',
    method: 'get'
  })
}

// ✅ 新增：批量删除
export function batchDeleteQuestions(ids: number[]) {
  return request({
    url: '/exam/questions/batch-delete',
    method: 'post',
    data: ids
  })
}


// ===========================
// 试卷相关
// ===========================

export interface ExamItem {
  id: number;
  title: string;
  status: number; // 0草稿 1已发布 2已结束
  total_score: number;
  duration: number;
  question_count: number;
  created_at: string;
  class_names: string[];
}

// 1. 获取试卷列表
export function getExams() {
  return request<any, ExamItem[]>({
    url: '/exam/exams',
    method: 'get'
  })
}

// 2. 创建试卷 (手动/随机)
// mode: 1手动, 2随机
export function createExam(data: {
  title: string;
  mode: number;
  questions?: Array<{ question_id: number; score: number }>;
  random_config?: Array<{ type: string; difficulty: number; tag?: string; count: number; score: number }>;
}) {
  return request({
    url: '/exam/exams',
    method: 'post',
    data
  })
}

// ✅ 3. 删除试卷
export function deleteExam(id: number) {
  return request({
    url: `/exam/exams/${id}`,
    method: 'delete'
  })
}

// ✅ 获取试卷详情
export function getExamDetail(id: number) {
  return request({
    url: `/exam/exams/${id}`,
    method: 'get'
  })
}

// ✅ 更新试卷
export function updateExam(id: number, data: any) {
  return request({
    url: `/exam/exams/${id}`,
    method: 'put',
    data
  })
}


// ----- 学生端考试相关------
// 1. 获取学生可见的考试列表
export function getStudentExams() {
  return request<any, any[]>({
    url: '/exam/student/list',
    method: 'get'
  })
}

// 2. 开始/进入考试
export function enterExam(examId: number) {
  return request({
    url: `/exam/student/enter/${examId}`,
    method: 'post'
  })
}

// 3. 获取试卷内容 (题目)
export function getExamPaper(examId: number) {
  return request<any, any[]>({
    url: `/exam/student/paper/${examId}`,
    method: 'get'
  })
}

// 4. 提交试卷
export function submitExam(examId: number, data: { answers: any[], cheat_count: number }) {
  return request({
    url: `/exam/student/submit/${examId}`,
    method: 'post',
    data
  })
}