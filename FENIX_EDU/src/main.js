import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./assets/main.css";

import { useAuthStore } from "./stores/auth";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

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

app.use(router);

// ✅ Монтируем ТОЛЬКО после инициализации auth и готовности роутера
(async () => {
  try {
    const authStore = useAuthStore();
    if (typeof authStore.init === "function") {
      await authStore.init();
    }

    await router.isReady();
    app.mount("#app");
  } catch (e) {
    console.error("Ошибка инициализации приложения:", e);
    await router.isReady();
    app.mount("#app");
  }
})();

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
