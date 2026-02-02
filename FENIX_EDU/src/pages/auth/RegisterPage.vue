<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-illustration">
        <div class="illustration-content">
          <div class="illustration-icon">🚀</div>
          <h2 class="illustration-title">Начните обучение сегодня</h2>
          <p class="illustration-text">
            Присоединяйтесь к тысячам студентов, которые уже обучаются на нашей
            платформе
          </p>
        </div>
      </div>

      <div class="auth-form-wrapper">
        <div class="auth-form">
          <div class="form-header">
            <h1 class="form-title">Создать аккаунт</h1>
            <p class="form-subtitle">Заполните форму для регистрации</p>
          </div>

          <form @submit.prevent="handleRegister" class="register-form">
            <div class="name-group">
              <div class="form-group">
                <label for="firstName" class="form-label">Имя</label>
                <div class="input-group">
                  <input
                    v-model="registerData.firstName"
                    type="text"
                    id="firstName"
                    placeholder="Иван"
                    required
                    class="form-input"
                    :class="{ error: errors.firstName }"
                  />
                </div>
                <div v-if="errors.firstName" class="error-message">
                  {{ errors.firstName }}
                </div>
              </div>

              <div class="form-group">
                <label for="lastName" class="form-label">Фамилия</label>
                <div class="input-group">
                  <input
                    v-model="registerData.lastName"
                    type="text"
                    id="lastName"
                    placeholder="Иванов"
                    required
                    class="form-input"
                    :class="{ error: errors.lastName }"
                  />
                </div>
                <div v-if="errors.lastName" class="error-message">
                  {{ errors.lastName }}
                </div>
              </div>
            </div>

            <div class="form-group">
              <label for="email" class="form-label">Email</label>
              <div class="input-group">
                <input
                  v-model="registerData.email"
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
                  v-model="registerData.password"
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  placeholder="Создайте надежный пароль"
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
              <div class="password-requirements">
                <p class="requirements-title">Пароль должен содержать:</p>
                <ul class="requirements-list">
                  <li :class="{ valid: registerData.password.length >= 8 }">
                    Минимум 8 символов
                  </li>
                  <li :class="{ valid: /[A-Z]/.test(registerData.password) }">
                    Заглавную букву
                  </li>
                  <li :class="{ valid: /[0-9]/.test(registerData.password) }">
                    Цифру
                  </li>
                  <li
                    :class="{ valid: /[!@#$%^&*]/.test(registerData.password) }"
                  >
                    Специальный символ
                  </li>
                </ul>
              </div>
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label"
                >Подтверждение пароля</label
              >
              <div class="input-group">
                <input
                  v-model="registerData.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  id="confirmPassword"
                  placeholder="Повторите пароль"
                  required
                  class="form-input"
                  :class="{ error: errors.confirmPassword }"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  {{ showConfirmPassword ? "🙈" : "👁️" }}
                </button>
              </div>
              <div v-if="errors.confirmPassword" class="error-message">
                {{ errors.confirmPassword }}
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Роль</label>
              <div class="role-selector">
                <label
                  :class="[
                    'role-option',
                    { selected: registerData.role === 'student' },
                  ]"
                >
                  <input
                    type="radio"
                    v-model="registerData.role"
                    value="student"
                    class="role-radio"
                  />
                  <div class="role-content">
                    <span class="role-icon">👨‍🎓</span>
                    <div class="role-info">
                      <div class="role-title">Студент</div>
                      <div class="role-description">
                        Доступ к курсам и обучению
                      </div>
                    </div>
                  </div>
                </label>
                <label
                  :class="[
                    'role-option',
                    { selected: registerData.role === 'teacher' },
                  ]"
                >
                  <input
                    type="radio"
                    v-model="registerData.role"
                    value="teacher"
                    class="role-radio"
                  />
                  <div class="role-content">
                    <span class="role-icon">👨‍🏫</span>
                    <div class="role-info">
                      <div class="role-title">Преподаватель</div>
                      <div class="role-description">
                        Создание курсов и преподавание
                      </div>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            <div class="form-group" v-if="registerData.role === 'student'">
              <label for="course" class="form-label">Курс</label>
              <div class="input-group">
                <select
                  v-model="registerData.course"
                  id="course"
                  required
                  class="form-input"
                  :class="{ error: errors.course }"
                >
                  <option value="">Выберите курс</option>
                  <option value="1">1 курс</option>
                  <option value="2">2 курс</option>
                  <option value="3">3 курс</option>
                  <option value="4">4 курс</option>
                </select>
              </div>
              <div v-if="errors.course" class="error-message">
                {{ errors.course }}
              </div>
            </div>

            <div class="form-group" v-if="registerData.role === 'student'">
              <label for="group" class="form-label">Группа</label>
              <div class="input-group">
                <input
                  v-model="registerData.group"
                  type="text"
                  id="group"
                  placeholder="Например: ИС-21-1"
                  required
                  class="form-input"
                  :class="{ error: errors.group }"
                />
              </div>
              <div v-if="errors.group" class="error-message">
                {{ errors.group }}
              </div>
            </div>

            <button type="submit" class="submit-btn" :disabled="isLoading">
              <span v-if="!isLoading">Создать аккаунт</span>
              <span v-else class="loading">⏳</span>
            </button>

            <div class="auth-footer">
              <p class="footer-text">
                Уже есть аккаунт?
                <router-link to="/login" class="auth-link">Войти</router-link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

// Данные формы
const registerData = reactive({
  firstName: "",
  lastName: "",
  email: "",
  password: "",
  confirmPassword: "",
  role: "student",
  course: "",
  group: "",
});

// Ошибки валидации
const errors = reactive({
  firstName: "",
  lastName: "",
  email: "",
  password: "",
  confirmPassword: "",
  course: "",
  group: "",
});

// Состояния
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const isLoading = ref(false);

// Валидация email
const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

// Валидация пароля
const validatePassword = (password) => {
  const requirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*]/.test(password),
  };

  return {
    valid: Object.values(requirements).every(Boolean),
    requirements,
  };
};

watch(
  () => registerData.password,
  (newPassword) => {
    const validation = validatePassword(newPassword);
    if (newPassword && !validation.valid) {
      errors.password = "Пароль не соответствует требованиям";
    } else {
      errors.password = "";
    }
  },
);

watch(
  () => [registerData.password, registerData.confirmPassword],
  () => {
    if (
      registerData.confirmPassword &&
      registerData.password !== registerData.confirmPassword
    ) {
      errors.confirmPassword = "Пароли не совпадают";
    } else {
      errors.confirmPassword = "";
    }
  },
);

// Обработчик регистрации
const handleRegister = async () => {
  Object.keys(errors).forEach((key) => (errors[key] = ""));

  let isValid = true;

  if (!registerData.firstName.trim()) {
    errors.firstName = "Пожалуйста, введите имя";
    isValid = false;
  }

  if (!registerData.lastName.trim()) {
    errors.lastName = "Пожалуйста, введите фамилию";
    isValid = false;
  }

  if (!registerData.email) {
    errors.email = "Пожалуйста, введите email";
    isValid = false;
  } else if (!validateEmail(registerData.email)) {
    errors.email = "Пожалуйста, введите корректный email";
    isValid = false;
  }

  const passwordValidation = validatePassword(registerData.password);
  if (!registerData.password) {
    errors.password = "Пожалуйста, введите пароль";
    isValid = false;
  } else if (!passwordValidation.valid) {
    errors.password = "Пароль не соответствует требованиям";
    isValid = false;
  }

  if (!registerData.confirmPassword) {
    errors.confirmPassword = "Пожалуйста, подтвердите пароль";
    isValid = false;
  } else if (registerData.password !== registerData.confirmPassword) {
    errors.confirmPassword = "Пароли не совпадают";
    isValid = false;
  }

  if (registerData.role === "student") {
    if (!registerData.course) {
      errors.course = "Пожалуйста, выберите курс";
      isValid = false;
    }
    if (!registerData.group.trim()) {
      errors.group = "Пожалуйста, введите группу";
      isValid = false;
    }
  }

  if (!isValid) return;

  isLoading.value = true;

  try {
    // Объединяем имя и фамилию
    const fullName =
      `${registerData.firstName} ${registerData.lastName}`.trim();

    // Вызываем регистрацию
    await authStore.register({
      full_name: fullName,
      email: registerData.email,
      password: registerData.password,
      role: registerData.role,
      course: registerData.role === "student" ? registerData.course : null,
      group: registerData.role === "student" ? registerData.group : null,
    });

    // После успешной регистрации сразу перенаправляем на страницу ожидания
    alert(
      "Регистрация успешна! Ваш аккаунт ожидает подтверждения администратором.",
    );

    // Очищаем поля формы
    Object.keys(registerData).forEach((key) => {
      if (key !== "role") {
        if (typeof registerData[key] === "string") {
          registerData[key] = "";
        }
      }
    });
    registerData.role = "student";

    // Перенаправляем на страницу ожидания
    router.push("/waiting-approval");
  } catch (error) {
    console.error("Ошибка регистрации:", error);

    // Безопасная обработка ошибок
    let errorMessage = "Произошла ошибка при регистрации";

    if (error.response) {
      const responseData = error.response.data;

      if (responseData) {
        if (responseData.detail) {
          if (Array.isArray(responseData.detail)) {
            responseData.detail.forEach((err) => {
              if (err.loc && err.loc[1]) {
                const field = err.loc[1];
                errors[field] = err.msg;
              }
            });
            return;
          } else if (typeof responseData.detail === "string") {
            errorMessage = responseData.detail;
          }
        } else if (responseData.message) {
          errorMessage = responseData.message;
        } else if (responseData.email && Array.isArray(responseData.email)) {
          errors.email = responseData.email[0];
          return;
        } else if (
          responseData.password &&
          Array.isArray(responseData.password)
        ) {
          errors.password = responseData.password[0];
          return;
        }
      }
    } else if (error.request) {
      errorMessage = "Сервер не отвечает. Проверьте подключение к интернету.";
    } else if (error.message) {
      errorMessage = error.message;
    }

    alert(errorMessage);
    errors.email = errorMessage;
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0c3d1 0%, #c8dae8 100%);
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

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.name-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
  padding: 0.75rem 1rem;
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

/* Требования к паролю */
.password-requirements {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.requirements-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.75rem;
}

.requirements-list li {
  color: #c53030;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
}

.requirements-list li:before {
  content: "❌";
  margin-right: 0.5rem;
  font-size: 0.75rem;
}

.requirements-list li.valid {
  color: #22543d;
}

.requirements-list li.valid:before {
  content: "✅";
}

.role-selector {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.role-option {
  flex: 1;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.role-option:hover {
  border-color: #667eea;
  background: #f7fafc;
}

.role-option.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.role-radio {
  display: none;
}

.role-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.role-icon {
  font-size: 1.8rem;
}

.role-info {
  flex: 1;
}

.role-title {
  font-weight: 600;
  color: #2d3748;
  font-size: 0.85rem;
}

.role-description {
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.25rem;
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
  .name-group {
    grid-template-columns: 1fr;
  }

  .role-selector {
    flex-direction: column;
  }

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

  .role-option {
    padding: 0.75rem;
  }

  .role-icon {
    font-size: 1.5rem;
  }
}
</style>
