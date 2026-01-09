import { defineStore } from 'pinia';
import { ref } from 'vue';
import { login, register, getUserInfo } from '@/api/auth';
import type { LoginParams, UserInfo } from '@/types/user';
import { getTeacherHomeworkStats } from '@/api/homework';

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '');
  const userInfo = ref<UserInfo | null>(null);
  const pendingHomeworkCount = ref(0);

  // ✅ 【新增】刷新待办数的方法
  async function refreshPendingCount() {
    // 只有老师才查，且必须已登录
    if (token.value && userInfo.value?.role === 'teacher') {
      try {
        const res = await getTeacherHomeworkStats();
        pendingHomeworkCount.value = res.pending_count;
      } catch (e) {
        console.error('获取待办数失败', e);
      }
    }
  }

  // 登录动作
  async function userLogin(params: LoginParams) {
    const res = await login(params);
    token.value = res.access_token;
    localStorage.setItem('token', res.access_token); // 持久化
  }

  // 注册动作
  async function userRegister(params: LoginParams) {
    await register(params);
  }

  // 获取用户信息
  async function fetchUserInfo() {
    if (!token.value) return;
    const res = await getUserInfo();
    userInfo.value = res;
  }

  // 退出登录
  function logout() {
    token.value = '';
    userInfo.value = null;
    localStorage.removeItem('token');
  }

  return { token, userInfo, pendingHomeworkCount, userLogin, userRegister, fetchUserInfo, logout, refreshPendingCount };
});