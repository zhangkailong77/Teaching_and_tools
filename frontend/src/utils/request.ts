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
    // 获取错误状态码
    const status = error.response?.status;
    const msg = error.response?.data?.detail || '请求失败';

    // 1. 如果是 401 (未授权/Token失效)
    if (status === 401) {
      // 这里的 msg 就是后端返回的 "Could not validate credentials"
      // 我们选择不弹窗，或者提示“登录已过期”
      console.warn('登录过期，正在跳转...');
      
      // 清除失效的 token
      localStorage.removeItem('token');
      
      // 强制跳转回登录页
      window.location.href = '/login'; 
      
      return Promise.reject(error);
    }

    // 2. 其他错误 (404, 500 等) 才弹窗
    alert(msg); 
    return Promise.reject(error);
  }
);

export default service;