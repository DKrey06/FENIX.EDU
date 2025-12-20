<template>
  <div class="course-detail-page">
    <div class="course-header">
      <div class="breadcrumb">
        <router-link
          :to="{ name: 'CourseView', params: { id: route.params.id } }"
          class="breadcrumb-link"
        >
          <span class="breadcrumb-icon">←</span>
          Просмотр курса
        </router-link>
      </div>
      <div class="header-content">
        <h1 class="course-title">
          {{ currentCourse.title || currentCourse.name }}
        </h1>
        <div class="course-meta">
          <div class="meta-item">
            <span
              class="meta-dot"
              :class="
                currentCourse.status === 'inProgress'
                  ? 'dot-progress'
                  : 'dot-done'
              "
            ></span>
            <span class="meta-text">
              {{
                currentCourse.status === "inProgress"
                  ? "В процессе"
                  : "Завершен"
              }}
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
      <div class="course-sections">
        <div class="sections-header">
          <h2 class="sections-title">Редактирование содержания</h2>
          <div class="edit-controls">
            <button class="save-btn" @click="saveChanges" :disabled="isSaving">
              <span class="save-icon">{{ isSaving ? "⏳" : "💾" }}</span>
              {{ isSaving ? "Сохранение..." : "Сохранить" }}
            </button>
            <button class="cancel-btn" @click="cancelEdit">Отмена</button>
          </div>
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
                <span class="section-number">
                  Раздел
                  <input
                    type="number"
                    min="1"
                    v-model.number="section.number"
                    class="section-number-input"
                    @click.stop
                  />
                  .
                </span>
                <span class="section-name">
                  <input
                    v-model="section.title"
                    class="section-title-input"
                    @click.stop
                  />
                </span>
              </div>
              <span class="section-toggle">
                {{ activeSection === section.id ? "Скрыть" : "Показать" }}
              </span>
            </div>

            <div class="subsection-list" v-if="activeSection === section.id">
              <div
                v-for="subsection in section.subsections"
                :key="subsection.id"
                class="subsection-item editable"
              >
                <div class="subsection-left">
                  <span class="subsection-icon">{{ subsection.icon }}</span>
                  <input
                    v-model="subsection.title"
                    class="subsection-name-input"
                  />
                  <div class="subsection-status" :class="subsection.status">
                    {{ subsection.statusIcon }}
                  </div>
                </div>

                <div class="file-upload">
                  <label class="file-upload-btn" :for="'file-' + subsection.id">
                    Прикрепить файлы
                  </label>
                  <input
                    :id="'file-' + subsection.id"
                    type="file"
                    class="file-input"
                    @change="handleFileUpload($event, subsection.id)"
                    multiple
                    accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.webp"
                  />
                </div>

                <div
                  v-if="subsection.files && subsection.files.length > 0"
                  class="files-list"
                >
                  <div
                    v-for="file in subsection.files"
                    :key="file.id"
                    class="file-item"
                  >
                    <div
                      class="file-thumb"
                      v-if="isImage(file.name) && file.url"
                    >
                      <img
                        :src="API_BASE + file.url"
                        :alt="file.name"
                        class="thumb-img"
                      />
                    </div>
                    <span class="file-icon" v-else>FILE</span>

                    <div class="file-main">
                      <span class="file-name">{{ file.name }}</span>
                      <span class="file-size">{{
                        formatFileSize(file.size)
                      }}</span>
                    </div>
                    <button
                      class="file-delete-btn"
                      @click="deleteFile(subsection.id, file.id)"
                    >
                      Удалить
                    </button>
                  </div>
                </div>
              </div>

              <button
                class="add-subsection-btn"
                @click="addSubsection(section.id)"
              >
                Добавить задание
              </button>
            </div>
          </div>

          <button class="add-section-btn" @click="addNewSection">
            Добавить раздел
          </button>
        </div>
      </div>

      <div class="course-stats-panel">
        <div class="course-stats">
          <div class="stats-title">Статистика курса</div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon">%</div>
              <div class="stat-content">
                <div class="stat-value">{{ currentCourse.progress || 0 }}%</div>
                <div class="stat-label">Прогресс курса</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">R</div>
              <div class="stat-content">
                <div class="stat-value">{{ sections.length }}</div>
                <div class="stat-label">Разделов</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">T</div>
              <div class="stat-content">
                <div class="stat-value">{{ totalSubsections }}</div>
                <div class="stat-label">Заданий</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">F</div>
              <div class="stat-content">
                <div class="stat-value">{{ totalFiles }}</div>
                <div class="stat-label">Файлов</div>
              </div>
            </div>
          </div>
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

const activeSection = ref(null);
const currentCourse = ref({});
const sections = ref([]);
const isSaving = ref(false);

const totalSubsections = computed(() => {
  return sections.value.reduce(
    (total, section) => total + (section.subsections?.length || 0),
    0
  );
});

const totalFiles = computed(() => {
  return sections.value.reduce((total, section) => {
    return (
      total +
      section.subsections.reduce(
        (acc, sub) => acc + (sub.files?.length || 0),
        0
      )
    );
  }, 0);
});

const toggleSection = (sectionId) => {
  activeSection.value = activeSection.value === sectionId ? null : sectionId;
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

const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return "0 Б";
  const k = 1024;
  const sizes = ["Б", "КБ", "МБ", "ГБ"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
};

const handleFileUpload = async (event, subsectionId) => {
  const files = Array.from(event.target.files);
  if (!files.length) return;

  const token = localStorage.getItem("access_token");
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  try {
    const response = await fetch(
      `${API_URL}/subsections/${subsectionId}/files`,
      {
        method: "POST",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const text = await response.text();
      console.error("Ошибка загрузки файлов:", response.status, text);
      alert("Не удалось загрузить файлы");
      return;
    }

    const uploadedFiles = await response.json();

    const sectionIndex = sections.value.findIndex((s) =>
      s.subsections.some((sub) => sub.id === subsectionId)
    );
    const subsectionIndex = sections.value[sectionIndex].subsections.findIndex(
      (s) => s.id === subsectionId
    );

    if (sectionIndex !== -1 && subsectionIndex !== -1) {
      sections.value[sectionIndex].subsections[subsectionIndex].files = [
        ...(sections.value[sectionIndex].subsections[subsectionIndex].files ||
          []),
        ...uploadedFiles,
      ];
    }

    event.target.value = "";
  } catch (e) {
    console.error("Ошибка загрузки файлов:", e);
    alert("Ошибка загрузки файлов");
  }
};

const deleteFile = async (subsectionId, fileId) => {
  const token = localStorage.getItem("access_token");

  try {
    const response = await fetch(
      `${API_URL}/subsections/${subsectionId}/files/${fileId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
          Accept: "application/json",
        },
      }
    );

    if (!response.ok) {
      const text = await response.text();
      console.error("Ошибка удаления файла:", response.status, text);
      alert("Не удалось удалить файл");
      return;
    }

    const sectionIndex = sections.value.findIndex((s) =>
      s.subsections.some((sub) => sub.id === subsectionId)
    );
    const subsectionIndex = sections.value[sectionIndex].subsections.findIndex(
      (s) => s.id === subsectionId
    );
    const fileIndex = sections.value[sectionIndex].subsections[
      subsectionIndex
    ].files.findIndex((f) => f.id === fileId);

    if (fileIndex !== -1) {
      sections.value[sectionIndex].subsections[subsectionIndex].files.splice(
        fileIndex,
        1
      );
    }
  } catch (e) {
    console.error("Ошибка удаления файла:", e);
    alert("Ошибка удаления файла");
  }
};

const addSubsection = (sectionId) => {
  const sectionIndex = sections.value.findIndex((s) => s.id === sectionId);
  const newSubsection = {
    id: Date.now(),
    icon: "",
    title: "Новое задание",
    status: "status-pending",
    statusIcon: "▶",
    files: [],
  };
  sections.value[sectionIndex].subsections.push(newSubsection);
};

const addNewSection = () => {
  const maxNumber =
    sections.value.length > 0
      ? Math.max(...sections.value.map((s) => Number(s.number) || 0))
      : 0;

  const newSection = {
    id: Date.now(),
    number: maxNumber + 1,
    title: "Новый раздел",
    subsections: [],
  };
  sections.value.push(newSection);
};

const saveChanges = async () => {
  isSaving.value = true;

  try {
    const token = localStorage.getItem("access_token");
    const courseId = route.params.id;

    const payload = {
      sections: sections.value,
    };

    const response = await fetch(`${API_URL}/courses/${courseId}/structure`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const text = await response.text();
      console.error("Ошибка сохранения структуры:", response.status, text);
      alert("Не удалось сохранить структуру курса");
      return;
    }

    router.push({ name: "CourseView", params: { id: route.params.id } });
  } catch (e) {
    console.error("Ошибка сохранения структуры:", e);
    alert("Ошибка сохранения курса");
  } finally {
    isSaving.value = false;
  }
};

const cancelEdit = () => {
  router.push({ name: "CourseView", params: { id: route.params.id } });
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

onMounted(async () => {
  if (authStore.user?.role !== "teacher") {
    router.replace({ name: "CourseView", params: { id: route.params.id } });
    return;
  }
  await loadCourse();
});
</script>

<style scoped>
/* можно оставить твои стили, ниже только новые/доп. */
.course-detail-page {
  min-height: calc(100vh - 200px);
  padding: 2rem;
  background: #f6fbff;
}

.save-btn,
.cancel-btn {
  border-radius: 999px;
  padding: 0.45rem 1.1rem;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
}

.save-btn {
  background: #059669;
  color: #ffffff;
  margin-right: 0.5rem;
}

.save-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.cancel-btn {
  background: #e5e7eb;
  color: #374151;
}

.file-item {
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
  font-size: 0.7rem;
  font-weight: 600;
  color: #374151;
}

.file-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 0.9rem;
  color: #111827;
}

.file-size {
  font-size: 0.8rem;
  color: #6b7280;
}

.file-delete-btn {
  background: #f87171;
  color: white;
  border: none;
  border-radius: 999px;
  padding: 0.25rem 0.7rem;
  font-size: 0.8rem;
  cursor: pointer;
}
</style>
