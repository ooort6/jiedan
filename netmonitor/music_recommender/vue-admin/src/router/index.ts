import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";
import NProgress from "nprogress";
import "nprogress/nprogress.css";
import { ChatDotRound } from "@element-plus/icons-vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/login/index.vue"),
    meta: { title: "登录", requiresAuth: false },
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/register/index.vue"),
    meta: { title: "注册", requiresAuth: false },
  },
  {
    path: "/",
    name: "Layout",
    component: () => import("@/layouts/index.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/views/dashboard/index.vue"),
        meta: { title: "控制台", icon: "HomeFilled", requiresAuth: true },
      },
      {
        path: "profile",
        name: "Profile",
        component: () => import("@/views/profile/index.vue"),
        meta: { title: "个人信息", icon: "User", requiresAuth: true },
      },
      {
        path: "notes",
        name: "Notes",
        component: () => import("@/views/notes/index.vue"),
        meta: { title: "笔记管理", icon: "Document", requiresAuth: true },
      },
      {
        path: "calendar",
        name: "Calendar",
        component: () => import("@/views/calendar/index.vue"),
        meta: { title: "日程安排", icon: "Calendar", requiresAuth: true },
      },
      {
        path: "categories",
        name: "Categories",
        component: () => import("@/views/categories/index.vue"),
        meta: { title: "分类管理", icon: "Folder", requiresAuth: true },
      },
      {
        path: "ai-chat",
        name: "AiChat",
        component: () => import("@/views/ai-chat/index.vue"),
        meta: { title: "AI助手", icon: "ChatDotRound", requiresAuth: true },
      },
      {
        path: "todo",
        name: "Todo",
        component: () => import("@/views/todo/index.vue"),
        meta: { title: "待办事项", icon: "List", requiresAuth: true },
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/dashboard",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 全局前置守卫
router.beforeEach((to, from, next) => {
  NProgress.start();
  document.title = to.meta.title ? `${to.meta.title} - Vue Admin` : "Vue Admin";

  const token = localStorage.getItem("token");

  // 如果需要登录但没有token，重定向到登录页
  if (to.meta.requiresAuth && !token) {
    next({ name: "Login" });
    return;
  }

  // 如果已登录且访问登录页，重定向到首页
  if (to.path === "/login" && token) {
    next({ path: "/" });
    return;
  }

  next();
});

// 全局后置守卫
router.afterEach(() => {
  NProgress.done();
});

export default router;
