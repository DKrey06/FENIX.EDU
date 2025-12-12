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

<style scoped>
.messenger-page {
  min-height: calc(100vh - 120px);
  padding: 2rem;
  background: #e7e7ec;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

.main-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  height: 85vh;
  min-height: 550px;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.main-grid.with-info-panel {
  grid-template-columns: 320px 1fr 320px;
}

.contacts-panel {
  background: #f5d6d8;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 8px 30px rgba(212, 185, 187, 0.3);
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(212, 185, 187, 0.4);
  position: relative;
  overflow: hidden;
}

.panel-header {
  margin-bottom: 1.25rem;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
}

.back-btn {
  width: 40px;
  height: 40px;
  background: white;
  border: 2px solid rgba(47, 65, 86, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #2f4156;
  line-height: 1;
  flex-shrink: 0;
}

.back-btn:hover {
  background: #2f4156;
  color: white;
  transform: translateX(-2px);
}

.panel-title {
  font-size: 1.6rem;
  color: #2f4156;
  font-weight: 700;
  margin: 0;
  flex: 1;
  text-align: center;
}

.search-container {
  margin-bottom: 1.25rem;
  width: 100%;
  flex-shrink: 0;
}

.search-box {
  display: flex;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid rgba(212, 185, 187, 0.4);
  width: 100%;
}

.search-input {
  flex: 1;
  padding: 0.875rem 1rem;
  border: none;
  outline: none;
  background: transparent;
  color: #2f4156;
  font-size: 0.95rem;
  width: 100%;
  min-width: 0;
}

.search-input::placeholder {
  color: #a0aec0;
}

.search-btn {
  background: #d3a5b1;
  color: #2f4156;
  border: none;
  padding: 0 1.5rem;
  cursor: pointer;
  transition: background 0.3s;
  flex-shrink: 0;
  width: 50px;
}

.search-btn:hover {
  background: #c895a3;
}

.contacts-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 0;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  gap: 1rem;
  border: 2px solid transparent;
  min-width: 0;
}

.contact-item:hover {
  background: white;
}

.contact-item.active {
  background: white;
  border-color: #2f4156;
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.15);
}

.contact-avatar {
  width: 52px;
  height: 52px;
  background: #d3a5b1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  flex-shrink: 0;
}

.contact-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.contact-name {
  font-weight: 600;
  color: #2f4156;
  margin-bottom: 0.25rem;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.contact-role {
  font-size: 0.8rem;
  color: #667eea;
  margin-bottom: 0.25rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.contact-last-message {
  font-size: 0.85rem;
  color: #718096;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.contact-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  flex-shrink: 0;
}

.contact-time {
  font-size: 0.75rem;
  color: #a0aec0;
  white-space: nowrap;
}

.unread-badge {
  background: #2f4156;
  color: white;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  font-weight: 600;
  min-width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.chat-main {
  background: #f6fbff;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 30px rgba(200, 218, 232, 0.3);
  border: 1px solid rgba(200, 218, 232, 0.4);
  overflow: hidden;
  position: relative;
  min-height: 0;
}

.chat-header {
  background: #daefff;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(200, 218, 232, 0.4);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.teacher-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.teacher-avatar {
  width: 54px;
  height: 54px;
  background: #2f4156;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  flex-shrink: 0;
}

.teacher-details {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.teacher-name {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2f4156;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.teacher-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator {
  width: 10px;
  height: 10px;
  background: #48bb78;
  border-radius: 50%;
}

.status-text {
  font-size: 0.9rem;
  color: #4a5568;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.action-btn {
  width: 44px;
  height: 44px;
  background: white;
  border: 2px solid rgba(47, 65, 86, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.action-btn:hover {
  background: #2f4156;
  color: white;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 1.2rem;
}

.messages-container {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  background: #f6fbff;
  min-height: 0;
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  max-width: 80%;
  gap: 1rem;
}

.message.received {
  align-self: flex-start;
}

.message.sent {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  background: #2f4156;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.message.sent .message-avatar {
  display: none;
}

.message-content {
  background: white;
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
  min-width: 160px;
  max-width: 100%;
}

.message.received .message-content {
  border-bottom-left-radius: 4px;
}

.message.sent .message-content {
  background: #2f4156;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(47, 65, 86, 0.1);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.message.sent .message-header {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.message-author {
  font-weight: 600;
  font-size: 0.95rem;
  color: #2f4156;
  white-space: nowrap;
}

.message.sent .message-author {
  color: white;
}

.message-time {
  font-size: 0.8rem;
  color: #a0aec0;
  white-space: nowrap;
}

.message.sent .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.message-text {
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
  word-break: break-word;
}

.message-status {
  text-align: right;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

.message-input-container {
  padding: 1.25rem 1.5rem;
  background: white;
  border-top: 1px solid rgba(200, 218, 232, 0.4);
  flex-shrink: 0;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.attach-btn {
  width: 50px;
  height: 50px;
  background: rgba(47, 65, 86, 0.05);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  align-self: flex-end;
  margin-bottom: 2px;
}

.attach-btn:hover {
  background: rgba(47, 65, 86, 0.1);
  transform: translateY(-2px);
}

.tool-icon {
  font-size: 1.1rem;
}

.message-input {
  flex: 1;
  padding: 0.875rem 1rem;
  border: 2px solid #e7e7ec;
  border-radius: 12px;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
  color: #2f4156;
  background: white;
  outline: none;
  max-height: 120px;
  line-height: 1.5;
  min-height: 50px;
  min-width: 0;
}

.message-input:focus {
  border-color: #2f4156;
}

.send-btn {
  width: 52px;
  height: 52px;
  background: #2f4156;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  align-self: flex-end;
  margin-bottom: 2px;
}

.send-btn:hover:not(:disabled) {
  background: #1a2530;
  transform: translateY(-2px);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-icon {
  font-size: 1.3rem;
  transform: rotate(45deg);
}

.teacher-info-panel {
  background: #f5d6d8;
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 8px 30px rgba(212, 185, 187, 0.3);
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(212, 185, 187, 0.4);
  position: relative;
  overflow: hidden;
  height: 85vh;
  min-height: 550px;
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-shrink: 0;
}

.close-btn {
  width: 40px;
  height: 40px;
  background: white;
  border: 2px solid rgba(47, 65, 86, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #2f4156;
  line-height: 1;
  flex-shrink: 0;
}

.close-btn:hover {
  background: #2f4156;
  color: white;
  transform: rotate(90deg);
}

.teacher-profile {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(212, 185, 187, 0.4);
  flex-shrink: 0;
}

.profile-avatar {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
}

.avatar-large {
  width: 90px;
  height: 90px;
  background: #d3a5b1;
  color: #2f4156;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.8rem;
  margin: 0 auto;
}

.profile-status {
  position: absolute;
  bottom: 5px;
  right: 5px;
}

.profile-details {
  text-align: center;
}

.profile-name {
  font-size: 1.6rem;
  color: #2f4156;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.profile-role {
  font-size: 1.1rem;
  color: #667eea;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.info-sections {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  min-height: 0;
}

.info-section {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 1.25rem;
}

.section-title {
  font-size: 1.1rem;
  color: #2f4156;
  font-weight: 600;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-icon {
  font-size: 1.2rem;
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.discipline-item,
.schedule-item,
.contact-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 10px;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.discipline-item {
  justify-content: flex-start;
}

.discipline-name {
  font-weight: 500;
  color: #2f4156;
  font-size: 1rem;
}

.schedule-day {
  font-weight: 500;
  color: #2f4156;
  font-size: 1rem;
}

.schedule-time {
  font-size: 0.9rem;
  color: #667eea;
  font-weight: 600;
}

.contact-info-item {
  justify-content: flex-start;
  gap: 0.75rem;
}

.contact-icon {
  font-size: 1.1rem;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.contact-text {
  font-size: 0.95rem;
  color: #2f4156;
}

.panel-footer {
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(212, 185, 187, 0.4);
  flex-shrink: 0;
}

.btn-schedule {
  width: 100%;
  padding: 1rem;
  background: #2f4156;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.btn-schedule:hover {
  background: #1a2530;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.3);
}

.btn-icon {
  font-size: 1.2rem;
}

.btn-text {
  font-size: 1rem;
}

/* Адаптивность */
@media (max-width: 1400px) {
  .main-grid {
    grid-template-columns: 300px 1fr;
  }

  .main-grid.with-info-panel {
    grid-template-columns: 300px 1fr 300px;
  }
}

@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 280px 1fr;
    height: 80vh;
  }

  .main-grid.with-info-panel {
    grid-template-columns: 280px 1fr 280px;
  }
}

@media (max-width: 1100px) {
  .main-grid.with-info-panel {
    grid-template-columns: 280px 1fr;
  }

  .teacher-info-panel {
    position: fixed;
    top: 50%;
    right: 2rem;
    transform: translateY(-50%);
    width: 350px;
    max-width: calc(100% - 4rem);
    max-height: 85vh;
    z-index: 1000;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  }
}

@media (max-width: 768px) {
  .messenger-page {
    padding: 1rem;
    min-height: calc(100vh - 100px);
  }

  .main-grid {
    grid-template-columns: 1fr;
    height: calc(100vh - 150px);
    min-height: 500px;
  }

  .contacts-panel {
    display: none;
  }

  .chat-header {
    padding: 1rem;
  }

  .messages-container {
    padding: 1rem;
  }

  .message-input-container {
    padding: 1rem;
  }

  .message {
    max-width: 90%;
  }

  .teacher-info-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 95%;
    max-width: 500px;
    max-height: 90vh;
    z-index: 1000;
  }

  .main-grid.with-info-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .teacher-name {
    font-size: 1.2rem;
  }

  .message-content {
    padding: 0.875rem;
  }

  .message-text {
    font-size: 0.95rem;
  }

  .input-wrapper {
    gap: 0.5rem;
  }

  .attach-btn {
    width: 46px;
    height: 46px;
  }

  .send-btn {
    width: 46px;
    height: 46px;
  }

  .search-box {
    width: 100%;
  }

  .search-input {
    width: calc(100% - 50px);
  }
}
</style>
