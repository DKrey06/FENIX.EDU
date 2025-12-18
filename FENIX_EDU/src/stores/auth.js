import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "axios";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const token = ref(localStorage.getItem("access_token"));
  const refreshToken = ref(localStorage.getItem("refresh_token"));
  const isLoading = ref(false);

  // Создаем экземпляр axios с базовым URL
  const api = axios.create({
    baseURL: "http://localhost:8000",
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Перехватчик для добавления токена к запросам
  api.interceptors.request.use((config) => {
    if (token.value) {
      config.headers.Authorization = `Bearer ${token.value}`;
    }
    return config;
  });

  // Перехватчик для обработки ошибок и обновления токена
  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // Если ошибка 401 и это не попытка обновления токена
      if (
        error.response?.status === 401 &&
        !originalRequest._retry &&
        !originalRequest.url.includes("/api/auth/refresh")
      ) {
        originalRequest._retry = true;

        try {
          // Пытаемся обновить токен
          const { data } = await refreshAccessToken();

          // Сохраняем новые токены
          token.value = data.access_token;
          refreshToken.value = data.refresh_token;

          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);

          // Обновляем заголовок и повторяем запрос
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Если не удалось обновить - выходим
          logout();
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );

  // Регистрация
  const register = async (userData) => {
    isLoading.value = true;
    try {
      const response = await api.post("/api/auth/register", userData);

      if (response.data.access_token) {
        token.value = response.data.access_token;
        refreshToken.value = response.data.refresh_token;
        user.value = response.data.user;

        localStorage.setItem("access_token", response.data.access_token);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        localStorage.setItem("user", JSON.stringify(response.data.user));
        localStorage.setItem("isAuthenticated", "true");
      }

      return response.data;
    } catch (error) {
      console.error("Ошибка регистрации:", error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  // Вход
  const login = async (credentials) => {
    isLoading.value = true;
    try {
      const response = await api.post("/api/auth/login", credentials);

      token.value = response.data.access_token;
      refreshToken.value = response.data.refresh_token;
      user.value = response.data.user;

      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);
      localStorage.setItem("user", JSON.stringify(response.data.user));
      localStorage.setItem("isAuthenticated", "true");

      return response.data;
    } catch (error) {
      console.error("Ошибка входа:", error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  // Обновление токена
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error("No refresh token");
    }

    try {
      const response = await api.post("/api/auth/refresh", {
        refresh_token: refreshToken.value,
      });

      return response.data;
    } catch (error) {
      console.error("Ошибка обновления токена:", error);
      throw error;
    }
  };

  // Выход
  const logout = () => {
    if (token.value) {
      try {
        api.post("/api/auth/logout");
      } catch (error) {
        console.error("Ошибка при выходе:", error);
      }
    }

    token.value = null;
    refreshToken.value = null;
    user.value = null;

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    localStorage.removeItem("isAuthenticated");
  };

  // Получение текущего пользователя
  const getCurrentUser = async () => {
    if (!token.value) {
      return null;
    }

    isLoading.value = true;
    try {
      const response = await api.get("/api/auth/me");
      user.value = response.data;
      localStorage.setItem("user", JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      console.error("Ошибка получения данных пользователя:", error);
      logout();
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // Для админов: получение списка пользователей
  const fetchAdminUsers = async (params = {}) => {
    try {
      const response = await api.get("/api/admin/users", { params });
      return response.data;
    } catch (error) {
      console.error("Ошибка загрузки пользователей:", error);
      throw error;
    }
  };

  // Для админов: обновление статуса пользователя
  const updateUserStatus = async (userId, status) => {
    try {
      const response = await api.put(`/api/admin/users/${userId}/status`, {
        status,
      });
      return response.data;
    } catch (error) {
      console.error("Ошибка обновления статуса:", error);
      throw error;
    }
  };

  // Инициализация при загрузке страницы
  const init = async () => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      user.value = JSON.parse(savedUser);
    }

    if (token.value) {
      await getCurrentUser();
    }
  };

  return {
    user,
    token,
    isLoading,
    register,
    login,
    logout,
    getCurrentUser,
    fetchAdminUsers,
    updateUserStatus,
    init,
  };
});
