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
        path: 'student/my-class', 
        name: 'StudentMyClass',
        component: () => import('@/views/dashboard/student/my-class.vue'), 
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: 'student/course/:id',
        name: 'StudentCourseDetail',
        component: () => import('@/views/dashboard/student/course-detail.vue'), 
        meta: { requiresAuth: true, role: 'student', activeMenu: '/dashboard/student' }
      },
      {
        path: 'student/homeworks', 
        name: 'StudentHomeworks',
        component: () => import('@/views/dashboard/student/homeworks.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: 'student/exams',
        name: 'StudentExamLobby',
        component: () => import('@/views/dashboard/student/exams/index.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: 'student/exams/take/:id',
        name: 'TakeExam',
        component: () => import('@/views/dashboard/student/exams/take.vue'),
        meta: { requiresAuth: true, role: 'student', hideSidebar: true } // 标记隐藏侧边栏
      },
      {
        path: 'student/exams/result/:id',
        name: 'StudentExamResult',
        component: () => import('@/views/dashboard/student/exams/analysis.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: 'student/messages',
        name: 'StudentMessages',
        component: () => import('@/views/dashboard/student/messages/index.vue'),
        meta: { requiresAuth: true, role: 'student' }
      },
      {
        path: 'teacher', // 访问地址: /dashboard/teacher
        name: 'TeacherDashboard',
        component: () => import('@/views/dashboard/teacher/index.vue'),
        meta: { requiresAuth: true, role: 'teacher' }
      },
      {
        path: 'teacher/students', 
        name: 'TeacherStudentList',
        component: () => import('@/views/dashboard/teacher/students.vue'),
        meta: { requiresAuth: true, role: 'teacher' }
      },
      {
        path: 'teacher/courses', 
        name: 'TeacherCourseLibrary',
        component: () => import('@/views/dashboard/teacher/courses.vue'), // 稍后创建这个文件
        meta: { requiresAuth: true, role: 'teacher' }
      },
      {
        path: 'teacher/courses/:id', 
        name: 'TeacherCourseDetail',
        component: () => import('@/views/dashboard/teacher/detail.vue'), 
        meta: { requiresAuth: true, role: 'teacher', activeMenu: '/dashboard/teacher/courses' }
      },
      {
        path: 'teacher/classes', 
        name: 'TeacherClassManagement',
        component: () => import('@/views/dashboard/teacher/classes.vue'),
        meta: { requiresAuth: true, role: 'teacher' }
      },
      {
        path: 'teacher/homeworks', 
        name: 'TeacherHomeworks',
        component: () => import('@/views/dashboard/teacher/homeworksManager.vue'), 
        meta: { requiresAuth: true, role: 'teacher' }
      },
      {
        path: 'teacher/homeworks/:id', 
        name: 'TeacherGrading',
        component: () => import('@/views/dashboard/teacher/homeworksGrading.vue'), 
        meta: { requiresAuth: true, role: 'teacher', activeMenu: '/dashboard/teacher/homeworks' }
      },
      {
        path: 'teacher/exams', 
        name: 'TeacherExamCenter',
        component: () => import('@/views/dashboard/teacher/exams/index.vue'), 
        meta: { requiresAuth: true, role: 'teacher' }
      },
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