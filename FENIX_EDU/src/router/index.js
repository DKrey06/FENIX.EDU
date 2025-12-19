import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

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
  {
    path: "/",
    name: "Landing",
    component: LandingPage,
    meta: { guestOnly: true },
  },
  {
    path: "/waiting-approval",
    name: "WaitingApproval",
    component: WaitingApprovalPage,
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: IndexPage,
    meta: { requiresAuth: true },
  },
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
    path: "/course/:id/edit",
    name: "CourseViewEdit",
    component: () => import("../pages/CourseViewEditPage.vue"),
    meta: { requiresAuth: true, requiresTeacher: true },
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

  if (to.name === "WaitingApproval") {
    next();
    return;
  }

  if (to.path === "/" && isAuthenticated) {
    if (user && user.status === "pending") {
      next("/waiting-approval");
    } else {
      next("/dashboard");
    }
    return;
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login");
    return;
  }

  if (to.meta.guestOnly && isAuthenticated) {
    if (user && user.status === "pending") {
      next("/waiting-approval");
    } else {
      next("/dashboard");
    }
    return;
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next("/dashboard");
    return;
  }

  if (to.meta.requiresAuth && isAuthenticated && user) {
    if (user.status === "pending") {
      next("/waiting-approval");
      return;
    }

    if (user.status === "active" && to.meta.guestOnly) {
      next("/dashboard");
      return;
    }

    if (user.status === "rejected" || user.status === "blocked") {
      authStore.logout();
      next("/login");
      return;
    }
  }

  if (to.meta.requiresTeacher) {
    if (!isAuthenticated || !user || user.role !== "teacher") {
      if (to.params.id) {
        next({ name: "CourseView", params: { id: to.params.id } });
      } else {
        next("/dashboard");
      }
      return;
    }
  }

  next();
});

export default router;
