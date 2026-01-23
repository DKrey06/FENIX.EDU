<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-illustration">
        <div class="illustration-content">
          <div class="illustration-icon">🎓</div>
          <h2 class="illustration-title">Добро пожаловать в FENIX.EDU</h2>
          <p class="illustration-text">
            Войдите в свой аккаунт, чтобы продолжить обучение на нашей
            образовательной платформе
          </p>
        </div>
      </div>

      <div class="auth-form-wrapper">
        <div class="auth-form">
          <div class="form-header">
            <h1 class="form-title">Вход в аккаунт</h1>
            <p class="form-subtitle">Введите ваши данные для входа</p>
          </div>

          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <label for="email" class="form-label">Email</label>
              <div class="input-group">
                <input
                  v-model="loginData.email"
                  type="email"
                  id="email"
                  placeholder="student@fenixedu.ru"
                  required
                  class="form-input"
                  :class="{ error: errors.email }"
                />
              </div>
              <div v-if="errors.email" class="error-message">
                {{ errors.email }}
              </div>
            </div>

            <div class="form-group">
              <label for="password" class="form-label">Пароль</label>
              <div class="input-group">
                <input
                  v-model="loginData.password"
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  placeholder="Введите ваш пароль"
                  required
                  class="form-input"
                  :class="{ error: errors.password }"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showPassword = !showPassword"
                >
                  {{ showPassword ? "🙈" : "👁️" }}
                </button>
              </div>
              <div v-if="errors.password" class="error-message">
                {{ errors.password }}
              </div>
            </div>

            <div class="remember-me">
              <input
                type="checkbox"
                id="remember"
                v-model="loginData.remember"
                class="checkbox"
              />
              <label for="remember" class="checkbox-label"
                >Запомнить меня</label
              >
            </div>

            <button type="submit" class="submit-btn" :disabled="isLoading">
              <span v-if="!isLoading">Войти</span>
              <span v-else class="loading">⏳</span>
            </button>

            <div class="auth-footer">
              <p class="footer-text">
                Ещё нет аккаунта?
                <router-link to="/register" class="auth-link"
                  >Зарегистрироваться</router-link
                >
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

// Данные формы
const loginData = reactive({
  email: "",
  password: "",
  remember: false,
});

// Ошибки валидации
const errors = reactive({
  email: "",
  password: "",
});

// Состояния
const showPassword = ref(false);
const isLoading = ref(false);

// Валидация email
const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

// Обработчик входа
const handleLogin = async () => {
  errors.email = "";
  errors.password = "";

  let isValid = true;

  if (!loginData.email) {
    errors.email = "Пожалуйста, введите email";
    isValid = false;
  } else if (!validateEmail(loginData.email)) {
    errors.email = "Пожалуйста, введите корректный email";
    isValid = false;
  }

  if (!loginData.password) {
    errors.password = "Пожалуйста, введите пароль";
    isValid = false;
  } else if (loginData.password.length < 6) {
    errors.password = "Пароль должен содержать минимум 6 символов";
    isValid = false;
  }

  if (!isValid) return;

  isLoading.value = true;

  try {
    await authStore.login(loginData.email, loginData.password);

    // Проверяем статус пользователя после входа
    const user = authStore.user;

    if (user && user.status === "pending") {
      // Если статус "ожидает подтверждения", перенаправляем на waiting-approval
      router.push("/waiting-approval");
    } else if (user && user.status === "active") {
      // Если аккаунт активен, перенаправляем на dashboard
      router.push("/dashboard");
    } else if (user && user.status === "rejected") {
      // Если аккаунт отклонен
      errors.password = "Ваш аккаунт был отклонен администратором";
    } else if (user && user.status === "blocked") {
      // Если аккаунт заблокирован
      errors.password = "Ваш аккаунт заблокирован";
    } else {
      // По умолчанию - на dashboard
      router.push("/dashboard");
    }

    if (loginData.remember) {
      localStorage.setItem("userEmail", loginData.email);
    }
  } catch (error) {
    console.error("Ошибка входа:", error);
    // Показываем пользователю понятное сообщение
    if (error.message.includes("Аккаунт не подтвержден")) {
      errors.password = "Ваш аккаунт ожидает подтверждения администратором";
    } else if (error.message.includes("Неверный email или пароль")) {
      errors.password = "Неверный email или пароль";
    } else {
      errors.password = error.message || "Произошла ошибка при входе";
    }
  } finally {
    isLoading.value = false;
  }
};

// Исправьте демо-данные
const fillDemoCredentials = () => {
  loginData.email = "admin@fenixedu.ru"; // Используем админский аккаунт
  loginData.password = "admin123";
  loginData.remember = true;
};

// Вызываем для демо
fillDemoCredentials();
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #c8dae8 42%, #d3a5b1 69%);
  padding: 2rem;
}

.auth-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1200px;
  width: 100%;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.auth-illustration {
  background: linear-gradient(135deg, #4c51bf 0%, #805ad5 100%);
  color: white;
  padding: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.illustration-content {
  max-width: 400px;
  text-align: center;
}

.illustration-icon {
  font-size: 3.5rem;
  margin-bottom: 1.5rem;
  display: inline-block;
}

.illustration-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.3;
}

.illustration-text {
  font-size: 1rem;
  opacity: 0.9;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.auth-form-wrapper {
  padding: 3rem;
  display: flex;
  align-items: center;
}

.auth-form {
  width: 100%;
  max-width: 380px;
  margin: 0 auto;
}

.form-header {
  margin-bottom: 2rem;
  text-align: center;
}

.form-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  color: #718096;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  margin-bottom: 0.25rem;
}

.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 0.4rem;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input.error {
  border-color: #fc8181;
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: #a0aec0;
  padding: 0;
  height: 100%;
  display: flex;
  align-items: center;
}

.error-message {
  color: #fc8181;
  font-size: 0.8rem;
  margin-top: 0.4rem;
  min-height: 1.2rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.25rem 0;
}

.checkbox {
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
}

.checkbox-label {
  font-size: 0.85rem;
  color: #4a5568;
  cursor: pointer;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.85rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.auth-footer {
  text-align: center;
  padding-top: 1.25rem;
  border-top: 1px solid #e2e8f0;
  margin-top: 0.5rem;
}

.footer-text {
  color: #718096;
  font-size: 0.85rem;
}

.auth-link {
  color: #667eea;
  font-weight: 600;
  text-decoration: none;
  margin-left: 0.5rem;
}

.auth-link:hover {
  text-decoration: underline;
}

/* Адаптивность */
@media (max-width: 992px) {
  .auth-container {
    grid-template-columns: 1fr;
  }

  .auth-illustration {
    padding: 2.5rem;
  }

  .auth-form-wrapper {
    padding: 2.5rem;
  }
}

@media (max-width: 768px) {
  .auth-page {
    padding: 1rem;
  }

  .auth-illustration {
    padding: 2rem;
  }

  .auth-form-wrapper {
    padding: 2rem;
  }

  .illustration-title {
    font-size: 1.5rem;
  }

  .form-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 576px) {
  .auth-illustration {
    padding: 1.5rem;
  }

  .auth-form-wrapper {
    padding: 1.5rem;
  }

  .illustration-title {
    font-size: 1.3rem;
  }

  .form-title {
    font-size: 1.3rem;
  }

  .illustration-icon {
    font-size: 3rem;
  }

  .form-input {
    padding: 0.65rem 0.85rem;
    font-size: 0.9rem;
  }
}
</style>
