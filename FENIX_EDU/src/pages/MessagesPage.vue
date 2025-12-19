<template>
  <div class="messenger-page">
    <div class="main-grid" :class="{ 'with-info-panel': showTeacherInfo }">
      <aside class="contacts-panel">
        <div class="panel-header">
          <button class="back-btn" @click="goBack" title="Назад">
            <span class="back-icon">←</span>
          </button>
          <h2 class="panel-title">Контакты</h2>
        </div>

        <div class="search-container">
          <div class="search-box">
            <input
              type="text"
              placeholder="Поиск..."
              class="search-input"
              v-model="searchQuery"
            />
            <button class="search-btn">🔍</button>
          </div>
        </div>

        <div class="contacts-list">
          <div
            v-for="contact in filteredContacts"
            :key="contact.id"
            :class="['contact-item', { active: activeContact === contact.id }]"
            @click="selectContact(contact.id)"
          >
            <div class="contact-avatar">{{ contact.avatar }}</div>
            <div class="contact-info">
              <div class="contact-name">{{ contact.name }}</div>
              <div class="contact-role">{{ contact.role }}</div>
              <div class="contact-last-message">{{ contact.lastMessage }}</div>
            </div>
            <div class="contact-meta">
              <span class="contact-time">{{ contact.time }}</span>
              <span class="unread-badge" v-if="contact.unread">{{
                contact.unread
              }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- Основной чат -->
      <main class="chat-main">
        <div class="chat-header">
          <div class="teacher-info">
            <div class="teacher-avatar">{{ getCurrentContact()?.avatar }}</div>
            <div class="teacher-details">
              <div class="teacher-name">{{ getCurrentContact()?.name }}</div>
              <div class="teacher-status">
                <span class="status-indicator online"></span>
                <span class="status-text">В сети</span>
              </div>
            </div>
          </div>
          <div class="chat-actions">
            <button
              class="action-btn"
              title="Информация"
              @click="toggleTeacherInfo"
            >
              <span class="action-icon">ℹ️</span>
            </button>
          </div>
        </div>

        <!-- Сообщения -->
        <div class="messages-container" ref="messagesContainer">
          <div class="messages-wrapper">
            <div
              v-for="message in messages"
              :key="message.id"
              :class="['message', message.type]"
            >
              <div class="message-avatar" v-if="message.type === 'received'">
                {{ getCurrentContact()?.avatar }}
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-author">{{
                    message.type === "received"
                      ? getCurrentContact()?.name
                      : "Вы"
                  }}</span>
                  <span class="message-time">{{ message.time }}</span>
                </div>
                <div class="message-text">{{ message.text }}</div>
                <div class="message-status" v-if="message.type === 'sent'">
                  <span class="status-icon">✓✓</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Поле ввода сообщения -->
        <div class="message-input-container">
          <div class="input-wrapper">
            <button class="tool-btn attach-btn" title="Прикрепить файл">
              <span class="tool-icon">📎</span>
            </button>
            <textarea
              v-model="newMessage"
              placeholder="Введите сообщение..."
              class="message-input"
              @keydown.enter.exact.prevent="sendMessage"
              rows="1"
              ref="messageInput"
            ></textarea>
            <button
              class="send-btn"
              @click="sendMessage"
              :disabled="!newMessage.trim()"
            >
              <span class="send-icon">✈️</span>
            </button>
          </div>
        </div>
      </main>

      <!-- Правая боковая панель с информацией о преподавателе (скрыта по умолчанию) -->
      <aside class="teacher-info-panel" v-if="showTeacherInfo">
        <div class="panel-header">
          <h2 class="panel-title">Информация</h2>
          <button class="close-btn" @click="toggleTeacherInfo">
            <span class="close-icon">×</span>
          </button>
        </div>

        <div class="teacher-profile">
          <div class="profile-avatar">
            <div class="avatar-large">{{ getCurrentContact()?.avatar }}</div>
            <div class="profile-status">
              <span class="status-indicator online large"></span>
            </div>
          </div>
          <div class="profile-details">
            <h3 class="profile-name">{{ getCurrentContact()?.name }}</h3>
            <div class="profile-role">Преподаватель</div>
          </div>
        </div>

        <div class="info-sections">
          <div class="info-section">
            <h4 class="section-title">
              <span class="section-icon">📚</span>
              Дисциплины
            </h4>
            <div class="section-content">
              <div class="discipline-item">
                <div class="discipline-name">Веб-разработка</div>
              </div>
              <div class="discipline-item">
                <div class="discipline-name">Базы данных</div>
              </div>
              <div class="discipline-item">
                <div class="discipline-name">Алгоритмы</div>
              </div>
            </div>
          </div>

          <div class="info-section">
            <h4 class="section-title">
              <span class="section-icon">🕒</span>
              Расписание консультаций
            </h4>
            <div class="section-content">
              <div class="schedule-item">
                <div class="schedule-day">Понедельник</div>
                <div class="schedule-time">15:00 - 17:00</div>
              </div>
              <div class="schedule-item">
                <div class="schedule-day">Среда</div>
                <div class="schedule-time">14:00 - 16:00</div>
              </div>
              <div class="schedule-item">
                <div class="schedule-day">Пятница</div>
                <div class="schedule-time">10:00 - 12:00</div>
              </div>
            </div>
          </div>

          <div class="info-section">
            <h4 class="section-title">
              <span class="section-icon">📞</span>
              Контакты
            </h4>
            <div class="section-content">
              <div class="contact-info-item">
                <span class="contact-icon">📧</span>
                <span class="contact-text">teacher@fenixedu.ru</span>
              </div>
              <div class="contact-info-item">
                <span class="contact-icon">📱</span>
                <span class="contact-text">+7 (XXX) XXX-XX-XX</span>
              </div>
              <div class="contact-info-item">
                <span class="contact-icon">🏢</span>
                <span class="contact-text">Каб. 305, корпус А</span>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-footer">
          <button class="btn btn-schedule" @click="openSchedule">
            <span class="btn-icon">📅</span>
            <span class="btn-text">Записаться на консультацию</span>
          </button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const activeContact = ref(1);
const newMessage = ref("");
const messagesContainer = ref(null);
const messageInput = ref(null);
const showTeacherInfo = ref(false);
const searchQuery = ref("");

const contacts = ref([
  {
    id: 1,
    avatar: "👨‍🏫",
    name: "Преподаватель 1",
    role: "Доцент",
    lastMessage: "Добрый день! Как успехи с заданием?",
    time: "15:30",
    unread: 2,
  },
  {
    id: 2,
    avatar: "👩‍🏫",
    name: "Преподаватель 2",
    role: "Профессор",
    lastMessage: "Проверьте, пожалуйста, задание №3",
    time: "14:45",
    unread: 0,
  },
  {
    id: 3,
    avatar: "👨‍🏫",
    name: "Преподаватель 3",
    role: "Старший преподаватель",
    lastMessage: "Вопрос по лекции №5",
    time: "12:20",
    unread: 1,
  },
  {
    id: 4,
    avatar: "👨‍🎓",
    name: "Студент Иванов",
    role: "Одногруппник",
    lastMessage: "Привет! Поможешь с лабой?",
    time: "11:15",
    unread: 0,
  },
  {
    id: 5,
    avatar: "👩‍🎓",
    name: "Студент Петрова",
    role: "Одногруппница",
    lastMessage: "Спасибо за помощь!",
    time: "10:30",
    unread: 0,
  },
]);

const messages = ref([
  { id: 1, text: "Добрый день! Как дела?", type: "received", time: "15:25" },
  {
    id: 2,
    text: "Привет! Все хорошо, спасибо! А как у вас?",
    type: "sent",
    time: "15:26",
  },
  {
    id: 3,
    text: "Отлично! Есть вопросы по последней лекции?",
    type: "received",
    time: "15:28",
  },
  {
    id: 4,
    text: 'Да, есть вопрос по теме "Введение в Vue.js" - не совсем понял про компоненты',
    type: "sent",
    time: "15:29",
  },
  {
    id: 5,
    text: "Хорошо, объясню на следующем занятии. Если что-то срочное - пишите!",
    type: "received",
    time: "15:30",
  },
]);

const filteredContacts = computed(() => {
  if (!searchQuery.value.trim()) {
    return contacts.value;
  }

  const query = searchQuery.value.toLowerCase();
  return contacts.value.filter(
    (contact) =>
      contact.name.toLowerCase().includes(query) ||
      contact.role.toLowerCase().includes(query) ||
      contact.lastMessage.toLowerCase().includes(query)
  );
});

const getCurrentContact = () => {
  return contacts.value.find((c) => c.id === activeContact.value);
};

const selectContact = (contactId) => {
  activeContact.value = contactId;
  const contact = contacts.value.find((c) => c.id === contactId);
  if (contact) {
    contact.unread = 0;
  }
  scrollToBottom();
  if (showTeacherInfo.value) {
    showTeacherInfo.value = false;
  }
};

const sendMessage = () => {
  if (!newMessage.value.trim()) return;

  const newMsg = {
    id: messages.value.length + 1,
    text: newMessage.value,
    type: "sent",
    time: new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  };

  messages.value.push(newMsg);
  newMessage.value = "";

  setTimeout(() => {
    const responses = [
      "Спасибо за сообщение! Я отвечу вам в ближайшее время.",
      "Понял ваш вопрос. Давайте обсудим на следующей консультации.",
      "Интересный вопрос! Пришлите, пожалуйста, более подробное описание.",
      "Хорошо, я учту ваше замечание.",
      "Спасибо за обратную связь!",
    ];

    const randomResponse =
      responses[Math.floor(Math.random() * responses.length)];

    const teacherResponse = {
      id: messages.value.length + 1,
      text: randomResponse,
      type: "received",
      time: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    messages.value.push(teacherResponse);
    scrollToBottom();
  }, 1000);

  scrollToBottom();
  resizeTextarea();
};

const toggleTeacherInfo = () => {
  showTeacherInfo.value = !showTeacherInfo.value;
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

const resizeTextarea = () => {
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.style.height = "auto";
      messageInput.value.style.height =
        Math.min(messageInput.value.scrollHeight, 120) + "px";
    }
  });
};

const openSchedule = () => {
  alert(
    "Функция записи на консультацию будет доступна в следующем обновлении!"
  );
};

const goBack = () => {
  router.back();
};

onMounted(() => {
  scrollToBottom();
  if (messageInput.value) {
    messageInput.value.addEventListener("input", resizeTextarea);
  }
});
</script>
