<template>
  <div class="archive-page">
    <div class="main-grid">
      <aside class="sidebar-panel">
        <div class="sidebar-header">
          <h2 class="sidebar-title">FENIX.EDU</h2>
        </div>

        <div class="sidebar-content">
          <div class="sidebar-section">
            <h3 class="section-title">Меню</h3>
            <nav class="navigation-menu">
              <router-link
                to="/"
                class="nav-item"
                :class="{ active: $route.path === '/' }"
              >
                <span class="nav-icon">🏠</span>
                <span class="nav-text">Главная</span>
              </router-link>
              <router-link
                to="/archive"
                class="nav-item"
                :class="{ active: $route.path === '/archive' }"
              >
                <span class="nav-icon">📚</span>
                <span class="nav-text">Архив обучения</span>
              </router-link>
              <router-link
                to="/messages"
                class="nav-item"
                :class="{ active: $route.path === '/messages' }"
              >
                <span class="nav-icon">💬</span>
                <span class="nav-text">Мессенджер</span>
              </router-link>
              <router-link
                to="/discussions"
                class="nav-item"
                :class="{ active: $route.path === '/discussions' }"
              >
                <span class="nav-icon">🗣️</span>
                <span class="nav-text">Обсуждение</span>
              </router-link>
              <router-link
                to="/courses"
                class="nav-item"
                :class="{ active: $route.path === '/courses' }"
              >
                <span class="nav-icon">📖</span>
                <span class="nav-text">Курсы</span>
              </router-link>
            </nav>
          </div>

          <div class="sidebar-section">
            <button class="logout-btn" @click="handleLogout">
              <span class="logout-icon">🚪</span>
              <span class="logout-text">Выход</span>
            </button>
          </div>
        </div>
      </aside>

      <main class="main-content">
        <div class="courses-section">
          <div class="courses-header">
            <h2 class="content-title">Архив обучения</h2>
            <div class="courses-controls">
              <div class="status-buttons">
                <button
                  class="status-btn"
                  :class="{ active: activeTab === 'inProgress' }"
                  @click="setActiveTab('inProgress')"
                >
                  В процессе
                </button>
                <button
                  class="status-btn"
                  :class="{ active: activeTab === 'completed' }"
                  @click="setActiveTab('completed')"
                >
                  Завершенные
                </button>
              </div>
              <div class="filter-container">
                <button class="filter-btn" @click="toggleFilter">Фильтр</button>
                <div class="filter-dropdown" v-if="showFilter">
                  <div class="filter-options">
                    <div
                      class="filter-option"
                      v-for="filter in filters"
                      :key="filter.id"
                    >
                      <input
                        type="checkbox"
                        :id="'filter-' + filter.id"
                        v-model="filter.selected"
                        class="filter-checkbox"
                      />
                      <label :for="'filter-' + filter.id" class="filter-label">
                        <span class="filter-icon">{{
                          getFilterIcon(filter.name)
                        }}</span>
                        {{ filter.name }}
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="courses-container">
            <div class="courses-wrapper">
              <div class="courses-grid">
                <div
                  v-for="course in filteredCourses"
                  :key="course.id"
                  class="course-card"
                  @click="openCourse(course.id)"
                >
                  <div class="course-image">
                    <img
                      src="@/assets/images/Course.png"
                      alt="Course"
                      class="course-img"
                    />
                  </div>
                  <div class="course-header">
                    <span class="course-status" :class="course.status">
                      {{
                        course.status === "inProgress"
                          ? "В процессе"
                          : "Завершен"
                      }}
                    </span>
                  </div>
                  <div class="course-body">
                    <h3 class="course-title">{{ course.title }}</h3>
                    <p class="course-description">
                      {{ course.description }}
                    </p>
                    <div
                      class="course-progress"
                      v-if="course.status === 'inProgress'"
                    >
                      <div class="progress-bar">
                        <div
                          class="progress-fill"
                          :style="{ width: course.progress + '%' }"
                        ></div>
                      </div>
                      <span class="progress-text">{{ course.progress }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const activeTab = ref("inProgress");
const showFilter = ref(false);

// Фильтры
const filters = ref([
  { id: 1, name: "Недавние", selected: false },
  { id: 2, name: "С высоким прогрессом", selected: false },
  { id: 3, name: "С низким прогрессом", selected: false },
  { id: 4, name: "Популярные", selected: false },
  { id: 5, name: "Новые", selected: false },
]);

const getFilterIcon = (filterName) => {
  switch (filterName) {
    case "Недавние":
      return "🕒";
    case "С высоким прогрессом":
      return "📈";
    case "С низким прогрессом":
      return "📉";
    case "Популярные":
      return "🔥";
    case "Новые":
      return "🆕";
    default:
      return "✓";
  }
};

// Курсы с прогрессом и датами
const courses = ref([
  {
    id: 1,
    title: "Математический анализ",
    description: "Основы математического анализа и дифференциальных уравнений",
    status: "inProgress",
    progress: 65,
    date: "2024-01-15",
    isPopular: true,
    isNew: false,
  },
  {
    id: 2,
    title: "Основы программирования",
    description: "Введение в программирование на Python",
    status: "inProgress",
    progress: 85,
    date: "2024-02-10",
    isPopular: true,
    isNew: false,
  },
  {
    id: 3,
    title: "Веб-дизайн",
    description: "Создание современных веб-интерфейсов",
    status: "completed",
    progress: 100,
    date: "2023-12-05",
    isPopular: false,
    isNew: false,
  },
  {
    id: 4,
    title: "Английский язык B2",
    description: "Деловой английский для IT-специалистов",
    status: "inProgress",
    progress: 45,
    date: "2024-03-01",
    isPopular: false,
    isNew: true,
  },
  {
    id: 5,
    title: "История искусств",
    description: "Искусство от античности до современности",
    status: "completed",
    progress: 100,
    date: "2023-11-20",
    isPopular: false,
    isNew: false,
  },
  {
    id: 6,
    title: "Базы данных",
    description: "Проектирование и оптимизация баз данных",
    status: "inProgress",
    progress: 30,
    date: "2024-02-25",
    isPopular: true,
    isNew: true,
  },
  {
    id: 7,
    title: "Алгоритмы и структуры данных",
    description: "Основные алгоритмы и структуры данных",
    status: "inProgress",
    progress: 70,
    date: "2024-01-30",
    isPopular: true,
    isNew: false,
  },
  {
    id: 8,
    title: "Мобильная разработка",
    description: "Создание мобильных приложений",
    status: "inProgress",
    progress: 55,
    date: "2024-02-15",
    isPopular: false,
    isNew: true,
  },
  {
    id: 9,
    title: "Машинное обучение",
    description: "Введение в искусственный интеллект",
    status: "completed",
    progress: 100,
    date: "2023-12-20",
    isPopular: true,
    isNew: false,
  },
  {
    id: 10,
    title: "Философия",
    description: "Основы философской мысли",
    status: "completed",
    progress: 100,
    date: "2023-10-15",
    isPopular: false,
    isNew: false,
  },
  {
    id: 11,
    title: "Экономика",
    description: "Основы экономической теории",
    status: "completed",
    progress: 100,
    date: "2023-09-20",
    isPopular: true,
    isNew: false,
  },
  {
    id: 12,
    title: "Дизайн интерфейсов",
    description: "Проектирование пользовательских интерфейсов",
    status: "inProgress",
    progress: 40,
    date: "2024-03-05",
    isPopular: false,
    isNew: true,
  },
]);

// Фильтрованные курсы
const filteredCourses = computed(() => {
  let result = courses.value.filter(
    (course) => course.status === activeTab.value
  );

  // Применяем фильтры, если выбраны
  const selectedFilters = filters.value
    .filter((f) => f.selected)
    .map((f) => f.name);

  if (selectedFilters.length > 0) {
    // Фильтрация по выбранным критериям
    result = result.filter((course) => {
      return selectedFilters.some((filter) => {
        switch (filter) {
          case "Недавние":
            // Показываем курсы, добавленные в последние 30 дней
            const courseDate = new Date(course.date);
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            return courseDate >= thirtyDaysAgo;

          case "С высоким прогрессом":
            return course.progress >= 70;

          case "С низким прогрессом":
            return course.progress <= 30;

          case "Популярные":
            return course.isPopular;

          case "Новые":
            return course.isNew;

          default:
            return true;
        }
      });
    });
  }

  return result;
});

const setActiveTab = (tab) => {
  activeTab.value = tab;
};

const toggleFilter = () => {
  showFilter.value = !showFilter.value;
};

const closeFilterOnClickOutside = (event) => {
  if (
    showFilter.value &&
    !event.target.closest(".filter-container") &&
    !event.target.closest(".filter-dropdown")
  ) {
    showFilter.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", closeFilterOnClickOutside);
});
onUnmounted(() => {
  document.removeEventListener("click", closeFilterOnClickOutside);
});

// Открытие курса
const openCourse = (courseId) => {
  console.log("Открываем курс из архива:", courseId);
  router.push(`/courses/${courseId}/edit`);
};

// Выход из системы
const handleLogout = () => {
  localStorage.removeItem("isAuthenticated");
  localStorage.removeItem("userData");
  router.push("/login");
};
</script>
<style scoped>
.archive-page {
  min-height: calc(100vh - 200px);
  padding: 2rem;
  background: #e7e7ec;
}

.main-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
  max-width: 1600px;
  margin: 0 auto;
}

.sidebar-panel {
  background: #f5d6d8;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 30px rgba(212, 185, 187, 0.3);
  height: fit-content;
  position: sticky;
  top: 120px;
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

.sidebar-header {
  margin-bottom: 2rem;
  text-align: center;
}

.sidebar-title {
  font-family: "Holtwood One SC", serif;
  font-size: 1.4rem;
  color: #2f4156;
  font-weight: 400;
  margin: 0;
  padding: 0.8rem 1.5rem;
  background: #d3a5b1;
  border-radius: 20px;
  display: inline-block;
  box-shadow: 0 4px 12px rgba(211, 165, 177, 0.3);
  letter-spacing: 0.5px;
  max-width: 100%;
  box-sizing: border-box;
  word-wrap: break-word;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 2rem;
}

.section-title {
  font-size: 1.1rem;
  color: #2f4156;
  margin-bottom: 1rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.navigation-menu {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1rem;
  background: #ffffff;
  border-radius: 12px;
  text-decoration: none;
  color: #2f4156;
  font-weight: 500;
  transition: all 0.3s;
  border: 2px solid rgba(47, 65, 86, 0.1);
  cursor: pointer;
}

.nav-item:hover {
  background: #f8f8f8;
  border-color: #2f4156;
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.1);
}

.nav-item.active {
  background: #ffffff;
  border-color: #2f4156;
  color: #2f4156;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.15);
}

.nav-icon {
  font-size: 1.25rem;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 0.95rem;
  flex: 1;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1rem;
  background: #ffffff;
  border: 2px solid rgba(47, 65, 86, 0.2);
  border-radius: 12px;
  color: #2f4156;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
  margin-top: auto;
  justify-content: center;
}

.logout-btn:hover {
  background: #f8f8f8;
  border-color: #2f4156;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.2);
}

.logout-icon {
  font-size: 1.25rem;
}

.logout-text {
  font-size: 0.95rem;
}

.main-content {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.courses-section {
  background: #f6fbff;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  width: 100%;
}

.courses-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.content-title {
  font-size: 2rem;
  color: #2f4156;
  font-weight: 700;
  margin: 0;
}

.courses-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.status-buttons {
  display: flex;
  gap: 0.5rem;
  background: #ffffff;
  border-radius: 12px;
  padding: 0.25rem;
  border: 2px solid #e7e7ec;
}

.status-btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #2f4156;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.status-btn.active {
  background: #2f4156;
  color: white;
  box-shadow: 0 2px 8px rgba(47, 65, 86, 0.2);
}

.status-btn:hover:not(.active) {
  background: #e7e7ec;
}

.filter-container {
  position: relative;
}

.filter-btn {
  padding: 0.5rem 1.5rem;
  background: #ffffff;
  border: 2px solid #2f4156;
  border-radius: 8px;
  color: #2f4156;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-btn:hover {
  background: #2f4156;
  color: white;
}

.filter-btn::before {
  content: "⚙️";
  font-size: 0.9rem;
}

.filter-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  padding: 1rem;
  min-width: 220px;
  z-index: 100;
  border: 1px solid #e7e7ec;
  max-height: 300px;
  overflow-y: auto;
}

.filter-dropdown::-webkit-scrollbar {
  width: 6px;
}

.filter-dropdown::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.filter-dropdown::-webkit-scrollbar-thumb {
  background: #c8dae8;
  border-radius: 3px;
}

.filter-dropdown::-webkit-scrollbar-thumb:hover {
  background: #a0b9d0;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  transition: background-color 0.2s;
  border-radius: 6px;
}

.filter-option:hover {
  background-color: rgba(47, 65, 86, 0.05);
}

.filter-checkbox {
  width: 18px;
  height: 18px;
  accent-color: #2f4156;
  cursor: pointer;
  margin-right: 8px;
}

.filter-label {
  color: #2f4156;
  font-size: 0.9rem;
  cursor: pointer;
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-icon {
  font-size: 1rem;
  width: 20px;
  text-align: center;
}

.courses-container {
  background: #f6fbff;
  border-radius: 16px;
  padding: 1.5rem;
  width: 100%;
}

.courses-wrapper {
  background: #f6fbff;
  width: 100%;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  width: 100%;
}

.course-card {
  background: #c8dae8;
  border-radius: 16px;
  padding: 1.25rem;
  transition: all 0.3s;
  cursor: pointer;
  border: 2px solid transparent;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(200, 218, 232, 0.4);
  border-color: #2f4156;
}

.course-image {
  width: 100%;
  height: 140px;
  margin-bottom: 1rem;
  border-radius: 12px;
  overflow: hidden;
  background: white;
  flex-shrink: 0;
}

.course-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0.75rem;
}

.course-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
}

.course-status.inProgress {
  background: #2f4156;
  color: white;
}

.course-status.completed {
  background: #48bb78;
  color: white;
}

.course-body {
  margin-bottom: 0.75rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.course-title {
  font-size: 1.1rem;
  color: #2f4156;
  margin-bottom: 0.5rem;
  font-weight: 700;
  line-height: 1.3;
}

.course-description {
  color: #4a5568;
  font-size: 0.85rem;
  line-height: 1.4;
  margin-bottom: 1rem;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.course-progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #2f4156;
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 0.8rem;
  color: #2f4156;
  font-weight: 600;
  min-width: 35px;
}

/* Адаптивность */
@media (max-width: 1400px) {
  .courses-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .main-grid {
    max-width: 1400px;
  }
}

@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .sidebar-panel {
    position: static;
    min-height: auto;
  }
}

@media (max-width: 992px) {
  .courses-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .archive-page {
    padding: 1rem;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }

  .courses-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .courses-controls {
    width: 100%;
    justify-content: space-between;
  }

  .sidebar-title {
    font-size: 1.2rem;
    padding: 0.6rem 1.2rem;
  }

  .course-image {
    height: 160px;
  }

  .course-title {
    font-size: 1.2rem;
  }

  .course-description {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .status-buttons {
    flex-direction: column;
    width: 100%;
  }

  .status-btn {
    width: 100%;
    text-align: center;
  }

  .courses-controls {
    flex-direction: column;
    gap: 1rem;
  }

  .filter-container {
    align-self: flex-start;
  }

  .course-image {
    height: 140px;
  }
}
</style>
