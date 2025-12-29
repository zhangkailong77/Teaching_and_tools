import request from '@/utils/request';

// 上传图片
// type 参数可选: 'avatars' | 'courses' | 'common'
export function uploadImage(file: File, type: string = 'common') {
  const formData = new FormData();
  formData.append('file', file);
  
  // 注意：这里把 type 拼在 query 参数里传给后端
  return request.post<any, { url: string }>(`/upload/image?type=${type}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}