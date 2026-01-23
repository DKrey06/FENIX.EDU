<template>
  <div class="discussion-page">
    <div class="discussion-container">
      <div class="discussion-section">
        <div class="discussion-header">
          <div class="header-left">
            <router-link to="/" class="back-to-main">
              <span class="back-icon">←</span>
              На главную
            </router-link>
            <h2 class="content-title">Обсуждения</h2>
          </div>

          <div class="search-box">
            <input
              v-model="search"
              type="text"
              placeholder="Поиск по подразделам..."
              class="search-input"
            />
            <button class="search-btn"></button>
          </div>
        </div>

        <div class="discussion-content-wrapper">
          <div class="courses-sidebar">
            <div class="sidebar-header">
              <h3 class="sidebar-title">Курсы</h3>
            </div>

            <div v-if="loadingCourses" class="hint">Загрузка курсов...</div>
            <div v-else-if="visibleCourses.length === 0" class="hint">
              Курсы не найдены
            </div>

            <div v-else class="courses-list">
              <div
                v-for="c in visibleCourses"
                :key="c.id"
                class="course-item"
                :class="{ active: activeCourseId === c.id }"
                @click="selectCourse(c.id)"
              >
                <div class="course-title">{{ c.name }}</div>
                <div class="course-desc" v-if="c.description">
                  {{ c.description }}
                </div>
              </div>
            </div>
          </div>

          <div class="sections-sidebar">
            <div class="sidebar-header">
              <h3 class="sidebar-title">Разделы курса</h3>
            </div>

            <div v-if="loadingStructure" class="hint">
              Загрузка структуры...
            </div>
            <div v-else-if="sections.length === 0" class="hint">
              В курсе пока нет структуры
            </div>

            <div v-else class="sections-tree">
              <div
                v-for="sec in filteredSections"
                :key="sec._key"
                class="sec-block"
              >
                <div class="sec-title">
                  <span class="sec-number">Раздел {{ sec.number }}.</span>
                  <span>{{ sec.title }}</span>
                </div>

                <div class="subsections-list">
                  <div
                    v-for="sub in sec.subsections"
                    :key="sub._key"
                    class="section-item"
                    :class="{ active: activeSubsectionId === sub.id }"
                    @click="selectSubsection(sub.id)"
                  >
                    <span class="section-icon">{{ sub.icon || " " }}</span>
                    <span class="section-text">{{ sub.title }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="discussion-content">
            <div class="current-section" v-if="activeSubsection">
              <h3 class="section-title">{{ activeSubsection.title }}</h3>

              <div class="files" v-if="activeSubsection.files?.length">
                <h4 class="files-title">Файлы</h4>
                <div
                  class="file-item"
                  v-for="f in activeSubsection.files"
                  :key="f.id || f.url || f.name"
                >
                  <a
                    class="file-link"
                    :href="apiBase + (f.url || '')"
                    target="_blank"
                    rel="noreferrer"
                  >
                    {{ f.name }}
                  </a>
                  <span class="file-size" v-if="typeof f.size === 'number'">
                    {{ formatBytes(f.size) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="current-section" v-else>
              <h3 class="section-title">Выберите подраздел</h3>
              <p class="section-description">
                Сначала выберите курс, затем подраздел — и откроются обсуждения.
              </p>
            </div>

            <div class="messages-list" v-if="activeSubsectionId">
              <div v-if="loadingComments" class="hint">
                Загрузка комментариев...
              </div>

              <div v-else-if="comments.length === 0" class="hint">
                Комментариев пока нет — можно начать обсуждение.
              </div>

              <div v-else>
                <!-- Основное сообщение -->
                <div v-for="c in comments" :key="c.id" class="message-block">
                  <div
                    class="message"
                    :class="c.author_role === 'teacher' ? 'teacher' : 'student'"
                  >
                    <div class="message__header">
                      <div class="message__author">
                        <div class="author-info">
                          <span class="author-name">{{ c.author_name }}</span>
                          <span class="author-role">{{
                            roleLabel(c.author_role)
                          }}</span>
                        </div>
                      </div>
                      <span class="message__time">{{
                        formatDateTime(c.created_at)
                      }}</span>
                    </div>

                    <div class="message__content">
                      <p>{{ c.content }}</p>
                    </div>

                    <div v-if="isAuthenticated" class="reply-form">
                      <div
                        v-if="!isReplyOpen(c.id)"
                        class="reply-toggle"
                        @click="openReply(c.id)"
                      >
                        Ответить
                      </div>

                      <div v-else>
                        <textarea
                          v-model="replyDraft[c.id]"
                          placeholder="Введите ответ..."
                          class="question-input"
                          rows="3"
                        ></textarea>

                        <div class="ask-actions">
                          <button
                            class="btn btn--primary"
                            @click="sendReply(c.id)"
                          >
                            Отправить
                          </button>
                          <button
                            class="btn btn--secondary"
                            @click="closeReply(c.id)"
                          >
                            Отмена
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Ответы на основное сообщение -->
                  <div
                    v-if="Array.isArray(c.replies) && c.replies.length"
                    class="replies-container"
                  >
                    <div
                      v-for="r in c.replies"
                      :key="r.id"
                      class="reply-wrapper"
                    >
                      <div
                        class="message reply"
                        :class="
                          r.author_role === 'teacher' ? 'teacher' : 'student'
                        "
                      >
                        <div class="message__header">
                          <div class="message__author">
                            <div class="author-info">
                              <span class="author-name">{{
                                r.author_name
                              }}</span>
                              <span class="author-role">{{
                                roleLabel(r.author_role)
                              }}</span>
                            </div>
                          </div>
                          <span class="message__time">{{
                            formatDateTime(r.created_at)
                          }}</span>
                        </div>

                        <div class="message__content">
                          <p>{{ r.content }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div
              class="ask-question"
              v-if="activeSubsectionId && isAuthenticated"
            >
              <h3 class="ask-title">Написать комментарий</h3>
              <div class="ask-form">
                <textarea
                  v-model="newQuestion"
                  placeholder="Введите комментарий..."
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

            <div class="hint" v-if="activeSubsectionId && !isAuthenticated">
              Для участия в обсуждении требуется авторизация
            </div>

            <div class="error" v-if="errorText">
              {{ errorText }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const apiBase = (
  import.meta?.env?.VITE_API_BASE || "http://localhost:8000"
).replace(/\/$/, "");

const courses = ref([]);
const sections = ref([]);
const activeCourseId = ref(null);
const activeSubsectionId = ref(null);

const comments = ref([]);
const replyDraft = ref({});
const replyOpen = ref({});
const newQuestion = ref("");

const search = ref("");

const loadingCourses = ref(false);
const loadingStructure = ref(false);
const loadingComments = ref(false);
const errorText = ref("");

function isReplyOpen(commentId) {
  return !!replyOpen.value[commentId];
}
function openReply(commentId) {
  replyOpen.value = { ...replyOpen.value, [commentId]: true };
}
function closeReply(commentId) {
  replyDraft.value[commentId] = "";
  const next = { ...replyOpen.value };
  delete next[commentId];
  replyOpen.value = next;
}

function getToken() {
  const t1 = localStorage.getItem("access_token");
  if (t1) return t1;

  const userData = localStorage.getItem("userData");
  if (userData) {
    try {
      const parsed = JSON.parse(userData);
      return parsed?.access_token || parsed?.token || null;
    } catch {
      return null;
    }
  }
  return null;
}

function getUser() {
  const userData = localStorage.getItem("userData");
  if (!userData) return null;
  try {
    return JSON.parse(userData);
  } catch {
    return null;
  }
}

const isAuthenticated = computed(() => !!getToken());
const user = computed(() => getUser());

function roleLabel(role) {
  switch (role) {
    case "student":
      return "Студент";
    case "teacher":
      return "Преподаватель";
    case "admin":
      return "Администратор";
    case "department_head":
      return "Зав. кафедрой";
    default:
      return role || "";
  }
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function formatDateTime(dt) {
  try {
    const d = new Date(dt);
    return d.toLocaleString([], {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  const mb = kb / 1024;
  return `${mb.toFixed(1)} MB`;
}

async function apiGet(path) {
  const res = await fetch(`${apiBase}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `GET ${path} failed`);
  }

  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${apiBase}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `POST ${path} failed`);
  }

  return res.json();
}

const requestedCourseId = computed(() => {
  const v = route.query.course_id;
  return v != null ? String(v) : null;
});

const visibleCourses = computed(() => courses.value || []);

const activeSubsection = computed(() => {
  if (!activeSubsectionId.value) return null;
  for (const sec of sections.value) {
    const found = (sec.subsections || []).find(
      (s) => s.id === activeSubsectionId.value,
    );
    if (found) return found;
  }
  return null;
});

const filteredSections = computed(() => {
  const q = (search.value || "").trim().toLowerCase();

  const normalized = (sections.value || []).map((sec, i) => ({
    ...sec,
    _key: sec.id ?? `${sec.number}-${i}`,
    subsections: (sec.subsections || []).map((s, j) => ({
      ...s,
      _key: s.id ?? `sub-${i}-${j}`,
    })),
  }));

  if (!q) return normalized;

  return normalized
    .map((sec) => {
      const subs = sec.subsections.filter((s) =>
        (s.title || "").toLowerCase().includes(q),
      );
      return { ...sec, subsections: subs };
    })
    .filter((sec) => sec.subsections.length > 0);
});

async function loadCourses() {
  errorText.value = "";
  loadingCourses.value = true;

  try {
    const list = await apiGet("/api/courses");
    courses.value = Array.isArray(list) ? list : [];

    if (!activeCourseId.value && courses.value.length > 0) {
      const wanted = requestedCourseId.value;

      if (wanted) {
        const found = courses.value.find((c) => String(c.id) === wanted);
        if (found) {
          await selectCourse(found.id);
          return;
        }
      }

      await selectCourse(courses.value[0].id);
    }
  } catch (e) {
    errorText.value =
      "Не удалось загрузить курсы. Проверь авторизацию и доступ к API.";
    console.error(e);
  } finally {
    loadingCourses.value = false;
  }
}

async function loadStructure(courseId) {
  errorText.value = "";
  loadingStructure.value = true;

  try {
    const structure = await apiGet(`/api/courses/${courseId}/structure`);
    sections.value = structure?.sections || [];

    const firstSub = sections.value?.[0]?.subsections?.[0];
    activeSubsectionId.value = firstSub?.id ?? null;

    comments.value = [];
    replyDraft.value = {};
    replyOpen.value = {};
    newQuestion.value = "";

    if (activeSubsectionId.value) {
      await loadComments();
    }
  } catch (e) {
    errorText.value = "Не удалось загрузить структуру курса.";
    console.error(e);
  } finally {
    loadingStructure.value = false;
  }
}

async function loadComments() {
  if (!activeCourseId.value || !activeSubsectionId.value) return;

  errorText.value = "";
  loadingComments.value = true;

  try {
    const data = await apiGet(
      `/api/discussions?course_id=${activeCourseId.value}&subsection_id=${activeSubsectionId.value}`,
    );

    comments.value = Array.isArray(data) ? data : [];
  } catch (e) {
    errorText.value = "Не удалось загрузить комментарии.";
    console.error(e);
  } finally {
    loadingComments.value = false;
  }
}

async function selectCourse(courseId) {
  if (activeCourseId.value === courseId) return;

  activeCourseId.value = courseId;
  activeSubsectionId.value = null;

  comments.value = [];
  replyDraft.value = {};
  replyOpen.value = {};
  newQuestion.value = "";

  await loadStructure(courseId);
}

async function selectSubsection(subId) {
  activeSubsectionId.value = subId;
  newQuestion.value = "";
  replyDraft.value = {};
  replyOpen.value = {};
  await loadComments();
}

async function submitQuestion() {
  errorText.value = "";

  if (!isAuthenticated.value) {
    errorText.value = "Требуется авторизация";
    return;
  }

  if (!activeCourseId.value || !activeSubsectionId.value) return;

  const content = (newQuestion.value || "").trim();
  if (!content) return;

  try {
    await apiPost("/api/discussions", {
      course_id: activeCourseId.value,
      subsection_id: activeSubsectionId.value,
      content,
    });

    newQuestion.value = "";
    await loadComments();
  } catch (e) {
    errorText.value = "Не удалось отправить комментарий.";
    console.error(e);
  }
}

function clearQuestion() {
  newQuestion.value = "";
}

async function sendReply(commentId) {
  errorText.value = "";

  if (!isAuthenticated.value) {
    errorText.value = "Требуется авторизация";
    return;
  }

  const content = (replyDraft.value[commentId] || "").trim();
  if (!content) return;

  try {
    await apiPost(`/api/discussions/${commentId}/replies`, { content });

    replyDraft.value[commentId] = "";
    const next = { ...replyOpen.value };
    delete next[commentId];
    replyOpen.value = next;

    await loadComments();
  } catch (e) {
    errorText.value = "Не удалось отправить ответ.";
    console.error(e);
  }
}

watch(
  () => route.query.course_id,
  async (val) => {
    if (!val) return;
    const wanted = String(val);

    // если курсы ещё не загружены — подождём загрузку через loadCourses()
    if (!courses.value || courses.value.length === 0) return;

    const found = courses.value.find((c) => String(c.id) === wanted);
    if (found && activeCourseId.value !== found.id) {
      await selectCourse(found.id);
    }
  },
);

onMounted(async () => {
  await loadCourses();
});
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

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.back-to-main {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #2f4156;
  text-decoration: none;
  font-weight: 500;
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 6px rgba(47, 65, 86, 0.08);
  transition: all 0.2s;
  width: fit-content;
}

.back-to-main:hover {
  background: #f6fbff;
  border-color: #2f4156;
}

.back-icon {
  font-size: 1.1rem;
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
  grid-template-columns: 280px 280px 1fr;
  gap: 2rem;
}

.courses-sidebar,
.sections-sidebar {
  background: #f5d6d8;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 30px rgba(212, 185, 187, 0.3);
  height: fit-content;
  position: sticky;
  top: 120px;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  margin-bottom: 2rem;
  text-align: center;
}

.sidebar-title {
  font-size: 1.25rem;
  color: #2f4156;
  font-weight: 600;
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

.courses-list,
.subsections-list,
.sections-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.course-item,
.section-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1rem;
  background: #ffffff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid rgba(47, 65, 86, 0.1);
}

.course-item {
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.course-item:hover,
.section-item:hover {
  background: #f8f8f8;
  border-color: #2f4156;
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.1);
}

.course-item.active,
.section-item.active {
  background: #ffffff;
  border-color: #2f4156;
  color: #2f4156;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.15);
}

.course-title {
  font-size: 1rem;
  color: #2f4156;
  font-weight: 700;
  line-height: 1.3;
}

.course-desc {
  color: #4a5568;
  font-size: 0.85rem;
  line-height: 1.4;
}

.sections-tree {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sec-block {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 1rem;
  border: 2px solid rgba(47, 65, 86, 0.08);
}

.sec-title {
  font-size: 1.05rem;
  color: #2f4156;
  margin-bottom: 1rem;
  font-weight: 700;
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
}

.sec-number {
  color: rgba(47, 65, 86, 0.7);
  font-weight: 700;
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

.section-status {
  font-size: 0.75rem;
  color: #2f4156;
  background: rgba(47, 65, 86, 0.06);
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(47, 65, 86, 0.12);
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

.files {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(47, 65, 86, 0.15);
}

.files-title {
  font-size: 1rem;
  color: #2f4156;
  font-weight: 700;
  margin: 0 0 0.75rem 0;
}

.file-item {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  padding: 0.35rem 0;
}

.file-link {
  color: #2f4156;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.file-link:hover {
  color: #1a2530;
}

.file-size {
  color: #4a5568;
  font-size: 0.85rem;
}

/* Стили для сообщений с отступами */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 2rem; /* Увеличил отступ между блоками сообщений */
  max-height: 500px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.message-block {
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* Отступ между основным сообщением и ответами */
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
}

.message-block:last-child {
  border-bottom: none;
  padding-bottom: 0;
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

.message__content p {
  color: #4a5568;
  line-height: 1.6;
  font-size: 0.95rem;
  margin: 0;
}

.replies-container {
  display: flex;
  flex-direction: column;
  gap: 1rem; /* Отступ между ответами */
  margin-left: 2rem; /* Отступ слева для ответов */
  padding-left: 1.5rem;
  border-left: 2px solid rgba(226, 232, 240, 0.8);
  position: relative;
}

.replies-container::before {
  content: "";
  position: absolute;
  left: -2px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(
    to bottom,
    rgba(66, 153, 225, 0.2),
    rgba(72, 187, 120, 0.2)
  );
}

.reply-wrapper {
  position: relative;
}

.reply-wrapper::before {
  content: "↳";
  position: absolute;
  left: -1.8rem;
  top: 0.5rem;
  color: #a0aec0;
  font-size: 1.2rem;
}

.reply {
  background: rgba(247, 250, 252, 0.8);
  border-left: 3px solid;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.reply.student {
  border-left-color: #4299e1;
}

.reply.teacher {
  border-left-color: #48bb78;
}

.reply-form {
  margin-top: 1rem;
  background: rgba(47, 65, 86, 0.04);
  border: 1px solid rgba(47, 65, 86, 0.12);
  border-radius: 14px;
  padding: 1rem;
}

.reply-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #4299e1;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.reply-toggle:hover {
  background: rgba(66, 153, 225, 0.1);
}

.reply-toggle::before {
  content: "↪";
  font-size: 1rem;
}

.ask-question {
  background: #c8dae8;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-top: 2rem;
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

.hint {
  background: rgba(255, 255, 255, 0.75);
  border: 2px dashed rgba(47, 65, 86, 0.25);
  border-radius: 14px;
  padding: 0.9rem 1rem;
  color: #4a5568;
  font-size: 0.95rem;
}

.error {
  background: rgba(255, 0, 0, 0.06);
  border: 2px solid rgba(255, 0, 0, 0.18);
  border-radius: 14px;
  padding: 0.9rem 1rem;
  color: #8b1d1d;
  font-weight: 600;
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

@media (max-width: 1200px) {
  .discussion-content-wrapper {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .courses-sidebar,
  .sections-sidebar {
    position: static;
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

  .replies-container {
    margin-left: 1rem;
    padding-left: 1rem;
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

  .replies-container {
    margin-left: 0.5rem;
    padding-left: 0.75rem;
  }
}
</style>
