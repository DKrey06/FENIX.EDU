import { defineStore } from "pinia";
import { ref, computed } from "vue";

const API_URL = "http://127.0.0.1:8000";

export const useMessengerStore = defineStore("messenger", () => {
  const threads = ref([]);
  const totalUnread = ref(0);
  const isLoading = ref(false);
  const currentThread = ref(null);
  const messages = ref([]);

  // Helper function for API calls
  const apiRequest = async (method, endpoint, data = null, params = {}) => {
    const token = localStorage.getItem("access_token");
    const headers = {
      "Content-Type": "application/json",
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const config = {
      method,
      headers,
    };

    if (data && (method === "POST" || method === "PUT" || method === "PATCH")) {
      config.body = JSON.stringify(data);
    }

    // Handle query parameters
    let url = `${API_URL}${endpoint}`;
    if (Object.keys(params).length > 0) {
      const queryParams = new URLSearchParams(params).toString();
      url += `?${queryParams}`;
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `HTTP error! status: ${response.status}`,
        );
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${method} ${endpoint}):`, error);
      throw error;
    }
  };

  // Получить количество непрочитанных сообщений
  const fetchUnreadCount = async () => {
    try {
      const response = await apiRequest("GET", "/api/messenger/unread-count");
      totalUnread.value = response.total_unread;
      return response;
    } catch (error) {
      console.error("Ошибка загрузки уведомлений:", error);
      throw error;
    }
  };

  // Получить список диалогов
  const fetchThreads = async () => {
    isLoading.value = true;
    try {
      const response = await apiRequest("GET", "/api/messenger/threads");
      threads.value = response;
      return response;
    } catch (error) {
      console.error("Ошибка загрузки диалогов:", error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  // Получить список преподавателей
  const fetchTeachers = async (search = "") => {
    try {
      const response = await apiRequest(
        "GET",
        "/api/messenger/teachers",
        null,
        {
          search: search,
          limit: 50,
        },
      );
      return response;
    } catch (error) {
      console.error("Ошибка загрузки преподавателей:", error);
      throw error;
    }
  };

  // Получить сообщения диалога
  const fetchThreadMessages = async (threadId) => {
    isLoading.value = true;
    try {
      const response = await apiRequest(
        "GET",
        `/api/messenger/threads/${threadId}/messages`,
      );
      messages.value = response;
      currentThread.value = threads.value.find((t) => t.id === threadId);
      return response;
    } catch (error) {
      console.error("Ошибка загрузки сообщений:", error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  // Отправить сообщение
  const sendMessage = async (teacherId, content) => {
    try {
      const response = await apiRequest("POST", "/api/messenger/messages", {
        teacher_id: teacherId,
        content: content,
      });
      // Обновляем счетчик непрочитанных
      await fetchUnreadCount();
      return response;
    } catch (error) {
      console.error("Ошибка отправки сообщения:", error);
      throw error;
    }
  };

  // Ответить в диалоге
  const sendReply = async (threadId, content) => {
    try {
      const response = await apiRequest(
        "POST",
        `/api/messenger/messages/${threadId}/reply`,
        {
          content: content,
        },
      );
      // Добавляем сообщение в список
      messages.value.push(response);
      // Обновляем счетчик непрочитанных
      await fetchUnreadCount();
      return response;
    } catch (error) {
      console.error("Ошибка отправки ответа:", error);
      throw error;
    }
  };

  // Пометить диалог как прочитанный
  const markAsRead = async (threadId) => {
    try {
      await apiRequest("POST", `/api/messenger/threads/${threadId}/read`);
      // Обновляем счетчик непрочитанных
      await fetchUnreadCount();
      // Обновляем локальный список диалогов
      const thread = threads.value.find((t) => t.id === threadId);
      if (thread) {
        thread.unread_count = 0;
      }
    } catch (error) {
      console.error("Ошибка отметки как прочитанного:", error);
      throw error;
    }
  };

  // Архивировать диалог
  const archiveThread = async (threadId) => {
    try {
      await apiRequest("POST", `/api/messenger/threads/${threadId}/archive`);
      // Удаляем из списка
      threads.value = threads.value.filter((t) => t.id !== threadId);
      // Обновляем счетчик непрочитанных
      await fetchUnreadCount();
    } catch (error) {
      console.error("Ошибка архивирования диалога:", error);
      throw error;
    }
  };
  const getAvatarInitials = (name) => {
    if (!name) return "👤";
    const parts = name.split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return {
    threads,
    totalUnread,
    isLoading,
    currentThread,
    messages,
    fetchUnreadCount,
    fetchThreads,
    fetchTeachers,
    fetchThreadMessages,
    sendMessage,
    sendReply,
    markAsRead,
    archiveThread,
    getAvatarInitials,
  };
});
