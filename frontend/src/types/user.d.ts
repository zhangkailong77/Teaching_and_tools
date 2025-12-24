// 用户角色
export type UserRole = 'student' | 'teacher';

// 登录/注册提交的表单数据
export interface LoginParams {
  username: string;
  password: string;
  role: UserRole; // 登录时不需要role，注册时需要
}

// 登录接口返回的数据
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// 用户信息接口
export interface UserInfo {
  id: number;
  username: string;
  role: UserRole;
  is_active: boolean;
}