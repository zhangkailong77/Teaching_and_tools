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