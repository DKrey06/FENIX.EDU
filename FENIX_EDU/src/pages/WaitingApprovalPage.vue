<!-- WaitingApprovalPage.vue - исправленный код -->
<template>
  <div class="waiting-page">
    <div class="container">
      <div class="icon">⏳</div>
      <h1>Ожидание подтверждения</h1>
      <div class="status-card" :class="statusClass">
        <div class="status-icon">{{ statusIcon }}</div>
        <div class="status-info">
          <h2>{{ statusTitle }}</h2>
          <p>{{ statusMessage }}</p>
          <div v-if="user" class="user-info">
            <p><strong>Имя:</strong> {{ user.full_name }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
            <p><strong>Роль:</strong> {{ roleLabel }}</p>
            <p v-if="user.course"><strong>Курс:</strong> {{ user.course }}</p>
            <p v-if="user.group"><strong>Группа:</strong> {{ user.group }}</p>
          </div>
        </div>
      </div>

      <div class="instructions" v-if="status === 'pending'">
        <h3>Что дальше?</h3>
        <ul>
          <li>Администратор проверит ваши данные</li>
          <li>Вы получите уведомление на email после подтверждения</li>
          <li>Обычно это занимает до 24 часов</li>
          <li>После подтверждения вы сможете войти в систему</li>
        </ul>
      </div>

      <div class="actions">
        <button @click="logout" class="logout-btn">Выйти</button>
      </div>

      <div class="contact">
        <p>Есть вопросы? Свяжитесь с администратором:</p>
        <a class="contact-link"> admin@fenixedu.ru </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const user = ref(null);
const status = ref("pending");
let intervalId = null;

const statusConfig = {
  pending: {
    icon: "",
    title: "Ожидание подтверждения",
    message: "Ваш аккаунт ожидает подтверждения администратором.",
    class: "pending",
  },
  active: {
    icon: "",
    title: "Аккаунт подтвержден!",
    message:
      "Ваш аккаунт успешно подтвержден. Теперь вы можете войти в систему.",
    class: "active",
  },
  rejected: {
    icon: "",
    title: "Аккаунт отклонен",
    message: "К сожалению, ваш аккаунт был отклонен администратором.",
    class: "rejected",
  },
  blocked: {
    icon: "",
    title: "Аккаунт заблокирован",
    message: "Ваш аккаунт был заблокирован администратором.",
    class: "blocked",
  },
};

const statusClass = computed(
  () => statusConfig[status.value]?.class || "pending",
);
const statusIcon = computed(() => statusConfig[status.value]?.icon || "⏳");
const statusTitle = computed(
  () => statusConfig[status.value]?.title || "Ожидание подтверждения",
);
const statusMessage = computed(
  () =>
    statusConfig[status.value]?.message ||
    "Ваш аккаунт ожидает подтверждения администратором.",
);

const roleLabel = computed(() => {
  const labels = {
    student: "Студент",
    teacher: "Преподаватель",
    admin: "Администратор",
    department_head: "Руководитель отдела",
  };
  return labels[user.value?.role] || user.value?.role;
});

const checkStatus = () => {
  // Для неаутентифицированных пользователей просто показываем ожидание
  if (!authStore.isAuthenticated) {
    status.value = "pending";
    // Попытаемся получить данные из localStorage если они есть
    try {
      const savedUser = localStorage.getItem("user_data");
      if (savedUser) {
        user.value = JSON.parse(savedUser);
        status.value = user.value.status || "pending";
      }
    } catch (error) {
      console.error("Ошибка чтения данных пользователя:", error);
    }
    return;
  }

  // Для аутентифицированных пользователей проверяем статус
  const currentUser = authStore.user;
  if (currentUser) {
    status.value = currentUser.status || "pending";
    user.value = currentUser;

    // Если аккаунт активен - перенаправляем на дашборд
    if (status.value === "active") {
      router.push("/dashboard");
    }
  }
};

const refreshStatus = () => {
  checkStatus();
};

const logout = () => {
  authStore.logout();
  router.push("/login");
};

const goToLogin = () => {
  router.push("/login");
};

onMounted(() => {
  checkStatus();

  // Автоматически обновляем статус каждые 30 секунд
  intervalId = setInterval(checkStatus, 30000);
});

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});
</script>
<style scoped>
.waiting-page {
  min-height: 100vh;
  padding: 3rem 1rem;
  background: linear-gradient(135deg, #f6fbff, #e7e7ec);
  display: flex;
  align-items: center;
  justify-content: center;
}

.container {
  max-width: 640px;
  width: 100%;
  background: #ffffff;
  border-radius: 24px;
  padding: 2.5rem 2.5rem 2rem;
  box-shadow: 0 16px 40px rgba(47, 65, 86, 0.18);
  text-align: center;
}

.icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

h1 {
  font-size: 1.9rem;
  margin: 0 0 0.5rem;
  color: #2f4156;
  font-weight: 700;
}

.container > p {
  margin: 0;
  color: #4a5568;
}

.status-card {
  margin-top: 1.75rem;
  padding: 1.5rem 1.75rem;
  border-radius: 16px;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  text-align: left;
}

.status-card.pending {
  background: #fff7e6;
  border: 1px solid #f6ad55;
}

.status-card.active {
  background: #e6fffa;
  border: 1px solid #38b2ac;
}

.status-card.rejected {
  background: #ffe6e6;
  border: 1px solid #f56565;
}

.status-card.blocked {
  background: #edf2f7;
  border: 1px solid #a0aec0;
}

.status-icon {
  font-size: 2rem;
  flex-shrink: 0;
  margin-top: 0.2rem;
}

.status-info h2 {
  margin: 0 0 0.3rem;
  font-size: 1.2rem;
  color: #2d3748;
  font-weight: 600;
}

.status-info p {
  margin: 0 0 0.5rem;
  color: #4a5568;
  font-size: 0.95rem;
}

.user-info {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px dashed #cbd5e0;
  font-size: 0.92rem;
  color: #2d3748;
}

.user-info p {
  margin: 0.2rem 0;
}

.instructions {
  margin-top: 1.75rem;
  text-align: left;
}

.instructions h3 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
  color: #2f4156;
  font-weight: 600;
}

.instructions ul {
  margin: 0;
  padding-left: 1.1rem;
  color: #4a5568;
  font-size: 0.95rem;
}

.instructions li + li {
  margin-top: 0.25rem;
}

.actions {
  margin-top: 2rem;
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
}

.refresh-btn,
.logout-btn {
  padding: 0.6rem 1.4rem;
  border-radius: 999px;
  border: 1px solid transparent;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn {
  background: #2f4156;
  color: #ffffff;
  border-color: #2f4156;
}

.refresh-btn:hover {
  background: #233244;
}

.logout-btn {
  background: #ffffff;
  color: #2f4156;
  border-color: #cbd5e0;
}

.logout-btn:hover {
  border-color: #2f4156;
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.18);
}

.contact {
  margin-top: 1.75rem;
  font-size: 0.9rem;
  color: #718096;
}

.contact-link {
  display: inline-block;
  margin-top: 0.25rem;
  color: #2f4156;
  font-weight: 500;
  text-decoration: none;
}

.contact-link:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .waiting-page {
    padding: 1.5rem 1rem;
  }

  .container {
    padding: 1.8rem 1.4rem 1.5rem;
    border-radius: 20px;
  }

  h1 {
    font-size: 1.6rem;
  }

  .status-card {
    flex-direction: column;
  }

  .status-icon {
    margin-bottom: 0.25rem;
  }
}
</style>
