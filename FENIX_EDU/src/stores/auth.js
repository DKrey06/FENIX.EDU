import { defineStore } from "pinia";
import { ref, computed } from "vue";

const API_URL = "http://127.0.0.1:8000/api";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const isAuthenticated = ref(false);
  const isAdmin = ref(false);
  const isCheckingAuth = ref(false);
  const lastAuthCheck = ref(0);
  const authCheckInterval = 5 * 60 * 1000;

  const isTeacher = computed(() => user.value?.role === "teacher");
  const isStudent = computed(() => user.value?.role === "student");

  const init = () => {
    const token = localStorage.getItem("access_token");
    if (token) {
      const now = Date.now();
      if (now - lastAuthCheck.value > authCheckInterval) {
        getCurrentUser().catch(console.error);
      } else {
        try {
          const savedUser = localStorage.getItem("user_data");
          if (savedUser) {
            user.value = JSON.parse(savedUser);
            isAuthenticated.value = true;
            isAdmin.value =
              user.value?.role === "admin" ||
              user.value?.role === "department_head";
          }
        } catch (error) {
          console.error("Ошибка парсинга user_data:", error);
          localStorage.removeItem("user_data");
        }
      }
    }
  };

  const getCurrentUser = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      clearUserData();
      return null;
    }

    if (isCheckingAuth.value) {
      return user.value;
    }

    isCheckingAuth.value = true;

    try {
      console.log(
        "Отправляем запрос к /auth/me с токеном:",
        token.substring(0, 20) + "..."
      );

      const response = await fetch(`${API_URL}/auth/me`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      });

      console.log("Ответ от /auth/me:", response.status, response.statusText);

      if (response.ok) {
        const data = await response.json();
        console.log("Данные пользователя получены:", data);

        user.value = data.user || data;
        isAuthenticated.value = true;
        isAdmin.value =
          user.value?.role === "admin" ||
          user.value?.role === "department_head";

        if (!user.value.status) {
          user.value.status = "pending";
        }

        localStorage.setItem("user_data", JSON.stringify(user.value));
        lastAuthCheck.value = Date.now();

        return user.value;
      } else {
        console.warn(
          "Не удалось получить данные пользователя:",
          response.status
        );

        if (response.status === 401) {
          console.log("Токен истек или невалиден");
          try {
            const newToken = await refreshToken();
            if (newToken) {
              return getCurrentUser();
            }
          } catch (refreshError) {
            console.error("Не удалось обновить токен:", refreshError);
            logout();
          }
        }

        clearUserData();
        return null;
      }
    } catch (error) {
      console.error("Ошибка получения информации о пользователе:", error);
      clearUserData();
      return null;
    } finally {
      isCheckingAuth.value = false;
    }
  };

  const login = async (email, password) => {
    try {
      console.log(
        "Попытка входа с email:",
        email,
        "и паролем:",
        password ? "***" : "нет"
      );

      const loginData = {
        email: email,
        password: password,
      };

      console.log("Отправляемые данные:", JSON.stringify(loginData));

      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(loginData),
      });

      console.log("Статус ответа:", response.status);
      console.log("Заголовки ответа:", response.headers);

      const responseText = await response.text();
      console.log("Тело ответа:", responseText);

      if (!response.ok) {
        let errorDetail;
        try {
          const errorData = JSON.parse(responseText);
          errorDetail =
            errorData.detail || errorData.message || JSON.stringify(errorData);
        } catch {
          errorDetail = responseText;
        }

        console.error("Ошибка от сервера:", errorDetail);
        throw new Error(errorDetail || `Ошибка входа: ${response.status}`);
      }

      const data = JSON.parse(responseText);
      console.log("Успешный ответ от сервера:", data);

      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
        if (data.refresh_token) {
          localStorage.setItem("refresh_token", data.refresh_token);
        }

        await getCurrentUser();

        return data;
      } else {
        throw new Error("Токен не получен от сервера");
      }
    } catch (error) {
      console.error("Полная ошибка входа:", error);
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      console.log("Отправка данных регистрации:", JSON.stringify(userData));

      const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(userData),
      });

      const responseText = await response.text();
      console.log("Ответ регистрации:", response.status, responseText);

      if (!response.ok) {
        let errorData;
        try {
          errorData = JSON.parse(responseText);
        } catch {
          errorData = {
            message: responseText || `Ошибка регистрации: ${response.status}`,
          };
        }

        const error = new Error(
          errorData.message || `Ошибка регистрации: ${response.status}`
        );
        error.response = {
          status: response.status,
          data: errorData,
        };
        throw error;
      }

      const data = JSON.parse(responseText);
      console.log("Успешная регистрация:", data);
      return data;
    } catch (error) {
      console.error("Ошибка регистрации:", error);

      if (error.response) {
        throw error;
      }

      const structuredError = new Error(error.message || "Ошибка регистрации");
      structuredError.response = {
        status: 0,
        data: { message: error.message },
      };
      throw structuredError;
    }
  };

  const logout = () => {
    clearUserData();

    if (
      window.location.pathname !== "/login" &&
      window.location.pathname !== "/"
    ) {
      window.location.href = "/login";
    }
  };

  const clearUserData = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_data");
    user.value = null;
    isAuthenticated.value = false;
    isAdmin.value = false;
    lastAuthCheck.value = 0;
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        throw new Error("Refresh token не найден");
      }

      console.log("Пытаемся обновить токен...");

      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка обновления токена: ${response.status}`);
      }

      const data = await response.json();
      console.log("Токен обновлен успешно");

      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
        if (data.refresh_token) {
          localStorage.setItem("refresh_token", data.refresh_token);
        }
        return data.access_token;
      } else {
        throw new Error("Новый токен не получен");
      }
    } catch (error) {
      console.error("Ошибка обновления токена:", error);
      logout();
      throw error;
    }
  };

  const fetchAdminUsers = async (params = {}) => {
    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("Токен не найден");
      }

      const queryParams = new URLSearchParams();
      queryParams.append("page", params.page || 1);
      queryParams.append("limit", params.limit || 20);

      if (params.status && params.status.trim() !== "") {
        queryParams.append("status", params.status);
      }
      if (params.role && params.role.trim() !== "") {
        queryParams.append("role", params.role);
      }

      console.log(
        "Запрос к /admin/users с параметрами:",
        queryParams.toString()
      );

      const response = await fetch(
        `${API_URL}/admin/users?${queryParams.toString()}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            Accept: "application/json",
          },
        }
      );

      console.log("Ответ от /admin/users:", response.status);

      if (!response.ok) {
        if (response.status === 401) {
          const newToken = await refreshToken();
          if (newToken) {
            return fetchAdminUsers(params);
          }
        }

        const errorText = await response.text();
        console.error("Ошибка ответа:", errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Ошибка загрузки пользователей:", error);
      throw error;
    }
  };

  const fetchPendingUsers = async (params = {}) => {
    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("Токен не найден");
      }

      const queryParams = new URLSearchParams();
      queryParams.append("status", "pending");
      queryParams.append("page", params.page || 1);
      queryParams.append("limit", params.limit || 10);

      const response = await fetch(
        `${API_URL}/admin/users?${queryParams.toString()}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            Accept: "application/json",
          },
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          await refreshToken();
          return fetchPendingUsers(params);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Ошибка загрузки ожидающих пользователей:", error);
      throw error;
    }
  };

  const approveUser = async (userId) => {
    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("Токен не найден");
      }

      const response = await fetch(`${API_URL}/admin/users/${userId}/approve`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          await refreshToken();
          return approveUser(userId);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Ошибка подтверждения пользователя:", error);
      throw error;
    }
  };

  const rejectUser = async (userId) => {
    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("Токен не найден");
      }

      const response = await fetch(`${API_URL}/admin/users/${userId}/reject`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          await refreshToken();
          return rejectUser(userId);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Ошибка отклонения пользователя:", error);
      throw error;
    }
  };

  const updateUserStatus = async (userId, status) => {
    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("Токен не найден");
      }

      const response = await fetch(`${API_URL}/admin/users/${userId}/status`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ status }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          await refreshToken();
          return updateUserStatus(userId, status);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Ошибка обновления статуса:", error);
      throw error;
    }
  };

  const checkAccountStatus = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("Токен не найден");
      }

      const response = await fetch(`${API_URL}/auth/me`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const userData = data.user || data;

      return {
        status: userData.status || "pending",
        user: userData,
      };
    } catch (error) {
      console.error("Ошибка проверки статуса:", error);
      throw error;
    }
  };

  init();

  return {
    user: computed(() => user.value),
    isAuthenticated: computed(() => isAuthenticated.value),
    isAdmin: computed(() => isAdmin.value),
    isTeacher,
    isStudent,
    init,
    getCurrentUser,
    login,
    register,
    logout,
    refreshToken,
    fetchAdminUsers,
    fetchPendingUsers,
    approveUser,
    rejectUser,
    updateUserStatus,
    checkAccountStatus,
  };
});
