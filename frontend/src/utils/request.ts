import axios from 'axios';

// 创建 axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // 读取 .env 里的地址
  timeout: 5000
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
    return response.data; // 直接返回 data，不用每次都 .data
  },
  (error) => {
    const msg = error.response?.data?.detail || '请求失败';
    alert(msg); // 简单弹窗提示错误
    return Promise.reject(error);
  }
);

export default service;