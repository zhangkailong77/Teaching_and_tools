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

/**
 * 课时时长格式化（兼容秒数 number / 秒数字符串 / mm:ss 字符串）
 */
export const formatLessonDuration = (duration?: string | number | null) => {
  if (duration === null || duration === undefined) return '--:--';

  if (typeof duration === 'number') {
    if (!Number.isFinite(duration) || duration < 0) return '--:--';
    const totalSeconds = Math.floor(duration);
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  const raw = duration.trim();
  if (!raw) return '--:--';

  const mmssMatch = raw.match(/^(\d+):(\d{1,2})$/);
  if (mmssMatch) {
    const mins = Number(mmssMatch[1]);
    const secs = Number(mmssMatch[2]);
    if (!Number.isFinite(mins) || !Number.isFinite(secs) || secs >= 60) return '--:--';
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  const asSeconds = Number(raw);
  if (Number.isFinite(asSeconds) && asSeconds >= 0) {
    const totalSeconds = Math.floor(asSeconds);
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  return '--:--';
};
