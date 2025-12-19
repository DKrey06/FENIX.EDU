import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

// Импортируем компоненты
import LandingPage from "../pages/LandingPage.vue";
import IndexPage from "../components/IndexPage.vue";
import LoginPage from "../pages/auth/LoginPage.vue";
import RegisterPage from "../pages/auth/RegisterPage.vue";
import CoursesPage from "../pages/CoursesPage.vue";
import DiscussionPage from "../pages/DiscussionPage.vue";
import ArchivePage from "../pages/ArchivePage.vue";
import MessagesPage from "../pages/MessagesPage.vue";
import WaitingApprovalPage from "../pages/WaitingApprovalPage.vue";

const routes = [
  // Лендинг для неавторизованных пользователей
  {
    path: "/",
    name: "Landing",
    component: LandingPage,
    meta: { guestOnly: true },
  },
  // Страница ожидания подтверждения - доступна всем
  {
    path: "/waiting-approval",
    name: "WaitingApproval",
    component: WaitingApprovalPage,
    // НЕ требует аутентификации, может требовать только для определенных сценариев
  },
  // Главная страница для авторизованных
  {
    path: "/dashboard",
    name: "Dashboard",
    component: IndexPage,
    meta: { requiresAuth: true },
  },
  // Админ-панель с layout
  {
    path: "/admin",
    component: () => import("../pages/AdminLayout.vue"),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: "",
        redirect: "/admin/users",
      },
      {
        path: "users",
        name: "AdminUsers",
        component: () => import("../pages/AdminUsersPage.vue"),
      },
    ],
  },
  // Страницы авторизации
  {
    path: "/login",
    name: "Login",
    component: LoginPage,
    meta: { guestOnly: true },
  },
  {
    path: "/register",
    name: "Register",
    component: RegisterPage,
    meta: { guestOnly: true },
  },
  // Другие защищенные маршруты
  {
    path: "/courses",
    name: "Courses",
    component: CoursesPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/course/:id",
    name: "CourseView",
    component: () => import("../pages/CourseViewPage.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/discussions",
    name: "Discussions",
    component: DiscussionPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/archive",
    name: "Archive",
    component: ArchivePage,
    meta: { requiresAuth: true },
  },
  {
    path: "/messages",
    name: "Messages",
    component: MessagesPage,
    meta: { requiresAuth: true },
  },
  // Редирект для несуществующих маршрутов
  {
    path: "/:pathMatch(.*)*",
    redirect: "/",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;
  const user = authStore.user;

  // Особый случай: waiting-approval доступен всем
  if (to.name === "WaitingApproval") {
    next();
    return;
  }

  // Авторизованный пользователь на лендинге -> на дашборд
  if (to.path === "/" && isAuthenticated) {
    // Проверяем статус пользователя
    if (user && user.status === "pending") {
      next("/waiting-approval");
    } else {
      next("/dashboard");
    }
    return;
  }

  // Неавторизованный пользователь на защищенной странице -> на логин
  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login");
    return;
  }

  // Авторизованный пользователь на гостевой странице -> на дашборд
  if (to.meta.guestOnly && isAuthenticated) {
    // Проверяем статус пользователя
    if (user && user.status === "pending") {
      next("/waiting-approval");
    } else {
      next("/dashboard");
    }
    return;
  }

  // Проверка админских прав
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next("/dashboard");
    return;
  }

  // Проверка статуса пользователя для страниц, требующих авторизации
  if (to.meta.requiresAuth && isAuthenticated && user) {
    // Если пользователь не подтвержден, перенаправляем на waiting-approval
    if (user.status === "pending") {
      next("/waiting-approval");
      return;
    }

    // Если пользователь активен и пытается зайти на гостевую страницу, перенаправляем на dashboard
    if (user.status === "active" && to.meta.guestOnly) {
      next("/dashboard");
      return;
    }

    // Если пользователь отклонен или заблокирован
    if (user.status === "rejected" || user.status === "blocked") {
      authStore.logout();
      next("/login");
      return;
    }
  }

  // Если все проверки пройдены
  next();
});

export default router;
