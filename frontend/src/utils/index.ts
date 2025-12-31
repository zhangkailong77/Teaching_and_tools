// src/utils/index.ts

/**
 * 获取完整的图片地址
 * @param path 后端返回的图片路径 (可能是相对路径 /static/...)
 */
export const getImgUrl = (path?: string) => {
  if (!path) return '';
  
  // 1. 如果已经是完整的网络图片 (http开头)，直接返回
  if (path.startsWith('http') || path.startsWith('https')) {
    return path;
  }
  
  // 2. 如果是相对路径，拼接 .env 里配置的 Base URL
  // 注意：import.meta.env.VITE_IMG_BASE_URL 需要你在 .env.development 里配置好
  const baseUrl = import.meta.env.VITE_IMG_BASE_URL || ''; 
  
  return `${baseUrl}${path}`;
};