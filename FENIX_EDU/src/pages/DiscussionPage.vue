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
            <button class="search-btn"></button>
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
    icon: "",
    description: "Основные понятия и введение в тему курса",
  },
  {
    id: 2,
    name: "Тема 1: Основные концепции",
    icon: "",
    description: "Изучение фундаментальных концепций предмета",
  },
  {
    id: 3,
    name: "Тема 2: Практические задания",
    icon: "",
    description: "Выполнение практических заданий и упражнений",
  },
  {
    id: 4,
    name: "Тема 3: Проектная работа",
    icon: "",
    description: "Работа над финальным проектом курса",
  },
  {
    id: 5,
    name: "FAQ и помощь",
    icon: "",
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

<style scoped>
.discussion-page {
  min-height: calc(100vh - 200px);
  padding: 2rem;
  background: #e7e7ec;
}

.discussion-container {
  max-width: 1600px;
  margin: 0 auto;
}

.discussion-section {
  background: #f6fbff;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  width: 100%;
}

.discussion-header {
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

.search-box {
  display: flex;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid #e7e7ec;
  transition: all 0.3s;
}

.search-box:focus-within {
  border-color: #2f4156;
}

.search-input {
  padding: 0.75rem 1rem;
  border: none;
  width: 300px;
  outline: none;
  background: transparent;
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
  padding: 0 1.5rem;
  cursor: pointer;
  transition: background 0.3s;
}

.search-btn:hover {
  background: #1a2530;
}

.discussion-content-wrapper {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
}

.sections-sidebar {
  background: #c8dae8;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  height: fit-content;
}

.sidebar-title {
  font-size: 1.25rem;
  color: #2f4156;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.sections-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.section-item:hover {
  background: white;
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.1);
}

.section-item.active {
  background: white;
  border-color: #2f4156;
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.15);
}

.section-icon {
  font-size: 1.25rem;
  width: 24px;
  text-align: center;
}

.section-text {
  font-size: 0.95rem;
  color: #2f4156;
  font-weight: 500;
  flex: 1;
}

.discussion-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.current-section {
  background: #c8dae8;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.current-section .section-title {
  font-size: 1.5rem;
  color: #2f4156;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.section-description {
  color: #4a5568;
  font-size: 0.95rem;
  line-height: 1.5;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.messages-list::-webkit-scrollbar {
  width: 6px;
}

.messages-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.messages-list::-webkit-scrollbar-thumb {
  background: #c8dae8;
  border-radius: 3px;
}

.messages-list::-webkit-scrollbar-thumb:hover {
  background: #a0b9d0;
}

.message {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  border-left: 4px solid transparent;
}

.message:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.message.student {
  border-left-color: #4299e1;
}

.message.teacher {
  border-left-color: #48bb78;
}

.message__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e7e7ec;
}

.message__author {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.author-avatar {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: #2f4156;
  margin-bottom: 0.25rem;
}

.author-role {
  font-size: 0.875rem;
  color: #718096;
}

.message__time {
  color: #a0aec0;
  font-size: 0.875rem;
}

.message__content h4 {
  color: #2f4156;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.message__content p {
  color: #4a5568;
  line-height: 1.6;
  font-size: 0.95rem;
}

.ask-question {
  background: #c8dae8;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.ask-title {
  font-size: 1.25rem;
  color: #2f4156;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.ask-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.question-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e7e7ec;
  border-radius: 12px;
  background: white;
  resize: vertical;
  font-family: inherit;
  font-size: 0.95rem;
  color: #2f4156;
  transition: all 0.3s;
  min-height: 120px;
}

.question-input:focus {
  outline: none;
  border-color: #2f4156;
  box-shadow: 0 0 0 3px rgba(47, 65, 86, 0.1);
}

.ask-actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  font-size: 0.95rem;
}

.btn--primary {
  background: #2f4156;
  color: white;
}

.btn--primary:hover {
  background: #1a2530;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.3);
}

.btn--secondary {
  background: white;
  color: #2f4156;
  border: 2px solid #2f4156;
}

.btn--secondary:hover {
  background: #f7fafc;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.1);
}

/* Адаптивность */
@media (max-width: 1200px) {
  .discussion-content-wrapper {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .sections-sidebar {
    order: 2;
  }
}

@media (max-width: 768px) {
  .discussion-page {
    padding: 1rem;
  }

  .discussion-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .search-box {
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .ask-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .discussion-content-wrapper {
    gap: 1rem;
  }

  .message__header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .message__time {
    align-self: flex-end;
  }
}
</style>
