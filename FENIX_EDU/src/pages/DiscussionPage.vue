<template>
  <div class="discussion-page">
    <div class="discussion-container">
      <div class="discussion-section">
        <div class="discussion-header">
          <h2 class="content-title">Обсуждения</h2>
          <div class="search-box">
            <input
              type="text"
              placeholder="Поиск по обсуждениям..."
              class="search-input"
            />
            <button class="search-btn">🔍</button>
          </div>
        </div>

        <div class="discussion-content-wrapper">
          <div class="sections-sidebar">
            <h3 class="sidebar-title">Разделы курса</h3>
            <div class="sections-list">
              <div
                v-for="section in sections"
                :key="section.id"
                class="section-item"
                :class="{ active: activeSection === section.id }"
                @click="setActiveSection(section.id)"
              >
                <span class="section-icon">{{ section.icon }}</span>
                <span class="section-text">{{ section.name }}</span>
              </div>
            </div>
          </div>

          <div class="discussion-content">
            <div class="current-section">
              <h3 class="section-title">{{ getActiveSectionName() }}</h3>
              <p class="section-description">
                {{ getActiveSectionDescription() }}
              </p>
            </div>

            <div class="messages-list">
              <div
                v-for="message in filteredMessages"
                :key="message.id"
                class="message"
                :class="message.type"
              >
                <div class="message__header">
                  <div class="message__author">
                    <span class="author-avatar">{{ message.avatar }}</span>
                    <div class="author-info">
                      <span class="author-name">{{ message.author }}</span>
                      <span class="author-role">{{ message.role }}</span>
                    </div>
                  </div>
                  <span class="message__time">{{ message.time }}</span>
                </div>
                <div class="message__content">
                  <h4 v-if="message.title">{{ message.title }}</h4>
                  <p>{{ message.content }}</p>
                </div>
              </div>
            </div>

            <div class="ask-question">
              <h3 class="ask-title">Задать вопрос</h3>
              <div class="ask-form">
                <textarea
                  v-model="newQuestion"
                  placeholder="Введите ваш вопрос..."
                  class="question-input"
                  rows="4"
                ></textarea>
                <div class="ask-actions">
                  <button class="btn btn--primary" @click="submitQuestion">
                    Отправить
                  </button>
                  <button class="btn btn--secondary" @click="clearQuestion">
                    Очистить
                  </button>
                </div>
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
import { useRouter } from "vue-router";

const router = useRouter();

// Активный раздел
const activeSection = ref(1);
const newQuestion = ref("");

// Разделы курса
const sections = ref([
  {
    id: 1,
    name: "Введение в курс",
    icon: "📖",
    description: "Основные понятия и введение в тему курса",
  },
  {
    id: 2,
    name: "Тема 1: Основные концепции",
    icon: "🔍",
    description: "Изучение фундаментальных концепций предмета",
  },
  {
    id: 3,
    name: "Тема 2: Практические задания",
    icon: "💻",
    description: "Выполнение практических заданий и упражнений",
  },
  {
    id: 4,
    name: "Тема 3: Проектная работа",
    icon: "🚀",
    description: "Работа над финальным проектом курса",
  },
  {
    id: 5,
    name: "FAQ и помощь",
    icon: "❓",
    description: "Часто задаваемые вопросы и техническая поддержка",
  },
]);

// Сообщения в обсуждениях
const messages = ref([
  {
    id: 1,
    sectionId: 1,
    author: "Иван Иванов",
    role: "Студент",
    avatar: "👨‍🎓",
    title: "Вопрос по введению в курс",
    content: "Не могу найти материалы по первой лекции. Где их можно скачать?",
    type: "student",
    time: "15:30",
  },
  {
    id: 2,
    sectionId: 1,
    author: "Мария Петрова",
    role: "Преподаватель",
    avatar: "👩‍🏫",
    title: "",
    content:
      "Материалы доступны в разделе 'Материалы курса'. Также можете скачать их по этой ссылке: drive.fenix.edu/materials",
    type: "teacher",
    time: "16:15",
  },
  {
    id: 3,
    sectionId: 2,
    author: "Алексей Смирнов",
    role: "Студент",
    avatar: "👨‍🎓",
    title: "Вопрос по теме 1",
    content:
      "Не понимаю концепцию, объясненную на слайде 25. Можно более подробное объяснение?",
    type: "student",
    time: "10:45",
  },
  {
    id: 4,
    sectionId: 2,
    author: "Мария Петрова",
    role: "Преподаватель",
    avatar: "👩‍🏫",
    title: "",
    content:
      "Концепция на слайде 25 объясняет основной принцип работы системы. Рекомендую посмотреть дополнительное видео в материалах курса.",
    type: "teacher",
    time: "11:30",
  },
  {
    id: 5,
    sectionId: 3,
    author: "Елена Ковалева",
    role: "Студент",
    avatar: "👩‍🎓",
    title: "Практическое задание 2",
    content:
      "Сложность выполнения практического задания слишком высокая. Можно ли получить дополнительные инструкции?",
    type: "student",
    time: "14:20",
  },
  {
    id: 6,
    sectionId: 1,
    author: "Дмитрий Федоров",
    role: "Студент",
    avatar: "👨‍🎓",
    title: "Дедлайн по первому заданию",
    content: "Когда крайний срок сдачи первого задания?",
    type: "student",
    time: "09:15",
  },
  {
    id: 7,
    sectionId: 1,
    author: "Мария Петрова",
    role: "Преподаватель",
    avatar: "👩‍🏫",
    title: "",
    content:
      "Крайний срок сдачи первого задания - 15 апреля. Удачи в выполнении!",
    type: "teacher",
    time: "09:45",
  },
]);

// Фильтрованные сообщения
const filteredMessages = computed(() => {
  return messages.value.filter(
    (message) => message.sectionId === activeSection.value
  );
});

// Установка активного раздела
const setActiveSection = (sectionId) => {
  activeSection.value = sectionId;
};

// Получение названия активного раздела
const getActiveSectionName = () => {
  const section = sections.value.find((s) => s.id === activeSection.value);
  return section ? section.name : "Выберите раздел";
};

// Получение описания активного раздела
const getActiveSectionDescription = () => {
  const section = sections.value.find((s) => s.id === activeSection.value);
  return section ? section.description : "";
};

// Отправка вопроса
const submitQuestion = () => {
  if (newQuestion.value.trim()) {
    const newMessage = {
      id: messages.value.length + 1,
      sectionId: activeSection.value,
      author: "Вы",
      role: "Студент",
      avatar: "👤",
      title: "Новый вопрос",
      content: newQuestion.value,
      type: "student",
      time: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    messages.value.push(newMessage);
    newQuestion.value = "";

    // Автоответ преподавателя (демо)
    setTimeout(() => {
      const teacherResponse = {
        id: messages.value.length + 1,
        sectionId: activeSection.value,
        author: "Мария Петрова",
        role: "Преподаватель",
        avatar: "👩‍🏫",
        title: "",
        content:
          "Спасибо за ваш вопрос! Я постараюсь ответить на него в ближайшее время.",
        type: "teacher",
        time: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
      messages.value.push(teacherResponse);
    }, 2000);
  }
};

// Очистка вопроса
const clearQuestion = () => {
  newQuestion.value = "";
};

// Выход из системы
const handleLogout = () => {
  localStorage.removeItem("isAuthenticated");
  localStorage.removeItem("userData");
  router.push("/login");
};
</script>

