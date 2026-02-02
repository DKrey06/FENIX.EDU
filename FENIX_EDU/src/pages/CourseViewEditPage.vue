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
                <!-- ----- ASSIGNMENT (DB) ----- -->
                <div class="assignment-box">
                  <div class="assignment-top">
                    <button
                      class="assign-btn"
                      type="button"
                      @click="
                        async () => {
                          await ensureAssignment(
                            subsection.id,
                            subsection.title,
                          );
                          await loadAssignmentAttachments(subsection.id);
                        }
                      "
                      :disabled="assignmentLoading[subsection.id]"
                    >
                      {{
                        assignmentBySubsection[subsection.id]?.id
                          ? "Открыть задание"
                          : "Создать задание"
                      }}
                      <span v-if="assignmentLoading[subsection.id]">⏳</span>
                    </button>

                    <button
                      v-if="assignmentBySubsection[subsection.id]?.id"
                      class="assign-save-btn"
                      type="button"
                      @click="saveAssignmentFields(subsection.id)"
                      :disabled="assignmentSaving[subsection.id]"
                    >
                      Сохранить поля
                      <span v-if="assignmentSaving[subsection.id]">⏳</span>
                    </button>
                  </div>

                  <div
                    v-if="assignmentBySubsection[subsection.id]?.id"
                    class="assignment-fields"
                  >
                    <label class="field-label">Описание задания</label>
                    <textarea
                      class="field-textarea"
                      v-model="
                        assignmentBySubsection[subsection.id].description
                      "
                      placeholder="Текст задания, требования, критерии..."
                      rows="4"
                    ></textarea>

                    <label class="field-label">Дедлайн</label>
                    <input
                      class="field-input"
                      type="datetime-local"
                      v-model="assignmentBySubsection[subsection.id].deadline"
                    />

                    <div class="file-upload">
                      <label
                        class="file-upload-btn"
                        :for="'assign-file-' + subsection.id"
                      >
                        {{
                          attachmentUploading[subsection.id]
                            ? "Загрузка..."
                            : "Прикрепить материалы к заданию"
                        }}
                      </label>
                      <input
                        :id="'assign-file-' + subsection.id"
                        type="file"
                        class="file-input"
                        @change="
                          uploadAssignmentAttachments($event, subsection.id)
                        "
                        multiple
                        accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.webp,.zip,.rar"
                      />
                    </div>

                    <div
                      v-if="
                        assignmentBySubsection[subsection.id]?.attachments
                          ?.length
                      "
                      class="files-list"
                    >
                      <div
                        v-for="file in assignmentBySubsection[subsection.id]
                          .attachments"
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
                          @click="
                            deleteAssignmentAttachment(subsection.id, file.id)
                          "
                        >
                          Удалить
                        </button>
                      </div>
                    </div>
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
              <div class="stat-content">
                <div class="stat-value">{{ currentCourse.progress || 0 }}%</div>
                <div class="stat-label">Прогресс курса</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-content">
                <div class="stat-value">{{ sections.length }}</div>
                <div class="stat-label">Разделов</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-content">
                <div class="stat-value">{{ totalSubsections }}</div>
                <div class="stat-label">Заданий</div>
              </div>
            </div>
            <div class="stat-item">
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

// ---- assignments state ----

const assignmentBySubsection = ref({}); // { [subsectionId]: assignmentObj }
const assignmentLoading = ref({}); // { [subsectionId]: true/false }
const assignmentSaving = ref({}); // { [subsectionId]: true/false }
const attachmentUploading = ref({}); // { [subsectionId]: true/false }

const setFlag = (objRef, key, val) => {
  objRef.value = { ...objRef.value, [key]: val };
};

const ensureAssignment = async (subsectionId, titleFallback) => {
  const courseId = route.params.id;
  const token = localStorage.getItem("access_token");

  setFlag(assignmentLoading, subsectionId, true);
  try {
    const listResp = await fetch(
      `${API_URL}/assignments?course_id=${courseId}&subsection_id=${subsectionId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      },
    );

    if (listResp.ok) {
      const list = await listResp.json();
      if (Array.isArray(list) && list.length > 0) {
        assignmentBySubsection.value = {
          ...assignmentBySubsection.value,
          [subsectionId]: list[0],
        };
        return list[0];
      }
    }

    const createResp = await fetch(`${API_URL}/assignments`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        course_id: Number(courseId),
        subsection_id: Number(subsectionId),
        title: titleFallback || "Задание",
        description: "",
        deadline: null,
      }),
    });

    if (!createResp.ok) {
      const text = await createResp.text();
      console.error("Не удалось создать задание:", createResp.status, text);
      alert("Не удалось создать задание в БД");
      return null;
    }

    const created = await createResp.json();
    assignmentBySubsection.value = {
      ...assignmentBySubsection.value,
      [subsectionId]: created,
    };
    return created;
  } catch (e) {
    console.error("ensureAssignment error:", e);
    alert("Ошибка при создании/загрузке задания");
    return null;
  } finally {
    setFlag(assignmentLoading, subsectionId, false);
  }
};

const saveAssignmentFields = async (subsectionId) => {
  const token = localStorage.getItem("access_token");
  const a = assignmentBySubsection.value[subsectionId];
  if (!a?.id) {
    alert("Сначала нажми «Создать задание в БД»");
    return;
  }

  setFlag(assignmentSaving, subsectionId, true);
  try {
    const resp = await fetch(`${API_URL}/assignments/${a.id}`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        title: a.title,
        description: a.description || "",
        deadline: a.deadline || null,
      }),
    });

    if (!resp.ok) {
      const text = await resp.text();
      console.error("Ошибка обновления задания:", resp.status, text);
      alert("Не удалось сохранить поля задания");
      return;
    }

    const updated = await resp.json();
    assignmentBySubsection.value = {
      ...assignmentBySubsection.value,
      [subsectionId]: updated,
    };
  } catch (e) {
    console.error("saveAssignmentFields error:", e);
    alert("Ошибка сохранения задания");
  } finally {
    setFlag(assignmentSaving, subsectionId, false);
  }
};

const loadAssignmentAttachments = async (subsectionId) => {
  const token = localStorage.getItem("access_token");
  const a = assignmentBySubsection.value[subsectionId];
  if (!a?.id) return;

  try {
    const resp = await fetch(`${API_URL}/assignments/${a.id}/attachments`, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
      },
    });
    if (resp.ok) {
      const files = await resp.json();
      assignmentBySubsection.value = {
        ...assignmentBySubsection.value,
        [subsectionId]: { ...a, attachments: files || [] },
      };
    }
  } catch (e) {
    console.error("loadAssignmentAttachments error:", e);
  }
};

const uploadAssignmentAttachments = async (event, subsectionId) => {
  const files = Array.from(event.target.files || []);
  if (!files.length) return;

  const token = localStorage.getItem("access_token");
  const a = assignmentBySubsection.value[subsectionId];
  if (!a?.id) {
    alert("Сначала нажми «Создать задание в БД»");
    event.target.value = "";
    return;
  }

  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));

  setFlag(attachmentUploading, subsectionId, true);
  try {
    const resp = await fetch(`${API_URL}/assignments/${a.id}/attachments`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!resp.ok) {
      const text = await resp.text();
      console.error("Ошибка загрузки файлов задания:", resp.status, text);
      alert("Не удалось загрузить файлы к заданию");
      return;
    }

    const uploaded = await resp.json();
    const prev = a.attachments || [];
    assignmentBySubsection.value = {
      ...assignmentBySubsection.value,
      [subsectionId]: { ...a, attachments: [...prev, ...(uploaded || [])] },
    };

    event.target.value = "";
  } catch (e) {
    console.error("uploadAssignmentAttachments error:", e);
    alert("Ошибка загрузки файлов");
  } finally {
    setFlag(attachmentUploading, subsectionId, false);
  }
};

const deleteAssignmentAttachment = async (subsectionId, attachmentId) => {
  const token = localStorage.getItem("access_token");
  const a = assignmentBySubsection.value[subsectionId];
  if (!a?.id) return;

  try {
    const resp = await fetch(
      `${API_URL}/assignments/${a.id}/attachments/${attachmentId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      },
    );

    if (!resp.ok) {
      const text = await resp.text();
      console.error("Ошибка удаления файла задания:", resp.status, text);
      alert("Не удалось удалить файл");
      return;
    }

    const next = (a.attachments || []).filter((x) => x.id !== attachmentId);
    assignmentBySubsection.value = {
      ...assignmentBySubsection.value,
      [subsectionId]: { ...a, attachments: next },
    };
  } catch (e) {
    console.error("deleteAssignmentAttachment error:", e);
    alert("Ошибка удаления файла");
  }
};

const totalSubsections = computed(() => {
  return sections.value.reduce(
    (total, section) => total + (section.subsections?.length || 0),
    0,
  );
});

const totalFiles = computed(() => {
  return sections.value.reduce((total, section) => {
    return (
      total +
      section.subsections.reduce(
        (acc, sub) => acc + (sub.files?.length || 0),
        0,
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
      },
    );

    if (!response.ok) {
      const text = await response.text();
      console.error("Ошибка загрузки файлов:", response.status, text);
      alert("Не удалось загрузить файлы");
      return;
    }

    const uploadedFiles = await response.json();

    const sectionIndex = sections.value.findIndex((s) =>
      s.subsections.some((sub) => sub.id === subsectionId),
    );
    const subsectionIndex = sections.value[sectionIndex].subsections.findIndex(
      (s) => s.id === subsectionId,
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
      },
    );

    if (!response.ok) {
      const text = await response.text();
      console.error("Ошибка удаления файла:", response.status, text);
      alert("Не удалось удалить файл");
      return;
    }

    const sectionIndex = sections.value.findIndex((s) =>
      s.subsections.some((sub) => sub.id === subsectionId),
    );
    const subsectionIndex = sections.value[sectionIndex].subsections.findIndex(
      (s) => s.id === subsectionId,
    );
    const fileIndex = sections.value[sectionIndex].subsections[
      subsectionIndex
    ].files.findIndex((f) => f.id === fileId);

    if (fileIndex !== -1) {
      sections.value[sectionIndex].subsections[subsectionIndex].files.splice(
        fileIndex,
        1,
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
  const allowed = ["teacher", "department_head", "admin"];
  if (!allowed.includes(authStore.user?.role)) {
    router.replace({ name: "CourseView", params: { id: route.params.id } });
    return;
  }
  await loadCourse();
});
</script>

<style scoped>
.course-detail-page {
  min-height: calc(100vh - 200px);
  padding: 2rem;
  background: linear-gradient(135deg, #f6fbff 0%, #f0f7ff 100%);
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
  transition: all 0.2s ease;
}

.breadcrumb-link:hover {
  background: #f6fbff;
  border-color: #2f4156;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(47, 65, 86, 0.12);
}

.breadcrumb-icon {
  font-size: 1.1rem;
}

.header-content {
  background: #ffffff;
  padding: 1.25rem 1.75rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #e7f0ff;
  max-width: 800px;
  width: 100%;
  flex: 1;
}

.course-title {
  font-size: 1.6rem;
  color: #2f4156;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
  max-width: 100%;
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
  border: 1px solid #e2e8f0;
}

.meta-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.dot-progress {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.dot-done {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.meta-label {
  color: #6b7280;
  font-weight: 500;
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
  border: 1px solid #e7f0ff;
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

.edit-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.save-btn,
.cancel-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 1.1rem;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.save-btn {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(5, 150, 105, 0.2);
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}

.save-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.cancel-btn {
  background: #e5e7eb;
  color: #374151;
}

.cancel-btn:hover {
  background: #d1d5db;
  transform: translateY(-1px);
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
  transition: all 0.2s ease;
}

.section-item.section-active {
  border-color: #667eea;
  box-shadow: 0 4px 14px rgba(102, 126, 234, 0.14);
  background: #f8fbff;
}

.section-header {
  padding: 0.9rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.section-header:hover {
  background: #f0f7ff;
}

.section-title {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: center;
}

.section-number {
  font-weight: 600;
  color: #2f4156;
  text-transform: uppercase;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.section-number-input {
  width: 50px;
  padding: 0.2rem 0.4rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
  text-align: center;
}

.section-name {
  font-weight: 500;
  color: #2d3748;
  font-size: 1rem;
  display: flex;
  align-items: center;
}

.section-title-input {
  padding: 0.4rem 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 1rem;
  min-width: 200px;
  width: 100%;
  max-width: 400px;
}

.section-toggle {
  font-size: 0.9rem;
  color: #667eea;
  font-weight: 500;
}

/* задания */
.subsection-list {
  padding: 0.7rem 1.1rem 0.9rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.subsection-item.editable {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  padding: 0.9rem;
  border-radius: 12px;
  background: #ffffff;
  transition: all 0.2s ease;
  border: 1px solid #e7f0ff;
}

.subsection-item.editable:hover {
  background: #f8fafc;
  transform: translateX(3px);
  border-color: #cbd5e1;
}

.subsection-left {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.subsection-icon {
  font-size: 1.1rem;
}

.subsection-name-input {
  padding: 0.4rem 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.95rem;
  flex: 1;
  min-width: 200px;
  max-width: 400px;
}

.subsection-status {
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  align-self: center;
  border: 1px solid transparent;
}

.status-pending {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border-color: #fcd34d;
}

/* Assignment Box */
.assignment-box {
  margin-top: 0.5rem;
  padding: 1rem;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
}

.assignment-top {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.assign-btn,
.assign-save-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 999px;
  padding: 0.4rem 1rem;
  border: 1px solid #2f4156;
  background: #ffffff;
  color: #2f4156;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.assign-btn:hover:not(:disabled) {
  background: #2f4156;
  color: #ffffff;
  transform: translateY(-1px);
}

.assign-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.assign-save-btn {
  border-color: #059669;
  color: #059669;
}

.assign-save-btn:hover:not(:disabled) {
  background: #059669;
  color: #ffffff;
  transform: translateY(-1px);
}

.assign-save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Поля задания */
.assignment-fields {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.field-label {
  font-size: 0.85rem;
  color: #374151;
  font-weight: 600;
}

.field-textarea,
.field-input {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.75rem;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s ease;
  background: white;
}

.field-textarea:focus,
.field-input:focus {
  border-color: #2f4156;
  box-shadow: 0 0 0 3px rgba(47, 65, 86, 0.1);
}

.field-textarea {
  min-height: 80px;
  resize: vertical;
  line-height: 1.4;
}

/* Загрузка файлов */
.file-upload {
  margin-top: 0.5rem;
}

.file-upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-upload-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.file-input {
  display: none;
}

/* Список файлов */
.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.8rem;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.file-item:hover {
  background: #f9fafb;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.file-thumb {
  width: 64px;
  height: 48px;
  border-radius: 8px;
  overflow: hidden;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d1d5db;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-icon {
  width: 48px;
  height: 36px;
  border-radius: 8px;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 600;
  color: #374151;
  border: 1px solid #d1d5db;
}

.file-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.file-name {
  font-size: 0.9rem;
  color: #111827;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  padding: 0.35rem 0.9rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-delete-btn:hover {
  background: #ef4444;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.2);
}

/* Кнопки добавления */
.add-subsection-btn,
.add-section-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px dashed #cbd5e1;
  background: transparent;
  color: #64748b;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-subsection-btn {
  margin-top: 0.5rem;
}

.add-section-btn {
  margin-top: 1rem;
}

.add-subsection-btn:hover,
.add-section-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f8fafc;
  transform: translateY(-1px);
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
  border: 1px solid #e7f0ff;
}

.stats-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2f4156;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.stat-item {
  padding: 0.75rem 0.9rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #f6fbff 0%, #e8f2ff 100%);
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.stat-item:hover {
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2f4156;
  line-height: 1;
}

.stat-label {
  font-size: 0.85rem;
  color: #4a5568;
  font-weight: 500;
}

.stat-icon {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 0.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 999px;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  color: #0369a1;
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
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .course-detail-page {
    padding: 1.25rem;
  }

  .course-title {
    font-size: 1.4rem;
  }

  .sections-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .edit-controls {
    width: 100%;
    justify-content: flex-end;
  }

  .subsection-left {
    flex-wrap: wrap;
  }

  .subsection-name-input {
    min-width: 150px;
    max-width: 100%;
  }

  .assignment-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .assign-btn,
  .assign-save-btn {
    width: 100%;
    justify-content: center;
  }

  .file-item {
    flex-wrap: wrap;
  }

  .stat-item {
    padding: 0.6rem 0.75rem;
  }
}

@media (max-width: 480px) {
  .course-detail-page {
    padding: 1rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .section-toggle {
    align-self: flex-end;
  }

  .save-btn,
  .cancel-btn {
    width: 100%;
    justify-content: center;
  }

  .edit-controls {
    flex-direction: column;
    width: 100%;
  }
}
</style>
