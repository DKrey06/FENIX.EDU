<template>
  <div class="edit-page">
    <header class="edit-header">
      <div class="edit-header-left">
        <h1 class="edit-title">Редактирование курса</h1>
        <p class="edit-subtitle">
          Измените данные и сохраните, чтобы обновить курс.
        </p>
      </div>
      <div class="edit-header-right">
        <button class="btn-secondary" @click="goBack">Назад</button>
        <button class="btn-ghost" @click="handleLogout">Выход</button>
      </div>
    </header>

    <main class="edit-main">
      <section class="edit-form-card">
        <h2 class="section-title">Основная информация</h2>
        <form @submit.prevent="saveCourse" class="form-grid">
          <div class="form-field">
            <label class="form-label">Название курса</label>
            <input
              v-model="form.title"
              type="text"
              class="form-input"
              required
            />
          </div>

          <div class="form-field">
            <label class="form-label">Описание</label>
            <textarea
              v-model="form.description"
              class="form-textarea"
              rows="4"
              required
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="form-label">Статус</label>
              <select v-model="form.status" class="form-select">
                <option value="inProgress">В процессе</option>
                <option value="completed">Завершен</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="form-label">Популярный курс</label>
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="form.isPopular"
                  class="checkbox-input"
                />
                <span>Отметить как популярный</span>
              </label>
            </div>

            <div class="form-field">
              <label class="form-label">Новый курс</label>
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="form.isNew"
                  class="checkbox-input"
                />
                <span>Показывать как новый</span>
              </label>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="goBack">
              Отмена
            </button>
            <button type="submit" class="btn-primary">
              Сохранить изменения
            </button>
          </div>

          <p v-if="saved" class="saved-text">
            Изменения сохранены для курса с идентификатором {{ courseId }}.
          </p>
        </form>
      </section>

      <aside class="edit-preview-card">
        <h2 class="section-title">Превью карточки курса</h2>
        <div class="course-card">
          <div class="course-image">
            <img
              src="@/assets/images/Course.png"
              alt="Course"
              class="course-img"
            />
          </div>
          <div class="course-header">
            <span class="course-status" :class="form.status">
              {{ form.status === "inProgress" ? "В процессе" : "Завершен" }}
            </span>
          </div>
          <div class="course-body">
            <h3 class="course-title">{{ form.title }}</h3>
            <p class="course-description">
              {{ form.description }}
            </p>
            <div
              class="course-progress"
              v-if="form.status === 'inProgress'"
            >
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: form.progress + '%' }"
                ></div>
              </div>
              <span class="progress-text">{{ form.progress }}%</span>
            </div>
          </div>
        </div>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const courseId = computed(() => route.params.id);

// Здесь можно будет подгружать реальные данные курса по courseId
const form = ref({
  title: "Название курса",
  description: "Краткое описание курса",
  status: "inProgress",
  progress: 50,
  isPopular: false,
  isNew: false,
});

const saved = ref(false);

const goBack = () => {
  router.push("/archive");
};

const saveCourse = () => {
  saved.value = true;
  // Здесь можно отправить запрос на сервер с form.value и courseId.value
  console.log("Сохраняем курс", courseId.value, form.value);
};

const handleLogout = () => {
  localStorage.removeItem("isAuthenticated");
  localStorage.removeItem("userData");
  router.push("/login");
};
</script>

<style scoped>
.edit-page {
  min-height: 100vh;
  padding: 2rem 3rem;
  background: #e7e7ec;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.edit-header-left {
  max-width: 60%;
}

.edit-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #2f4156;
}

.edit-subtitle {
  margin-top: 0.5rem;
  font-size: 0.95rem;
  color: #4a5568;
}

.edit-header-right {
  display: flex;
  gap: 0.75rem;
}

.edit-main {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 1.1fr);
  gap: 2rem;
  align-items: flex-start;
}

/* Карточки */
.edit-form-card,
.edit-preview-card {
  background: #f6fbff;
  border-radius: 20px;
  padding: 1.75rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.section-title {
  font-size: 1.1rem;
  color: #2f4156;
  margin: 0 0 1rem 0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Форма */
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-label {
  font-size: 0.9rem;
  color: #2f4156;
  font-weight: 600;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #cbd5e0;
  padding: 0.6rem 0.75rem;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #ffffff;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  border-color: #2f4156;
  box-shadow: 0 0 0 1px rgba(47, 65, 86, 0.2);
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #2f4156;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  accent-color: #2f4156;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.saved-text {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: #38a169;
}

/* Кнопки */
.btn-primary {
  padding: 0.6rem 1.4rem;
  background: #2f4156;
  color: white;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s, transform 0.1s;
}

.btn-primary:hover {
  background: #243347;
  transform: translateY(-1px);
}

.btn-secondary {
  padding: 0.6rem 1.4rem;
  background: #e7e7ec;
  color: #2f4156;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s, transform 0.1s;
}

.btn-secondary:hover {
  background: #d5d5dd;
  transform: translateY(-1px);
}

.btn-ghost {
  padding: 0.5rem 1.1rem;
  background: transparent;
  border-radius: 8px;
  border: 1px solid #cbd5e0;
  color: #2f4156;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s, border-color 0.2s;
}

.btn-ghost:hover {
  background: #f1f1f5;
  border-color: #2f4156;
}

/* Превью карточки курса */
.course-card {
  background: #c8dae8;
  border-radius: 16px;
  padding: 1.25rem;
  border: 2px solid transparent;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.course-image {
  width: 100%;
  height: 140px;
  margin-bottom: 1rem;
  border-radius: 12px;
  overflow: hidden;
  background: white;
  flex-shrink: 0;
}

.course-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0.75rem;
}

.course-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
}

.course-status.inProgress {
  background: #2f4156;
  color: white;
}

.course-status.completed {
  background: #48bb78;
  color: white;
}

.course-body {
  margin-bottom: 0.75rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.course-title {
  font-size: 1.1rem;
  color: #2f4156;
  margin-bottom: 0.5rem;
  font-weight: 700;
  line-height: 1.3;
}

.course-description {
  color: #4a5568;
  font-size: 0.85rem;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.course-progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #2f4156;
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 0.8rem;
  color: #2f4156;
  font-weight: 600;
  min-width: 35px;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .edit-main {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .edit-page {
    padding: 1.25rem 1.5rem;
  }

  .edit-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .edit-header-left {
    max-width: 100%;
  }
}
</style>
