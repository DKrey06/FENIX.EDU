import { createRouter, createWebHistory } from "vue-router";
import IndexPage from "../components/IndexPage.vue";
import CoursesPage from "../pages/CoursesPage.vue";
import DiscussionPage from "../pages/DiscussionPage.vue";
import ArchivePage from "../pages/ArchivePage.vue";
import MessagesPage from "../pages/MessagesPage.vue";
import LoginPage from "../pages/auth/LoginPage.vue";
import RegisterPage from "../pages/auth/RegisterPage.vue";
import CourseEditPage from "../pages/CourseEditPageFK.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: IndexPage,
    meta: { requiresAuth: true },
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
  meta: { requiresAuth: true },
},
{
  path: "/courses/:id/edit",
  name: "CourseEdit",
  component: () => import("../pages/CourseEditPageFK.vue"),
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
    path: "/:pathMatch(.*)*",
    redirect: "/",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem("isAuthenticated") === "true";

  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login");
  }
  else if (to.meta.guestOnly && isAuthenticated) {
    next("/");
  }
  else {
    next();
  }
});

export default router;
