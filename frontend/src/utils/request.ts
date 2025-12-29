import axios from 'axios';

// 创建 axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // 读取 .env 里的地址
  timeout: 120000
});

// 请求拦截器：每次请求自动带上 Token
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：简化返回数据，处理报错
service.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const status = error.response?.status;
    // 获取后端返回的原始错误信息
    const detail = error.response?.data?.detail;

    // --- ✅ 1. 专门处理 422 参数校验错误 ---
    if (status === 422) {
      // FastAPI 的 422 错误通常是一个数组: [{loc:.., msg:..}, ...]
      if (Array.isArray(detail)) {
        // 取出第一个错误的字段和原因
        const firstError = detail[0];
        const field = firstError.loc[firstError.loc.length - 1]; // 出错的字段名
        const msg = firstError.msg; // 错误原因
        alert(`参数校验失败: 字段【${field}】${msg}`);
      } else {
        // 如果是字符串，直接显示
        alert(`参数错误: ${typeof detail === 'object' ? JSON.stringify(detail) : detail}`);
      }
      return Promise.reject(error);
    }

    // --- ✅ 2. 处理 401 登录过期 (保持之前写的) ---
    if (status === 401) {
      console.warn('登录过期，正在跳转...');
      localStorage.removeItem('token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // --- 3. 其他错误 ---
    // 防止 [object Object] 再次出现
    const errorMsg = typeof detail === 'string' ? detail : '请求失败，请检查网络或联系管理员';
    alert(errorMsg);
    
    return Promise.reject(error);
  }
);

export default service;