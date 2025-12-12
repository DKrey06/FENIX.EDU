<template>
  <header class="header">
    <div class="header__container">
      <div class="header__brand">
        <router-link to="/" class="logo-link">
          <div class="logo">
            <span class="logo__icon">🎓</span>
            <h1 class="logo__text">FENIX.EDU</h1>
          </div>
        </router-link>
      </div>

      <div class="header__search" v-if="!isAuthPage">
        <div class="search-box">
          <input
            type="text"
            placeholder="Поиск по курсам..."
            class="search-input"
          />
          <button class="search-btn">
            <span class="search-icon">🔍</span>
          </button>
        </div>
      </div>

      <div class="header__actions">
        <button class="notification-btn" v-if="!isAuthPage">
          <span class="notification-icon">🔔</span>
          <span class="notification-badge" v-if="notificationsCount > 0">
            {{ notificationsCount }}
          </span>
        </button>

        <div class="user-name" v-if="isAuthenticated && !isAuthPage">
          {{ userName }}
        </div>

        <div
          class="user-logo-container"
          @click="toggleProfileInfo"
          v-if="isAuthenticated && !isAuthPage"
          ref="userLogo"
        >
          <img :src="userLogoUrl" alt="User Logo" class="user-logo" />
          <span class="user-logo-badge" v-if="hasNotifications">!</span>
        </div>

        <div class="auth-buttons" v-if="!isAuthenticated">
          <router-link
            to="/login"
            class="auth-btn login-btn"
            :class="{ active: isLoginPage }"
          >
            <span class="auth-btn__text">Войти</span>
          </router-link>
          <router-link
            to="/register"
            class="auth-btn register-btn"
            :class="{ active: isRegisterPage }"
          >
            <span class="auth-btn__text">Регистрация</span>
          </router-link>
        </div>

        <!-- Плашка с информацией о профиле -->
        <div
          class="profile-info-panel"
          v-if="showProfileInfo && isAuthenticated"
          ref="profilePanel"
          :style="panelStyle"
        >
          <div class="profile-info-header">
            <div class="profile-avatar">
              <img :src="userLogoUrl" alt="User Avatar" class="avatar-image" />
            </div>
            <div class="profile-main-info">
              <h3 class="profile-name">{{ userName }}</h3>
              <div class="profile-role">{{ userRole }}</div>
              <div class="profile-email">{{ userEmail }}</div>
            </div>
            <button class="close-btn" @click.stop="showProfileInfo = false">
              ×
            </button>
          </div>

          <div class="profile-info-content">
            <div class="info-section">
              <h4 class="section-title">Учебная информация</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Группа:</span>
                  <span class="info-value">{{ userGroup }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Курс:</span>
                  <span class="info-value">{{ userCourse }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Факультет:</span>
                  <span class="info-value">{{ userFaculty }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Статус:</span>
                  <span class="info-value status-active">Активный</span>
                </div>
              </div>
            </div>

            <div class="info-section">
              <h4 class="section-title">Статистика</h4>
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">8</div>
                  <div class="stat-label">Курсов</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">4</div>
                  <div class="stat-label">В процессе</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">75%</div>
                  <div class="stat-label">Прогресс</div>
                </div>
              </div>
            </div>
          </div>

          <div class="profile-info-footer">
            <router-link to="/profile" class="profile-link">
              <span class="link-icon">👤</span>
              <span class="link-text">Мой профиль</span>
            </router-link>
            <button class="btn btn-logout" @click="handleLogout">
              <span class="btn-icon">🚪</span>
              <span class="btn-text">Выйти</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import userLogoCat from "@/assets/images/cat-logo.png";

const router = useRouter();
const route = useRoute();
const notificationsCount = ref(3);
const isAuthenticated = ref(false);
const showProfileInfo = ref(false);
const userLogo = ref(null);
const profilePanel = ref(null);

const userLogoUrl = userLogoCat;

// Данные пользователя
const userData = ref({
  firstName: "Иван",
  lastName: "Иванов",
  email: "student@fenixedu.ru",
  role: "student",
  group: "Б9124-01.03.02сп",
  course: "2 курс",
  faculty: "Прикладная математика и информатика",
});

const isAuthPage = computed(() => {
  return route.path === "/login" || route.path === "/register";
});

const isLoginPage = computed(() => {
  return route.path === "/login";
});

const isRegisterPage = computed(() => {
  return route.path === "/register";
});

const userName = computed(() => {
  return `${userData.value.firstName} ${userData.value.lastName}`;
});

const userRole = computed(() => {
  return userData.value.role === "teacher" ? "Преподаватель" : "Студент";
});

const userEmail = computed(() => userData.value.email);
const userGroup = computed(() => userData.value.group);
const userCourse = computed(() => userData.value.course);
const userFaculty = computed(() => userData.value.faculty);
const hasNotifications = computed(() => notificationsCount.value > 0);

const panelStyle = computed(() => {
  if (!userLogo.value) return {};

  const rect = userLogo.value.getBoundingClientRect();
  return {
    right: "0",
    top: `${rect.height + 10}px`,
  };
});

// Проверка авторизации
onMounted(() => {
  isAuthenticated.value = localStorage.getItem("isAuthenticated") === "true";

  const savedData = localStorage.getItem("userData");
  if (savedData) {
    try {
      const parsedData = JSON.parse(savedData);
      userData.value = { ...userData.value, ...parsedData };
    } catch (error) {
      console.error("Ошибка при загрузке данных пользователя:", error);
    }
  }

  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});

const handleClickOutside = (event) => {
  if (
    profilePanel.value &&
    !profilePanel.value.contains(event.target) &&
    userLogo.value &&
    !userLogo.value.contains(event.target)
  ) {
    showProfileInfo.value = false;
  }
};

const toggleProfileInfo = () => {
  if (isAuthenticated.value) {
    showProfileInfo.value = !showProfileInfo.value;
  }
};

const handleLogout = () => {
  localStorage.removeItem("isAuthenticated");
  localStorage.removeItem("userData");
  isAuthenticated.value = false;
  showProfileInfo.value = false;
  router.push("/login");
};

window.addEventListener("storage", (event) => {
  if (event.key === "isAuthenticated") {
    isAuthenticated.value = event.newValue === "true";
  }
});
</script>

<style scoped>
.header {
  background: white;
  box-shadow: 0 2px 15px rgba(212, 185, 187, 0.2);
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header__container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  gap: 2rem;
  position: relative;
}

.header__brand {
  min-width: 180px;
}

.logo-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.logo__icon {
  font-size: 2rem;
}

.logo__text {
  font-size: 1.5rem;
  font-weight: 800;
  color: #2f4156;
  margin: 0;
}

.logo-link:hover .logo__text {
  color: #1a2530;
}

.header__search {
  flex: 1;
  max-width: 400px;
}

.search-box {
  display: flex;
  background: #e7e7ec;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.search-box:focus-within {
  border-color: #2f4156;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  outline: none;
  color: #2f4156;
  font-size: 0.95rem;
}

.search-input::placeholder {
  color: #a0aec0;
}

.search-btn {
  background: #2f4156;
  color: white;
  border: none;
  padding: 0 1.25rem;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover {
  background: #1a2530;
}

.search-icon {
  font-size: 1rem;
}

.header__actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  position: relative;
}

.notification-btn {
  position: relative;
  background: transparent;
  border: none;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 1.25rem;
  color: #2f4156;
}

.notification-btn:hover {
  background: #e7e7ec;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #f0c3d1;
  color: #2f4156;
  font-size: 0.75rem;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.user-name {
  font-weight: 600;
  color: #2f4156;
  font-size: 0.95rem;
  padding: 0.5rem 1rem;
  background: rgba(200, 218, 232, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(200, 218, 232, 0.4);
}

.user-logo-container {
  position: relative;
  width: 40px;
  height: 40px;
  cursor: pointer;
  transition: transform 0.3s;
}

.user-logo-container:hover {
  transform: scale(1.1);
}

.user-logo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f0c3d1;
  box-shadow: 0 4px 12px rgba(240, 195, 209, 0.3);
}

.user-logo-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: #ff4757;
  color: white;
  font-size: 0.7rem;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border: 2px solid white;
}

.auth-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.auth-btn {
  padding: 0.75rem 1.25rem;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.login-btn {
  background: transparent;
  color: #2f4156;
  border: 2px solid #2f4156;
}

.login-btn:hover,
.login-btn.active {
  background: #2f4156;
  color: white;
}

.register-btn {
  background: #2f4156;
  color: white;
  border: 2px solid #2f4156;
}

.register-btn:hover,
.register-btn.active {
  background: #1a2530;
  border-color: #1a2530;
}

.profile-info-panel {
  position: absolute;
  right: 0;
  width: 350px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  padding: 1.5rem;
  z-index: 1001;
  border: 1px solid rgba(212, 185, 187, 0.3);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.profile-info-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e7e7ec;
  position: relative;
}

.profile-avatar {
  width: 60px;
  height: 60px;
  margin-right: 1rem;
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #f0c3d1;
}

.profile-main-info {
  flex: 1;
}

.profile-name {
  font-size: 1.25rem;
  color: #2f4156;
  margin: 0 0 0.25rem 0;
  font-weight: 600;
}

.profile-role {
  font-size: 0.9rem;
  color: #667eea;
  font-weight: 500;
  margin-bottom: 0.25rem;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.profile-email {
  font-size: 0.85rem;
  color: #718096;
}

.close-btn {
  position: absolute;
  top: 0;
  right: 0;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #a0aec0;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s;
}

.close-btn:hover {
  background: #e7e7ec;
  color: #2f4156;
}

.profile-info-content {
  margin-bottom: 1.5rem;
}

.info-section {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 0.95rem;
  color: #4a5568;
  font-weight: 600;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  background: rgba(200, 218, 232, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(200, 218, 232, 0.2);
}

.info-label {
  font-weight: 600;
  color: #2f4156;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
}

.info-value {
  color: #4a5568;
  font-size: 0.9rem;
}

.info-value.status-active {
  color: #48bb78;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  text-align: center;
}

.stat-item {
  padding: 0.75rem;
  background: linear-gradient(
    135deg,
    rgba(240, 195, 209, 0.2) 0%,
    rgba(200, 218, 232, 0.2) 100%
  );
  border-radius: 8px;
  border: 1px solid rgba(212, 185, 187, 0.3);
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2f4156;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.8rem;
  color: #718096;
}

.profile-info-footer {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #e7e7ec;
}

.profile-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(200, 218, 232, 0.2);
  border-radius: 8px;
  text-decoration: none;
  color: #2f4156;
  font-weight: 500;
  transition: all 0.3s;
}

.profile-link:hover {
  background: rgba(200, 218, 232, 0.4);
  transform: translateX(5px);
}

.link-icon {
  font-size: 1.1rem;
}

.link-text {
  font-size: 0.95rem;
}

.btn-logout {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f0c3d1;
  color: #2f4156;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.95rem;
}

.btn-logout:hover {
  background: #d3a5b1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(211, 165, 177, 0.3);
}

.btn-icon {
  font-size: 1.1rem;
}

.btn-text {
  font-size: 0.95rem;
}

/* Адаптивность */
@media (max-width: 768px) {
  .header {
    padding: 1rem;
  }

  .header__container {
    flex-wrap: wrap;
    gap: 1rem;
  }

  .header__search {
    order: 3;
    flex: 100%;
    max-width: none;
  }

  .logo__text {
    font-size: 1.25rem;
  }

  .user-name {
    display: none;
  }

  .auth-btn__text {
    display: none;
  }

  .auth-btn {
    padding: 0.75rem;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .profile-info-panel {
    width: 280px;
    right: -20px;
  }
}

@media (max-width: 480px) {
  .header__brand {
    min-width: auto;
  }

  .logo__text {
    display: none;
  }

  .header__actions {
    gap: 1rem;
  }

  .notification-btn {
    padding: 0.25rem;
  }

  .user-logo-container {
    width: 36px;
    height: 36px;
  }
}
</style>
