<template>
  <div class="course-detail-page">
    <div class="course-header">
      <div class="breadcrumb">
        <router-link to="/archive" class="breadcrumb-link">
          <span class="breadcrumb-icon">←</span>
          Назад к архиву
        </router-link>
      </div>
      <div class="header-content">
        <h1 class="course-title">{{ currentCourse.title || currentCourse.name }}</h1>
        <div class="course-meta">
          <div class="meta-item">
            <span class="meta-dot" :class="currentCourse.status === 'inProgress' ? 'dot-progress' : 'dot-done'"></span>
            <span class="meta-text">
              {{ currentCourse.status === "inProgress" ? "В процессе" : "Завершен" }}
            </span>
          </div>
          <div class="meta-item" v-if="currentCourse.status === 'inProgress'">
            <span class="meta-label">Прогресс:</span>
            <span class="meta-value">{{ currentCourse.progress || 0 }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="course-content">
      <!-- левая колонка: разделы -->
      <div class="course-sections">
        <div class="sections-header">
          <h2 class="sections-title">Содержание курса</h2>
          <button
            v-if="canEdit"
            class="edit-btn"
            @click="handleEdit"
          >
            ✏️ Редактировать
          </button>
        </div>

        <div class="sections-list">
          <div
            v-for="section in sections"
            :key="section.id"
            class="section-item"
            :class="{ 'section-active': activeSection === section.id }"
          >
            <div class="section-header" @click="toggleSection(section.id)">
              <div class="section-title">
                <span class="section-number">Раздел {{ section.number }}.</span>
                <span class="section-name">{{ section.title }}</span>
              </div>
              <span class="section-toggle">
                {{ activeSection === section.id ? "Скрыть" : "Показать" }}
              </span>
            </div>

            <div class="subsection-list" v-if="activeSection === section.id">
              <div
                v-for="subsection in section.subsections"
                :key="subsection.id"
                class="subsection-item"
              >
                <div class="subsection-main">
                  <span class="subsection-icon">{{ subsection.icon }}</span>
                  <div class="subsection-text">
                    <div class="subsection-name">{{ subsection.title }}</div>
                    <div class="subsection-description">
                      Задание раздела и прикреплённые материалы.
                    </div>
                  </div>
                  <span class="subsection-status" :class="subsection.status">
                    {{ statusText(subsection.status) }}
                  </span>
                </div>

                <!-- файлы задания -->
                <div
                  v-if="subsection.files && subsection.files.length"
                  class="subsection-files"
                >
                  <div
                    v-for="file in subsection.files"
                    :key="file.id"
                    class="file-row"
                  >
                    <button
                      class="file-thumb"
                      v-if="isImage(file.name) && file.url"
                      type="button"
                      @click="openImage(API_BASE + file.url, file.name)"
                    >
                      <img
                        :src="API_BASE + file.url"
                        :alt="file.name"
                        class="thumb-img"
                      />
                    </button>
                    <div class="file-icon" v-else>
                      📄
                    </div>

                    <div class="file-info">
                      <div class="file-name">{{ file.name }}</div>
                      <div class="file-meta">
                        {{ formatFileSize(file.size) }}
                      </div>
                    </div>
                  </div>
                </div>
                <!-- /файлы задания -->
              </div>
            </div>
          </div>

          <div v-if="!sections.length" class="empty-structure">
            Структура курса пока не настроена.
          </div>
        </div>
      </div>

      <!-- правая колонка: статистика -->
      <div class="course-stats-panel">
        <div class="course-stats">
          <div class="stats-title">Статистика курса</div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon">📊</div>
              <div class="stat-content">
                <div class="stat-value">{{ currentCourse.progress || 0 }}%</div>
                <div class="stat-label">Прогресс курса</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">📚</div>
              <div class="stat-content">
                <div class="stat-value">{{ sections.length }}</div>
                <div class="stat-label">Разделов</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">📝</div>
              <div class="stat-content">
                <div class="stat-value">{{ totalSubsections }}</div>
                <div class="stat-label">Заданий</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">⭐</div>
              <div class="stat-content">
                <div class="stat-value">4.8</div>
                <div class="stat-label">Рейтинг</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- полноэкранный просмотр изображения -->
    <div
      v-if="previewImageUrl"
      class="image-modal"
      @click.self="closeImage"
    >
      <div class="image-modal-content">
        <img :src="previewImageUrl" :alt="previewImageName" />
        <div class="image-modal-footer">
          <span class="image-name">{{ previewImageName }}</span>
          <button class="image-close-btn" type="button" @click="closeImage">
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const API_URL = "http://127.0.0.1:8000/api";
const API_BASE = "http://127.0.0.1:8000";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const activeSection = ref(1);
const currentCourse = ref({});
const sections = ref([]);

const previewImageUrl = ref(null);
const previewImageName = ref("");

const totalSubsections = computed(() => {
  return sections.value.reduce(
    (total, section) => total + (section.subsections?.length || 0),
    0
  );
});

const canEdit = computed(() => authStore.user?.role === "teacher");

const toggleSection = (sectionId) => {
  activeSection.value = activeSection.value === sectionId ? null : sectionId;
};

const handleEdit = () => {
  if (!canEdit.value) return;
  router.push({ name: "CourseViewEdit", params: { id: route.params.id } });
};

const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return "0 Б";
  const k = 1024;
  const sizes = ["Б", "КБ", "МБ", "ГБ"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
};

const isImage = (name) => {
  if (!name) return false;
  const lower = name.toLowerCase();
  return (
    lower.endsWith(".jpg") ||
    lower.endsWith(".jpeg") ||
    lower.endsWith(".png") ||
    lower.endsWith(".gif") ||
    lower.endsWith(".webp")
  );
};

const statusText = (status) => {
  switch (status) {
    case "status-completed":
      return "Завершено";
    case "status-pending":
      return "В ожидании";
    case "status-locked":
      return "Закрыто";
    default:
      return "";
  }
};

const openImage = (url, name) => {
  previewImageUrl.value = url;
  previewImageName.value = name || "";
};

const closeImage = () => {
  previewImageUrl.value = null;
  previewImageName.value = "";
};

const loadCourse = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const courseId = route.params.id;

    const coursesResp = await fetch(`${API_URL}/courses`, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
      },
    });

    if (coursesResp.ok) {
      const list = await coursesResp.json();
      const course = list.find((c) => String(c.id) === String(courseId));
      if (course) currentCourse.value = course;
    }

    const structResp = await fetch(`${API_URL}/courses/${courseId}/structure`, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
      },
    });

    if (structResp.ok) {
      const data = await structResp.json();
      sections.value = data.sections || [];
      if (sections.value.length) {
        activeSection.value = sections.value[0].id;
      }
    } else {
      sections.value = [];
    }
  } catch (e) {
    console.error("Ошибка загрузки курса/структуры:", e);
    sections.value = [];
  }
};

onMounted(() => {
  loadCourse();
});
</script>

<style scoped>
.course-detail-page {
  min-height: calc(100vh - 200px);
  padding: 2rem;
  background: #f6fbff;
}

/* шапка курса */

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.breadcrumb {
  margin-bottom: 1rem;
}

.breadcrumb-link {
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
}

.breadcrumb-link:hover {
  background: #f6fbff;
  border-color: #2f4156;
}

.breadcrumb-icon {
  font-size: 1.1rem;
}

.header-content {
  background: #ffffff;
  padding: 1.5rem 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.course-title {
  font-size: 1.8rem;
  color: #2f4156;
  font-weight: 700;
  margin: 0;
}

.course-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.8rem;
  background: #f8fafc;
  border-radius: 999px;
  font-size: 0.9rem;
}

.meta-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.dot-progress {
  background: #f59e0b;
}

.dot-done {
  background: #10b981;
}

.meta-label {
  color: #6b7280;
}

.meta-value {
  font-weight: 600;
  color: #111827;
}

.meta-text {
  color: #4a5568;
  font-weight: 500;
}

/* основной контент */

.course-content {
  display: grid;
  grid-template-columns: 3fr 1.4fr;
  gap: 2rem;
}

/* левая колонка — разделы */

.course-sections {
  background: #ffffff;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.sections-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.75rem;
}

.sections-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2f4156;
  margin: 0;
}

.edit-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  border: 1px solid #2f4156;
  background: #ffffff;
  color: #2f4156;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: #2f4156;
  color: #ffffff;
}

.sections-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-top: 0.75rem;
}

.section-item {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  background: #f9fbff;
  transition: all 0.2s;
}

.section-item.section-active {
  border-color: #2f4156;
  box-shadow: 0 4px 14px rgba(47, 65, 86, 0.14);
}

.section-header {
  padding: 0.9rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.section-title {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: baseline;
}

.section-number {
  font-weight: 600;
  color: #2f4156;
  text-transform: uppercase;
}

.section-name {
  font-weight: 500;
  color: #2d3748;
}

.section-toggle {
  font-size: 0.9rem;
  color: #4b5563;
}

/* задания */

.subsection-list {
  padding: 0.7rem 1.1rem 0.9rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.subsection-item {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  padding: 0.65rem 0.85rem;
  border-radius: 10px;
  background: #ffffff;
  transition: all 0.2s;
}

.subsection-item:hover {
  background: #edf2f7;
  transform: translateX(3px);
}

.subsection-main {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
}

.subsection-icon {
  font-size: 1.1rem;
  margin-top: 0.1rem;
}

.subsection-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.subsection-name {
  font-size: 0.95rem;
  color: #111827;
  font-weight: 500;
}

.subsection-description {
  font-size: 0.85rem;
  color: #6b7280;
  line-height: 1.35;
}

.subsection-status {
  padding: 0.1rem 0.6rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  align-self: center;
}

.status-completed {
  background: #dcfce7;
  color: #166534;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-locked {
  background: #e5e7eb;
  color: #374151;
}

/* файлы задания */

.subsection-files {
  padding-left: 2.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.file-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 0.55rem;
  border-radius: 6px;
  background: #f9fafb;
}

.file-thumb {
  width: 64px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  padding: 0;
  cursor: pointer;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-icon {
  width: 40px;
  height: 32px;
  border-radius: 6px;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: #374151;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 0.9rem;
  color: #111827;
}

.file-meta {
  font-size: 0.8rem;
  color: #6b7280;
}

/* правая колонка — статистика */

.course-stats-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.course-stats {
  background: #ffffff;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.stats-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2f4156;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.9rem;
  border-radius: 12px;
  background: #f6fbff;
}

.stat-icon {
  font-size: 1.4rem;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2f4156;
}

.stat-label {
  font-size: 0.85rem;
  color: #4a5568;
}

/* модалка полноэкранного просмотра изображения */

.image-modal {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
}

.image-modal-content {
  max-width: 90vw;
  max-height: 90vh;
  background: #0f172a;
  border-radius: 12px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.image-modal-content img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 8px;
  background: #020617;
}

.image-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: #e5e7eb;
}

.image-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 260px;
}

.image-close-btn {
  border: none;
  border-radius: 999px;
  padding: 0.35rem 0.9rem;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  background: #f97316;
  color: #ffffff;
}

/* адаптив */

@media (max-width: 992px) {
  .course-content {
    grid-template-columns: 1fr;
  }

  .course-header {
    flex-direction: column;
    gap: 1rem;
  }

  .header-content {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .course-detail-page {
    padding: 1.25rem;
  }

  .course-title {
    font-size: 1.5rem;
  }

  .sections-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>
