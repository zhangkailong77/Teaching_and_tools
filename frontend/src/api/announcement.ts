import request from '@/utils/request';

// 公告类型定义
export interface AnnouncementItem {
  id: number;
  title: string;
  type: 'urgent' | 'normal' | 'course' | 'tip';
  is_pinned: number;
  created_at: string;
  publisher_name: string;
  read_count: number;
  total_count: number;
  content?: string; // 详情时用到
}

// 1. 获取教师发布的公告列表
export function getTeacherAnnouncements() {
  return request<any, AnnouncementItem[]>({
    url: '/announcements/teacher/list',
    method: 'get'
  });
}

// 2. 发布公告
export function createAnnouncement(data: {
  title: string;
  content: string;
  type: string;
  target_type: 'all' | 'class';
  class_ids?: number[];
  is_pinned: number;
  expires_at?: string;
}) {
  return request({
    url: '/announcements/',
    method: 'post',
    data
  });
}


// 3. 获取公告详情
export function getAnnouncementDetail(id: number) {
  return request<any, {
    id: number;
    title: string;
    content: string;
    type: string;
    target_type: string;
    is_pinned: number;
    created_at: string;
    expires_at?: string;
    publisher_name: string;
    class_names: string[];
    read_count: number;
    total_count: number;
    students: Array<{
      id: number;
      name: string;
      student_number: string;
      is_read: boolean;
    }>;
  }>({
    url: `/announcements/${id}/detail`,
    method: 'get'
  });
}



// 3. [学生] 获取公告列表
export function getStudentAnnouncements() {
  return request<any, AnnouncementItem[]>({
    url: '/announcements/student/list',
    method: 'get'
  })
}

// 4. [学生] 标记已读
export function markAnnouncementRead(id: number) {
  return request({
    url: `/announcements/${id}/read`,
    method: 'post'
  })
}