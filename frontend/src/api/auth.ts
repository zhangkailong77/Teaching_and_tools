import request from '@/utils/request';
import type { LoginParams, LoginResponse, UserInfo } from '@/types/user';

// 登录接口 (注意后端是用 form-data 接收)
export function login(data: LoginParams) {
  // FastAPI 的 OAuth2PasswordRequestForm 需要表单格式
  const formData = new FormData();
  formData.append('username', data.username);
  formData.append('password', data.password);
  formData.append('role', data.role); 
  
  return request.post<any, LoginResponse>('/auth/login', formData);
}

// 注册接口 (后端是用 JSON 接收)
export function register(data: LoginParams) {
  return request.post<any, UserInfo>('/auth/register', data);
}

// 获取用户信息
export function getUserInfo() {
  return request.get<any, UserInfo>('/users/me');
}