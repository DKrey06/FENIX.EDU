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
          <div v-if="user" class="user-info"> <!-- Изменили userData на user -->
            <p><strong>Имя:</strong> {{ user.full_name }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
            <p><strong>Роль:</strong> {{ roleLabel }}</p>
            <p v-if="user.course"><strong>Курс:</strong> {{ user.course }}</p>
            <p v-if="user.group"><strong>Группа:</strong> {{ user.group }}</p>
          </div>
        </div>
      </div>

      <div class="instructions" v-if="status === 'pending'"> <!-- Изменили user.status на status -->
        <h3>Что дальше?</h3>
        <ul>
          <li>Администратор проверит ваши данные</li>
          <li>Вы получите уведомление на email после подтверждения</li>
          <li>Обычно это занимает до 24 часов</li>
          <li>После подтверждения вы сможете войти в систему</li>
        </ul>
      </div>

      <div class="actions">
        <button @click="refreshStatus" class="refresh-btn">
          Обновить статус
        </button>
        <button @click="logout" class="logout-btn">
          Выйти
        </button>
      </div>

      <div class="contact">
        <p>Есть вопросы? Свяжитесь с администратором:</p>
        <a href="mailto:admin@fenixedu.ru" class="contact-link">
          admin@fenixedu.ru
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const user = ref(null); // Переименовали userData в user
const status = ref('pending');

const statusConfig = {
  pending: {
    icon: '⏳',
    title: 'Ожидание подтверждения',
    message: 'Ваш аккаунт ожидает подтверждения администратором.',
    class: 'pending'
  },
  active: {
    icon: '✅',
    title: 'Аккаунт подтвержден!',
    message: 'Ваш аккаунт успешно подтвержден. Теперь вы можете войти в систему.',
    class: 'active'
  },
  rejected: {
    icon: '❌',
    title: 'Аккаунт отклонен',
    message: 'К сожалению, ваш аккаунт был отклонен администратором.',
    class: 'rejected'
  },
  blocked: {
    icon: '🚫',
    title: 'Аккаунт заблокирован',
    message: 'Ваш аккаунт был заблокирован администратором.',
    class: 'blocked'
  }
};

const statusClass = computed(() => statusConfig[status.value]?.class || 'pending');
const statusIcon = computed(() => statusConfig[status.value]?.icon || '⏳');
const statusTitle = computed(() => statusConfig[status.value]?.title || 'Ожидание подтверждения');
const statusMessage = computed(() => statusConfig[status.value]?.message || 'Ваш аккаунт ожидает подтверждения администратором.');

const roleLabel = computed(() => {
  const labels = {
    student: 'Студент',
    teacher: 'Преподаватель',
    admin: 'Администратор'
  };
  return labels[user.value?.role] || user.value?.role;
});

const checkStatus = async () => {
  try {
    const response = await authStore.checkAccountStatus();
    status.value = response.status;
    user.value = response.user; // Теперь user содержит данные пользователя

    // Если аккаунт активен - перенаправляем на дашборд
    if (response.status === 'active') {
      router.push('/dashboard');
    }
  } catch (error) {
    console.error('Ошибка проверки статуса:', error);
    // Если ошибка 403 (нет доступа) - перенаправляем на логин
    if (error.response?.status === 403) {
      authStore.logout();
      router.push('/login');
    }
  }
};

const refreshStatus = () => {
  checkStatus();
};

const logout = () => {
  authStore.logout();
  router.push('/login');
};

onMounted(() => {
  // Проверяем статус при загрузке страницы
  checkStatus();

  // Автоматически обновляем статус каждые 30 секунд
  setInterval(checkStatus, 30000);
});
</script>

<style scoped>
.waiting-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.container {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  max-width: 500px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

h1 {
  color: #2d3748;
  margin-bottom: 2rem;
  font-size: 2rem;
}

.status-card {
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  border: 2px solid #e2e8f0;
}

.status-card.pending {
  background: #fefcbf;
  border-color: #f6e05e;
}

.status-card.active {
  background: #c6f6d5;
  border-color: #48bb78;
}

.status-card.rejected {
  background: #fed7d7;
  border-color: #f56565;
}

.status-card.blocked {
  background: #e2e8f0;
  border-color: #a0aec0;
}

.status-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.status-info h2 {
  margin-bottom: 0.5rem;
  color: #2d3748;
}

.status-info p {
  color: #4a5568;
  margin-bottom: 1rem;
}

.user-info {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  text-align: left;
  margin-top: 1rem;
}

.user-info p {
  margin: 0.5rem 0;
  color: #4a5568;
}

.instructions {
  text-align: left;
  background: #f7fafc;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.instructions h3 {
  margin-bottom: 1rem;
  color: #2d3748;
}

.instructions ul {
  padding-left: 1.5rem;
  color: #4a5568;
}

.instructions li {
  margin-bottom: 0.5rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.refresh-btn {
  background: #4299e1;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.logout-btn {
  background: #e53e3e;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.contact {
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.contact-link {
  color: #667eea;
  font-weight: 600;
  text-decoration: none;
}

@media (max-width: 576px) {
  .container {
    padding: 2rem;
  }

  .actions {
    flex-direction: column;
  }
}
</style>