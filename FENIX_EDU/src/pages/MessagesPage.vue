<template>
  <div class="messenger-container">
    <div class="messenger-grid">
      <!-- Боковая панель с диалогами -->
      <aside class="threads-panel">
        <div class="panel-header">
          <h2 class="panel-title">Сообщения</h2>
          <button class="new-chat-btn" @click="showNewChat = !showNewChat">
            <span class="btn-icon">+</span>
            <span class="btn-text">Новый чат</span>
          </button>
        </div>

        <!-- Поиск -->
        <div class="search-container">
          <div class="search-box">
            <input type="text" placeholder="Поиск диалогов..." class="search-input" v-model="searchQuery" />
            <button class="search-btn">🔍</button>
          </div>
        </div>

        <!-- Список преподавателей для нового чата -->
        <div class="new-chat-panel" v-if="showNewChat">
          <div class="new-chat-header">
            <h3 class="new-chat-title">Выберите преподавателя</h3>
            <button class="close-btn" @click="showNewChat = false">×</button>
          </div>
          <div class="teachers-search">
            <input type="text" placeholder="Поиск преподавателей..." class="teachers-search-input"
              v-model="teacherSearch" @input="searchTeachers" />
          </div>
          <div class="teachers-list">
            <div v-for="teacher in filteredTeachers" :key="teacher.id" class="teacher-item"
              @click="startNewChat(teacher)">
              <div class="teacher-avatar">{{ getAvatarInitials(teacher.full_name) }}</div>
              <div class="teacher-info">
                <div class="teacher-name">{{ teacher.full_name }}</div>
                <div class="teacher-role">{{ formatRole(teacher.role) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Список диалогов -->
        <div class="threads-list">
          <div v-for="thread in filteredThreads" :key="thread.id"
            :class="['thread-item', { active: activeThread?.id === thread.id, unread: thread.unread_count > 0 }]"
            @click="selectThread(thread)">
            <div class="thread-avatar">{{ thread.teacher_avatar }}</div>
            <div class="thread-info">
              <div class="thread-name">{{ thread.teacher_name }}</div>
              <div class="thread-preview" v-if="thread.last_message">
                {{ thread.last_message.content }}
              </div>
            </div>
            <div class="thread-meta">
              <span class="thread-time">{{ formatTime(thread.last_message_at) }}</span>
              <span class="unread-badge" v-if="thread.unread_count > 0">
                {{ thread.unread_count }}
              </span>
            </div>
          </div>

          <div class="empty-state" v-if="threads.length === 0">
            <div class="empty-icon">💬</div>
            <div class="empty-text">Нет активных диалогов</div>
            <button class="empty-btn" @click="showNewChat = true">
              Начать общение
            </button>
          </div>
        </div>
      </aside>

      <!-- Основная область чата -->
      <main class="chat-area" v-if="activeThread">
        <div class="chat-header">
          <div class="chat-partner">
            <div class="partner-avatar">{{ activeThread.partner_avatar }}</div>
            <div class="partner-info">
              <div class="partner-name">{{ activeThread.partner_name }}</div>
              <div class="partner-status">
                <span class="status-indicator" :class="getStatusClass(activeThread)"></span>
                <span class="status-text">{{ getStatusText(activeThread) }}</span>
              </div>
            </div>
          </div>
          <div class="chat-actions">
            <button class="action-btn" title="Архивировать" @click="archiveCurrentThread">
              <span class="action-icon">📁</span>
            </button>
          </div>
        </div>

        <!-- Сообщения -->
        <!-- Сообщения -->
        <div class="messages-area" ref="messagesContainer">
          <div class="messages-list">
            <div v-for="message in messages" :key="message.id"
              :class="['message', message.sender_id === authStore.user?.id ? 'sent' : 'received']">
              <div class="message-avatar" v-if="message.sender_id !== authStore.user?.id">
                {{ getAvatarInitials(message.sender_name) }}
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-author">{{ message.sender_name }}</span>
                  <span class="message-time">{{ formatMessageTime(message.created_at) }}</span>
                </div>
                <div class="message-text">{{ message.content }}</div>
                <div class="message-status" v-if="message.sender_id === authStore.user?.id">
                  <span class="status-icon" :class="{ read: message.is_read }">✓✓</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Поле ввода -->
        <div class="message-input-area">
          <div class="input-wrapper">
            <textarea v-model="newMessage" placeholder="Введите сообщение..." class="message-input"
              @keydown.enter.exact.prevent="sendMessage" rows="1" ref="messageInput"></textarea>
            <button class="send-btn" @click="sendMessage" :disabled="!newMessage.trim()">
              <span class="send-icon">✈️</span>
            </button>
          </div>
        </div>
      </main>

      <!-- Состояние без выбранного диалога -->
      <main class="chat-area empty-chat" v-else>
        <div class="empty-chat-content">
          <div class="empty-chat-icon">💬</div>
          <div class="empty-chat-title">Выберите диалог</div>
          <div class="empty-chat-text">
            Выберите диалог из списка или начните новый разговор с преподавателем
          </div>
          <button class="empty-chat-btn" @click="showNewChat = true">
            Начать новый чат
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useMessengerStore } from '@/stores/messenger'
import { useAuthStore } from '@/stores/auth'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

const messengerStore = useMessengerStore()
const authStore = useAuthStore()

// Реактивные переменные
const activeThread = ref(null)
const newMessage = ref('')
const showNewChat = ref(false)
const searchQuery = ref('')
const teacherSearch = ref('')
const teachers = ref([])
const messagesContainer = ref(null)
const messageInput = ref(null)

// Загрузка данных при монтировании
onMounted(async () => {
  await loadThreads()
  await loadTeachers()

  if (route.query.thread) {
    const threadId = parseInt(route.query.thread);
    const thread = messengerStore.threads.find(t => t.id === threadId);
    if (thread) {
      await selectThread(thread);
    }
  }
})

// Загрузка диалогов
const loadThreads = async () => {
  try {
    await messengerStore.fetchThreads()
  } catch (error) {
    console.error('Ошибка загрузки диалогов:', error)
  }
}

// Загрузка преподавателей
const loadTeachers = async () => {
  try {
    const response = await messengerStore.fetchTeachers()
    teachers.value = response.teachers || []
  } catch (error) {
    console.error('Ошибка загрузки преподавателей:', error)
  }
}

// Поиск преподавателей
const searchTeachers = async () => {
  try {
    const response = await messengerStore.fetchTeachers(teacherSearch.value)
    teachers.value = response.teachers || []
  } catch (error) {
    console.error('Ошибка поиска преподавателей:', error)
  }
}

// Отфильтрованные диалоги
const filteredThreads = computed(() => {
  if (!searchQuery.value.trim()) {
    return messengerStore.threads
  }

  const query = searchQuery.value.toLowerCase()
  return messengerStore.threads.filter(thread =>
    thread.teacher_name.toLowerCase().includes(query) ||
    (thread.last_message?.content || '').toLowerCase().includes(query)
  )
})

// Отфильтрованные преподаватели
const filteredTeachers = computed(() => {
  return teachers.value.filter(teacher =>
    teacher.id !== authStore.user?.id
  )
})

// Выбор диалога
const selectThread = async (thread) => {
  // Используем partner_name и partner_avatar для отображения в заголовке
  activeThread.value = {
    id: thread.id,
    teacher_id: thread.teacher_id,
    teacher_name: thread.partner_name || thread.teacher_name,
    teacher_avatar: thread.partner_avatar || thread.teacher_avatar || getAvatarInitials(thread.partner_name || thread.teacher_name),
    partner_name: thread.partner_name || thread.teacher_name,
    partner_id: thread.partner_id || thread.teacher_id
  };

  await messengerStore.fetchThreadMessages(thread.id);
  await messengerStore.markAsRead(thread.id);
  scrollToBottom();
};

// Начать новый чат
const startNewChat = async (teacher) => {
  showNewChat.value = false
  teacherSearch.value = ''

  // Ищем существующий диалог
  const existingThread = messengerStore.threads.find(
    t => t.teacher_id === teacher.id
  )

  if (existingThread) {
    await selectThread(existingThread)
  } else {
    // Создаем новый диалог
    newMessage.value = `Здравствуйте! Меня зовут ${authStore.user?.full_name}. `
    activeThread.value = {
      id: null,
      teacher_id: teacher.id,
      teacher_name: teacher.full_name,
      teacher_avatar: getAvatarInitials(teacher.full_name)
    }

    nextTick(() => {
      messageInput.value?.focus()
    })
  }
}

// Отправить сообщение
const sendMessage = async () => {
  if (!newMessage.value.trim()) return

  try {
    if (activeThread.value.id) {
      // Отправляем ответ в существующий диалог
      await messengerStore.sendReply(activeThread.value.id, newMessage.value)
    } else {
      // Создаем новый диалог
      const message = await messengerStore.sendMessage(
        activeThread.value.teacher_id,
        newMessage.value
      )

      // Обновляем активный диалог
      activeThread.value = {
        ...activeThread.value,
        id: message.thread_id
      }

      // Перезагружаем список диалогов
      await loadThreads()
    }

    newMessage.value = ''
    scrollToBottom()
  } catch (error) {
    console.error('Ошибка отправки сообщения:', error)
  }
}

// Архивировать текущий диалог
const archiveCurrentThread = async () => {
  if (activeThread.value?.id) {
    await messengerStore.archiveThread(activeThread.value.id)
    activeThread.value = null
    await loadThreads()
  }
}

// Вспомогательные функции
const getAvatarInitials = (name) => {
  if (!name) return '👤'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase()
}

const formatRole = (role) => {
  const roles = {
    student: 'Студент',
    teacher: 'Преподаватель',
    department_head: 'Зав. кафедрой',
    admin: 'Администратор'
  }
  return roles[role] || role
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()

  if (date.toDateString() === now.toDateString()) {
    return format(date, 'HH:mm')
  }

  if (date.getFullYear() === now.getFullYear()) {
    return format(date, 'd MMM', { locale: ru })
  }

  return format(date, 'dd.MM.yy')
}

const formatMessageTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return format(date, 'HH:mm')
}

const getStatusClass = (thread) => {
  // Здесь можно добавить логику определения статуса онлайн/офлайн
  return 'online'
}

const getStatusText = (thread) => {
  return 'В сети'
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Компьютед-переменные для доступа к данным хранилища
const messages = computed(() => messengerStore.messages)
const threads = computed(() => messengerStore.threads)

// Наблюдаем за изменениями в сообщениях
watch(() => messengerStore.messages, () => {
  scrollToBottom()
}, { deep: true })
</script>


<style scoped>
.messenger-container {
  height: calc(100vh - 120px);
  padding: 2rem;
  background: #e7e7ec;
}

.messenger-grid {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 1.5rem;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.threads-panel {
  background: #f5d6d8;
  border-radius: 20px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(212, 185, 187, 0.4);
  box-shadow: 0 8px 30px rgba(212, 185, 187, 0.3);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.panel-title {
  font-size: 1.5rem;
  color: #2f4156;
  font-weight: 700;
  margin: 0;
}

.new-chat-btn {
  background: #2f4156;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  transition: all 0.3s;
}

.new-chat-btn:hover {
  background: #1a2530;
  transform: translateY(-2px);
}

.search-container {
  margin-bottom: 1.5rem;
}

.search-box {
  display: flex;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid rgba(212, 185, 187, 0.4);
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.95rem;
}

.search-btn {
  background: #d3a5b1;
  color: #2f4156;
  border: none;
  padding: 0 1rem;
  cursor: pointer;
}

.new-chat-panel {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border: 2px solid #2f4156;
}

.new-chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.new-chat-title {
  font-size: 1.1rem;
  color: #2f4156;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #2f4156;
}

.teachers-search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e7e7ec;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.95rem;
}

.teachers-list {
  max-height: 200px;
  overflow-y: auto;
}

.teacher-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
  gap: 0.75rem;
}

.teacher-item:hover {
  background: #f5d6d8;
}

.teacher-avatar {
  width: 40px;
  height: 40px;
  background: #d3a5b1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.teacher-info {
  flex: 1;
  min-width: 0;
}

.teacher-name {
  font-weight: 600;
  color: #2f4156;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.teacher-role {
  font-size: 0.85rem;
  color: #667eea;
}

.threads-list {
  flex: 1;
  overflow-y: auto;
}

.thread-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.3s;
  gap: 1rem;
  border: 2px solid transparent;
}

.thread-item:hover {
  background: white;
  transform: translateX(5px);
}

.thread-item.active {
  background: white;
  border-color: #2f4156;
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.15);
}

.thread-item.unread {
  background: rgba(47, 65, 86, 0.05);
}

.thread-avatar {
  width: 50px;
  height: 50px;
  background: #2f4156;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.thread-info {
  flex: 1;
  min-width: 0;
}

.thread-name {
  font-weight: 600;
  color: #2f4156;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.thread-preview {
  font-size: 0.9rem;
  color: #718096;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.thread-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  flex-shrink: 0;
}

.thread-time {
  font-size: 0.8rem;
  color: #a0aec0;
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
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-text {
  color: #718096;
  margin-bottom: 1.5rem;
}

.empty-btn {
  background: #2f4156;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.empty-btn:hover {
  background: #1a2530;
  transform: translateY(-2px);
}

.chat-area {
  background: white;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(200, 218, 232, 0.4);
  box-shadow: 0 8px 30px rgba(200, 218, 232, 0.3);
  overflow: hidden;
}

.chat-area.empty-chat {
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-chat-content {
  text-align: center;
  padding: 3rem;
}

.empty-chat-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.empty-chat-title {
  font-size: 1.5rem;
  color: #2f4156;
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.empty-chat-text {
  color: #718096;
  margin-bottom: 2rem;
  max-width: 300px;
}

.empty-chat-btn {
  background: #2f4156;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.empty-chat-btn:hover {
  background: #1a2530;
  transform: translateY(-2px);
}

.chat-header {
  background: #daefff;
  padding: 1.25rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(200, 218, 232, 0.4);
}

.chat-partner {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.partner-avatar {
  width: 50px;
  height: 50px;
  background: #2f4156;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.partner-info {
  display: flex;
  flex-direction: column;
}

.partner-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2f4156;
  margin-bottom: 0.25rem;
}

.partner-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-indicator.online {
  background: #48bb78;
}

.status-text {
  font-size: 0.9rem;
  color: #4a5568;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 40px;
  height: 40px;
  background: white;
  border: 2px solid rgba(47, 65, 86, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: #2f4156;
  color: white;
}

.messages-area {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  background: #f6fbff;
}

.messages-list {
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
  width: 36px;
  height: 36px;
  background: #2f4156;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  flex-shrink: 0;
}

.message.sent .message-avatar {
  display: none;
}

.message-content {
  background: white;
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message.sent .message-content {
  background: #2f4156;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.received .message-content {
  border-bottom-left-radius: 4px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(47, 65, 86, 0.1);
}

.message.sent .message-header {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.message-author {
  font-weight: 600;
  font-size: 0.9rem;
}

.message.sent .message-author {
  color: white;
}

.message-time {
  font-size: 0.8rem;
  color: #a0aec0;
}

.message.sent .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.message-text {
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
  word-break: break-word;
}

.message-status {
  text-align: right;
}

.status-icon {
  font-size: 0.85rem;
  opacity: 0.6;
}

.status-icon.read {
  color: #48bb78;
  opacity: 1;
}

.message-input-area {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid rgba(200, 218, 232, 0.4);
  background: white;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 0.875rem 1rem;
  border: 2px solid #e7e7ec;
  border-radius: 12px;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
  min-height: 50px;
  max-height: 120px;
  line-height: 1.5;
  outline: none;
}

.message-input:focus {
  border-color: #2f4156;
}

.send-btn {
  width: 50px;
  height: 50px;
  background: #2f4156;
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: flex-end;
  margin-bottom: 2px;
}

.send-btn:hover:not(:disabled) {
  background: #1a2530;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}


@media (max-width: 1024px) {
  .messenger-grid {
    grid-template-columns: 300px 1fr;
  }
}

@media (max-width: 768px) {
  .messenger-container {
    padding: 1rem;
    height: calc(100vh - 100px);
  }

  .messenger-grid {
    grid-template-columns: 1fr;
  }

  .threads-panel {
    display: none;
  }

  .chat-area.empty-chat .empty-chat-content {
    padding: 2rem;
  }
}

@media (max-width: 480px) {
  .chat-header {
    padding: 1rem;
  }

  .messages-area {
    padding: 1rem;
  }

  .message-input-area {
    padding: 1rem;
  }

  .message {
    max-width: 90%;
  }
}
</style>