<template>
  <div class="course-detail-page">
    <div class="course-header">
      <div class="breadcrumb">
        <router-link to="/courses" class="breadcrumb-link">
          <span class="breadcrumb-icon">←</span>
          Назад к дисциплинам
        </router-link>
      </div>
      <div class="header-content">
        <h1 class="course-title">Название дисциплины</h1>
        <div class="course-meta">
          <div class="meta-item">
            <span class="meta-icon">📚</span>
            <span class="meta-text">Курс на изучении</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">⏰</span>
            <span class="meta-text">До конца курса осталось 15 дней</span>
          </div>
        </div>
      </div>
    </div>

    <div class="course-content">
      <div class="course-sections">
        <div class="sections-header">
          <h2 class="sections-title">Содержание курса</h2>
          <button
            class="edit-btn"
            v-if="isTeacher"
            @click="toggleEditMode"
          >
            <span class="edit-icon">✏️</span>
            {{ isEditMode ? "Сохранить" : "Редактировать" }}
          </button>
        </div>

        <div class="sections-list">
          <div
            class="section-item"
            :class="{ 'section-active': activeSection === 1 }"
          >
            <div class="section-header" @click="toggleSection(1)">
              <div class="section-title">
                <span class="section-number">Раздел I.</span>
                <span class="section-name">Название раздела</span>
              </div>
              <span class="section-toggle">
                {{ activeSection === 1 ? "−" : "+" }}
              </span>
            </div>
            <div class="subsection-list" v-if="activeSection === 1">
              <div class="subsection-item">
                <span class="subsection-icon">📝</span>
                <span class="subsection-name">Тест</span>
                <div class="subsection-status status-completed">✓</div>
              </div>
              <div class="subsection-item">
                <span class="subsection-icon">📄</span>
                <span class="subsection-name">Текстовый документ</span>
                <div class="subsection-status status-completed">✓</div>
              </div>
              <div class="subsection-item">
                <span class="subsection-icon">🎬</span>
                <span class="subsection-name">Видео</span>
                <div class="subsection-status status-pending">▶</div>
              </div>
            </div>
          </div>

          <div
            class="section-item"
            :class="{ 'section-active': activeSection === 2 }"
          >
            <div class="section-header" @click="toggleSection(2)">
              <div class="section-title">
                <span class="section-number">Раздел II.</span>
                <span class="section-name">Название раздела</span>
              </div>
              <span class="section-toggle">
                {{ activeSection === 2 ? "−" : "+" }}
              </span>
            </div>
            <div class="subsection-list" v-if="activeSection === 2">
              <div class="subsection-item">
                <span class="subsection-icon">📚</span>
                <span class="subsection-name">Лекционные материалы</span>
                <div class="subsection-status status-pending">▶</div>
              </div>
              <div class="subsection-item">
                <span class="subsection-icon">🔬</span>
                <span class="subsection-name">Лабораторная работа</span>
                <div class="subsection-status status-locked">🔒</div>
              </div>
            </div>
          </div>

          <div
            class="section-item"
            :class="{ 'section-active': activeSection === 3 }"
          >
            <div class="section-header" @click="toggleSection(3)">
              <div class="section-title">
                <span class="section-number">Раздел III.</span>
                <span class="section-name">Название раздела</span>
              </div>
              <span class="section-toggle">
                {{ activeSection === 3 ? "−" : "+" }}
              </span>
            </div>
          </div>

          <div
            class="section-item"
            :class="{ 'section-active': activeSection === 4 }"
          >
            <div class="section-header" @click="toggleSection(4)">
              <div class="section-title">
                <span class="section-number">Раздел IV.</span>
                <span class="section-name">Название раздела</span>
              </div>
              <span class="section-toggle">
                {{ activeSection === 4 ? "−" : "+" }}
              </span>
            </div>
            <div class="subsection-list" v-if="activeSection === 4">
              <div class="subsection-item">
                <span class="subsection-icon">📝</span>
                <span class="subsection-name">Итоговый тест</span>
                <div class="subsection-status status-locked">🔒</div>
              </div>
            </div>
          </div>

          <button
            class="add-section-btn"
            v-if="isEditMode && isTeacher"
            @click="addNewSection"
          >
            <span class="add-icon">+</span>
            Добавить раздел
          </button>
        </div>
      </div>

      <div class="course-rating">
        <div class="rating-header">
          <h2 class="rating-title">
            <span class="rating-icon">🏆</span>
            Рейтинг
          </h2>
          <div class="rating-info">
            <div class="rating-total">
              Всего: {{ students.length }} студентов
            </div>
          </div>
        </div>

        <div class="rating-list">
          <div
            class="rating-item"
            v-for="(student, index) in students"
            :key="student.id"
          >
            <div class="student-rank">
              <span
                class="rank-number"
                :class="{
                  'rank-gold': index === 0,
                  'rank-silver': index === 1,
                  'rank-bronze': index === 2,
                }"
                >{{ index + 1 }}</span
              >
            </div>
            <div class="student-avatar">
              <div class="avatar-circle">{{ student.initials }}</div>
            </div>
            <div class="student-info">
              <div class="student-name">{{ student.name }}</div>
              <div class="student-group">{{ student.group }}</div>
            </div>
            <div class="student-score">
              <div class="score-value">{{ student.score }} баллов</div>
              <div class="score-progress">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: student.progress + '%' }"
                  ></div>
                </div>
                <div class="progress-text">{{ student.progress }}%</div>
              </div>
            </div>
          </div>
        </div>

        <div class="course-stats">
          <div class="stats-title">Статистика курса</div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon">📊</div>
              <div class="stat-content">
                <div class="stat-value">87%</div>
                <div class="stat-label">Средняя успеваемость</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">✅</div>
              <div class="stat-content">
                <div class="stat-value">92%</div>
                <div class="stat-label">Выполнено заданий</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">👥</div>
              <div class="stat-content">
                <div class="stat-value">{{ students.length }}</div>
                <div class="stat-label">Активных студентов</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">⏱️</div>
              <div class="stat-content">
                <div class="stat-value">15</div>
                <div class="stat-label">Дней до конца</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const isTeacher = computed(() => authStore.user?.role === "teacher");

const isEditMode = ref(false);
const activeSection = ref(1);

const students = ref([
  {
    id: 1,
    name: "Иванов Иван Иванович",
    group: "Б9124-01",
    score: 98,
    progress: 95,
    initials: "ИИ",
  },
  {
    id: 2,
    name: "Петров Петр Петрович",
    group: "Б9124-01",
    score: 96,
    progress: 92,
    initials: "ПП",
  },
  {
    id: 3,
    name: "Сидорова Анна Сергеевна",
    group: "Б9124-02",
    score: 94,
    progress: 90,
    initials: "СА",
  },
  {
    id: 4,
    name: "Кузнецов Алексей Владимирович",
    group: "Б9124-01",
    score: 92,
    progress: 88,
    initials: "КА",
  },
  {
    id: 5,
    name: "Морозова Екатерина Дмитриевна",
    group: "Б9124-02",
    score: 90,
    progress: 85,
    initials: "МЕ",
  },
  {
    id: 6,
    name: "Николаев Денис Олегович",
    group: "Б9124-01",
    score: 88,
    progress: 83,
    initials: "НД",
  },
  {
    id: 7,
    name: "Волкова Ольга Игоревна",
    group: "Б9124-02",
    score: 86,
    progress: 80,
    initials: "ВО",
  },
]);

const toggleEditMode = () => {
  if (!isTeacher.value) return;
  isEditMode.value = !isEditMode.value;
};

const toggleSection = (sectionNumber) => {
  activeSection.value =
    activeSection.value === sectionNumber ? null : sectionNumber;
};

const addNewSection = () => {
  console.log("Добавление нового раздела");
};
</script>

