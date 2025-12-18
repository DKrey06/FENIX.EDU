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
                <span class="input-icon">📧</span>
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
              <div class="label-row">
                <label for="password" class="form-label">Пароль</label>
                <a href="#" class="forgot-password">Забыли пароль?</a>
              </div>
              <div class="input-group">
                <span class="input-icon">🔒</span>
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
              <label for="remember" class="checkbox-label">Запомнить меня</label>
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
import { useAuthStore } from "../../stores/auth";

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
    await authStore.login({
      email: loginData.email,
      password: loginData.password,
    });

    if (loginData.remember) {
      localStorage.setItem("userEmail", loginData.email);
    }

    router.push("/");
  } catch (error) {
    console.error("Ошибка входа:", error);
    errors.password =
      error.response?.data?.message || "Неверный email или пароль";
  } finally {
    isLoading.value = false;
  }
};

// Автозаполнение для демо
const fillDemoCredentials = () => {
  loginData.email = "student@fenixedu.ru";
  loginData.password = "demo123";
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
  padding: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.illustration-content {
  max-width: 400px;
  text-align: center;
}

.illustration-icon {
  font-size: 4rem;
  margin-bottom: 2rem;
  display: inline-block;
}

.illustration-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  line-height: 1.3;
}

.illustration-text {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 3rem;
  line-height: 1.6;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  text-align: left;
}

.feature {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 1rem;
}

.feature-icon {
  font-size: 1.25rem;
}

.auth-form-wrapper {
  padding: 4rem;
  display: flex;
  align-items: center;
}

.auth-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.form-header {
  margin-bottom: 2.5rem;
  text-align: center;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  color: #718096;
  font-size: 1rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  margin-bottom: 0.5rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-password {
  font-size: 0.875rem;
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.forgot-password:hover {
  text-decoration: underline;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  font-size: 1.25rem;
  color: #a0aec0;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 3rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1rem;
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
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #a0aec0;
  padding: 0;
}

.error-message {
  color: #fc8181;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.5rem 0;
}

.checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
}

.checkbox-label {
  font-size: 0.875rem;
  color: #4a5568;
  cursor: pointer;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 1rem;
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

.social-login {
  margin: 1.5rem 0;
  text-align: center;
}

.social-text {
  color: #718096;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.social-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.social-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.social-btn.google:hover {
  border-color: #db4437;
  background: #f8f8f8;
}

.social-btn.yandex:hover {
  border-color: #ffcc00;
  background: #fffbf0;
}

.social-btn.vk:hover {
  border-color: #4c75a3;
  background: #f0f5fa;
}

.social-icon {
  font-size: 1.1rem;
}

.social-btn.google .social-icon {
  color: #db4437;
}

.social-btn.yandex .social-icon {
  color: #ffcc00;
  font-weight: 700;
}

.social-btn.vk .social-icon {
  color: #4c75a3;
  font-weight: 700;
}

.auth-footer {
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.footer-text {
  color: #718096;
  font-size: 0.875rem;
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
    padding: 3rem;
  }

  .auth-form-wrapper {
    padding: 3rem;
  }
}

@media (max-width: 576px) {
  .auth-page {
    padding: 1rem;
  }

  .auth-illustration {
    padding: 2rem;
  }

  .auth-form-wrapper {
    padding: 2rem;
  }

  .social-buttons {
    flex-direction: column;
  }

  .illustration-title {
    font-size: 1.5rem;
  }

  .form-title {
    font-size: 1.5rem;
  }
}
</style>
