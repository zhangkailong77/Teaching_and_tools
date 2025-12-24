import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  { 
    path: '/login', 
    name: 'Login',
    component: () => import('@/views/login/index.vue') 
  },
  {
    path: '/dashboard',
    children: [
      {
        path: 'student', // 访问地址: /dashboard/student
        name: 'StudentDashboard',
        component: () => import('@/views/dashboard/student/index.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: 'teacher', // 访问地址: /dashboard/teacher
        name: 'TeacherDashboard',
        component: () => import('@/views/dashboard/teacher/index.vue'),
        meta: { requiresAuth: true, role: 'teacher' }
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 简单的路由守卫：没 Token 不让进 Dashboard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (to.path !== '/login' && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router;