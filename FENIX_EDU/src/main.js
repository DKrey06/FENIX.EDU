import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./assets/main.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

app.config.errorHandler = (err, vm, info) => {
  console.error("Глобальная ошибка Vue:", err);
  console.error("Компонент:", vm);
  console.error("Информация:", info);
};

app.config.globalProperties.$API_URL = "http://127.0.0.1:8000/api";

const setupAuthInterceptor = () => {
  const originalFetch = window.fetch;

  window.fetch = async function (...args) {
    const [url, options = {}] = args;

    if (typeof url === "string" && url.includes("/api/auth/")) {
      return originalFetch.apply(this, args);
    }

    if (typeof url === "string" && url.includes("/api/")) {
      const token = localStorage.getItem("access_token");
      if (token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        };
        if (
          options.method &&
          options.method.toUpperCase() !== "GET" &&
          !(options.body instanceof FormData)
        ) {
          options.headers["Content-Type"] = "application/json";
        }
      }

      if (import.meta.env.DEV) {
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    }

    try {
      return await originalFetch.apply(this, [url, options]);
    } catch (error) {
      console.error("Ошибка fetch запроса:", error);
      throw error;
    }
  };
};

setupAuthInterceptor();

app.mount("#app");

import { useAuthStore } from "./stores/auth";

setTimeout(() => {
  try {
    const authStore = useAuthStore();
    console.log("Auth store инициализирован");

    router.beforeEach((to, from, next) => {
      const requiresAuth = to.matched.some(
        (record) => record.meta.requiresAuth
      );
      const requiresAdmin = to.matched.some(
        (record) => record.meta.requiresAdmin
      );

      if (requiresAuth && !authStore.isAuthenticated) {
        console.log("Требуется аутентификация, перенаправляем на логин");
        next("/login");
        return;
      }

      if (requiresAdmin && !authStore.isAdmin) {
        console.log("Требуются права администратора");
        next("/dashboard");
        return;
      }

      next();
    });

    if (localStorage.getItem("access_token")) {
      authStore
        .getCurrentUser()
        .then((user) => {
          if (user) {
            console.log("Пользователь аутентифицирован:", user.email);

            if (
              router.currentRoute.value.path === "/login" ||
              router.currentRoute.value.path === "/register" ||
              router.currentRoute.value.path === "/"
            ) {
              router.push("/dashboard");
            }
          } else {
            console.log("Пользователь не аутентифицирован");

            if (router.currentRoute.value.meta?.requiresAuth) {
              router.push("/login");
            }
          }
        })
        .catch((error) => {
          console.error("Ошибка проверки аутентификации:", error);
        });
    }
  } catch (error) {
    console.error("Ошибка инициализации auth store:", error);
  }
}, 100);

window.addEventListener("unhandledrejection", (event) => {
  if (
    event.reason &&
    event.reason.message &&
    event.reason.message.includes("NetworkError")
  ) {
    console.error("Ошибка сети:", event.reason);
    alert(
      "Проблемы с подключением к серверу. Проверьте ваше интернет-соединение."
    );
  }
});

window.addEventListener("offline", () => {
  console.log("Приложение перешло в режим offline");
});

window.addEventListener("online", () => {
  console.log("Приложение вернулось в онлайн режим");
});
