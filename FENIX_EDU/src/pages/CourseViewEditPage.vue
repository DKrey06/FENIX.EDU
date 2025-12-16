<template>
  <div class="course-detail-page">
    <div class="course-header">
      <div class="breadcrumb">
        <router-link to="/course/:id" class="breadcrumb-link">
          <span class="breadcrumb-icon">←</span>
          Просмотр курса
        </router-link>
      </div>
      <div class="header-content">
        <h1 class="course-title">{{ currentCourse.title }}</h1>
        <div class="course-meta">
          <div class="meta-item">
            <span class="meta-icon">{{ currentCourse.status === 'inProgress' ? '📚' : '✅' }}</span>
            <span class="meta-text">{{ currentCourse.status === 'inProgress' ? 'В процессе' : 'Завершен' }}</span>
          </div>
          <div class="meta-item" v-if="currentCourse.status === 'inProgress'">
            <span class="meta-icon">📊</span>
            <span class="meta-text">{{ currentCourse.progress }}% прогресс</span>
          </div>
        </div>
      </div>
    </div>

    <div class="course-content">
      <div class="course-sections">
        <div class="sections-header">
          <h2 class="sections-title">Содержание курса</h2>
          <div class="edit-controls">
            <button class="save-btn" @click="saveChanges">
              <span class="save-icon">💾</span>
              Сохранить
            </button>
            <button class="cancel-btn" @click="cancelEdit">
              <span class="cancel-icon">❌</span>
              Отмена
            </button>
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
                <span class="section-number">Раздел {{ section.number }}.</span>
                <span class="section-name">{{ section.title }}</span>
              </div>
              <span class="section-toggle">{{ activeSection === section.id ? "−" : "+" }}</span>
            </div>
            
            <div class="subsection-list" v-if="activeSection === section.id">
              <div
                v-for="subsection in section.subsections"
                :key="subsection.id"
                class="subsection-item editable"
              >
                <div class="subsection-left">
                  <span class="subsection-icon">{{ subsection.icon }}</span>
                  <span class="subsection-name">{{ subsection.title }}</span>
                  <div class="subsection-status" :class="subsection.status">
                    {{ subsection.statusIcon }}
                  </div>
                </div>
                
                <!-- Кнопка прикрепления файлов -->
                <div class="file-upload">
                  <label class="file-upload-btn" :for="'file-' + subsection.id">
                    📎 Добавить файл
                  </label>
                  <input
                    :id="'file-' + subsection.id"
                    type="file"
                    class="file-input"
                    @change="handleFileUpload($event, subsection.id)"
                    multiple
                    accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.png"
                  />
                </div>

                <!-- Список прикрепленных файлов -->
                <div v-if="subsection.files && subsection.files.length > 0" class="files-list">
                  <div
                    v-for="file in subsection.files"
                    :key="file.id"
                    class="file-item"
                  >
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <span class="file-size">{{ formatFileSize(file.size) }}</span>
                    <button 
                      class="file-delete-btn" 
                      @click="deleteFile(subsection.id, file.id)"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>

              <!-- Кнопка добавления нового подраздела -->
              <button class="add-subsection-btn" @click="addSubsection(section.id)">
                ➕ Добавить задание
              </button>
            </div>
          </div>

          <!-- Кнопка добавления нового раздела -->
          <button class="add-section-btn" @click="addNewSection">
            ➕ Добавить раздел
          </button>
        </div>
      </div>

      <!-- Статистика (остается как в просмотре) -->
      <div class="course-stats-panel">
        <div class="course-stats">
          <div class="stats-title">Статистика курса</div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon">📊</div>
              <div class="stat-content">
                <div class="stat-value">{{ currentCourse.progress }}%</div>
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
              <div class="stat-icon">📎</div>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const activeSection = ref(1)
const currentCourse = ref({})

// Массив курсов (тот же что в IndexPage/ArchivePage)
const courses = [
  {
    id: 1, title: "Математический анализ", status: "inProgress", progress: 65
  },
  {
    id: 2, title: "Основы программирования", status: "inProgress", progress: 85
  },
  {
    id: 3, title: "Веб-дизайн", status: "completed", progress: 100
  }
  // ... остальные курсы
]

// Разделы с подразделами и файлами
const sections = ref([
  {
    id: 1,
    number: 'I',
    title: 'Введение в анализ',
    subsections: [
      { 
        id: 1, 
        icon: '📝', 
        title: 'Тест 1', 
        status: 'status-completed', 
        statusIcon: '✓',
        files: [
          { id: 1, name: 'test1.pdf', size: 1024 },
          { id: 2, name: 'answers.docx', size: 2048 }
        ]
      },
      { 
        id: 2, 
        icon: '📄', 
        title: 'Лекция 1', 
        status: 'status-completed', 
        statusIcon: '✓',
        files: []
      }
    ]
  },
  {
    id: 2,
    number: 'II',
    title: 'Пределы и непрерывность',
    subsections: [
      { 
        id: 3, 
        icon: '🎬', 
        title: 'Видео 1', 
        status: 'status-pending', 
        statusIcon: '▶',
        files: []
      }
    ]
  }
])

const totalSubsections = computed(() => {
  return sections.value.reduce((total, section) => total + section.subsections.length, 0)
})

const totalFiles = computed(() => {
  return sections.value.reduce((total, section) => {
    return total + section.subsections.reduce((acc, sub) => acc + (sub.files?.length || 0), 0)
  }, 0)
})

const toggleSection = (sectionId) => {
  activeSection.value = activeSection.value === sectionId ? null : sectionId
}

const handleFileUpload = (event, subsectionId) => {
  const files = Array.from(event.target.files)
  const sectionIndex = sections.value.findIndex(s => 
    s.subsections.some(sub => sub.id === subsectionId)
  )
  const subsectionIndex = sections.value[sectionIndex].subsections.findIndex(s => s.id === subsectionId)
  
  files.forEach(file => {
    const fileData = {
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size
    }
    sections.value[sectionIndex].subsections[subsectionIndex].files.push(fileData)
  })
}

const deleteFile = (subsectionId, fileId) => {
  const sectionIndex = sections.value.findIndex(s => 
    s.subsections.some(sub => sub.id === subsectionId)
  )
  const subsectionIndex = sections.value[sectionIndex].subsections.findIndex(s => s.id === subsectionId)
  const fileIndex = sections.value[sectionIndex].subsections[subsectionIndex].files.findIndex(f => f.id === fileId)
  
  sections.value[sectionIndex].subsections[subsectionIndex].files.splice(fileIndex, 1)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const addSubsection = (sectionId) => {
  const sectionIndex = sections.value.findIndex(s => s.id === sectionId)
  const newSubsection = {
    id: Date.now(),
    icon: '📄',
    title: 'Новое задание',
    status: 'status-pending',
    statusIcon: '▶',
    files: []
  }
  sections.value[sectionIndex].subsections.push(newSubsection)
}

const addNewSection = () => {
  const newSection = {
    id: Date.now(),
    number: String.fromCharCode(64 + sections.value.length + 1),
    title: 'Новый раздел',
    subsections: []
  }
  sections.value.push(newSection)
}

const saveChanges = () => {
  console.log('Сохраненные изменения:', sections.value)
  // Здесь логика сохранения на сервер
  router.push({ name: 'CourseView', params: { id: route.params.id } })
}

const cancelEdit = () => {
  router.push({ name: 'CourseView', params: { id: route.params.id } })
}

onMounted(() => {
  const courseId = parseInt(route.params.id)
  const course = courses.find(c => c.id === courseId)
  if (course) {
    currentCourse.value = course
  }
})
</script>

<style scoped>
.course-detail-page {
  padding: 2rem;
  background: #f7fafc;
  min-height: 100vh;
}

/* Шапка курса */
.course-header {
  margin-bottom: 2.5rem;
}

.breadcrumb {
  margin-bottom: 1rem;
}

.breadcrumb-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s;
}

.breadcrumb-link:hover {
  background: rgba(102, 126, 234, 0.1);
}

.breadcrumb-icon {
  font-size: 1.2rem;
}

.header-content {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.course-title {
  font-size: 2.5rem;
  color: #2d3748;
  margin-bottom: 1rem;
  font-weight: 700;
}

.course-meta {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f7fafc;
  border-radius: 8px;
}

.meta-icon {
  font-size: 1.2rem;
}

.meta-text {
  color: #4a5568;
  font-weight: 500;
}

/* Основной контент */
.course-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
  margin-bottom: 2rem;
}

/* Левая колонка - Разделы */
.course-sections {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.sections-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e2e8f0;
}

.sections-title {
  font-size: 1.5rem;
  color: #2d3748;
  font-weight: 600;
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.edit-btn:hover {
  background: #5a67d8;
  transform: translateY(-1px);
}

.edit-icon {
  font-size: 1.1rem;
}

.sections-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-item {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
}

.section-item.section-active {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.section-header {
  padding: 1rem 1.25rem;
  background: #f7fafc;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.3s;
}

.section-header:hover {
  background: #edf2f7;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-number {
  font-weight: 600;
  color: #667eea;
  font-size: 1rem;
}

.section-name {
  font-weight: 500;
  color: #2d3748;
  font-size: 1.1rem;
}

.section-toggle {
  font-size: 1.5rem;
  color: #4a5568;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.subsection-list {
  padding: 1rem 1.25rem 1rem 3.5rem;
  background: white;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.subsection-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #f7fafc;
  border-radius: 8px;
  transition: all 0.3s;
}

.subsection-item:hover {
  background: #edf2f7;
  transform: translateX(4px);
}

.subsection-icon {
  font-size: 1.2rem;
}

.subsection-name {
  flex: 1;
  color: #4a5568;
  font-weight: 500;
}

.subsection-status {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9rem;
}

.status-completed {
  background: #48bb78;
  color: white;
}

.status-pending {
  background: #ed8936;
  color: white;
}

.status-locked {
  background: #cbd5e0;
  color: #4a5568;
}

.add-section-btn {
  margin-top: 1rem;
  padding: 0.875rem 1rem;
  background: #edf2f7;
  border: 2px dashed #cbd5e0;
  border-radius: 12px;
  color: #4a5568;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.add-section-btn:hover {
  background: #e2e8f0;
  border-color: #a0aec0;
}

.add-icon {
  font-size: 1.2rem;
}

/* Правая колонка - Рейтинг */
.course-rating {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.rating-header {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.rating-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.rating-icon {
  font-size: 1.5rem;
}

.rating-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rating-total {
  color: #718096;
  font-weight: 500;
}

.rating-list {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
  max-height: 500px;
}

.rating-item {
  display: grid;
  grid-template-columns: auto auto 1fr auto;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  transition: all 0.3s;
}

.rating-item:hover {
  background: #f7fafc;
}

.rating-item:last-child {
  border-bottom: none;
}

.student-rank {
  min-width: 36px;
}

.rank-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #edf2f7;
  color: #4a5568;
  font-weight: 700;
  font-size: 1rem;
}

.rank-gold {
  background: linear-gradient(135deg, #f6e05e, #d69e2e);
  color: white;
}

.rank-silver {
  background: linear-gradient(135deg, #a0aec0, #718096);
  color: white;
}

.rank-bronze {
  background: linear-gradient(135deg, #ed8936, #c05621);
  color: white;
}

.student-avatar {
  min-width: 40px;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.student-info {
  min-width: 0;
}

.student-name {
  font-weight: 500;
  color: #2d3748;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.student-group {
  font-size: 0.875rem;
  color: #718096;
}

.student-score {
  min-width: 120px;
  text-align: right;
}

.score-value {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.score-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.progress-text {
  font-size: 0.875rem;
  color: #718096;
  min-width: 40px;
}

/* Статистика курса */
.course-stats {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.stats-title {
  font-size: 1.25rem;
  color: #2d3748;
  font-weight: 600;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-item:hover {
  background: #edf2f7;
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 1.5rem;
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #718096;
}

/* Панель быстрых действий */
.quick-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e2e8f0;
}

.action-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 1rem;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #667eea;
  border-color: #667eea;
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
}

.action-btn:hover .action-icon,
.action-btn:hover .action-text {
  color: white;
}

.action-icon {
  font-size: 2rem;
  color: #667eea;
  transition: color 0.3s;
}

.action-text {
  font-weight: 500;
  color: #4a5568;
  transition: color 0.3s;
}

/* Адаптивность */
@media (max-width: 1200px) {
  .course-content {
    grid-template-columns: 1fr;
  }

  .course-rating {
    grid-column: 1;
  }
}

@media (max-width: 768px) {
  .course-detail-page {
    padding: 1rem;
  }

  .course-title {
    font-size: 2rem;
  }

  .course-meta {
    flex-direction: column;
    gap: 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions {
    flex-wrap: wrap;
  }

  .action-btn {
    flex: calc(50% - 0.5rem);
  }
}

@media (max-width: 480px) {
  .rating-item {
    grid-template-columns: auto 1fr;
    grid-template-rows: auto auto;
    gap: 0.5rem;
  }

  .student-score {
    grid-column: 2;
    grid-row: 2;
    text-align: left;
    margin-top: 0.5rem;
  }

  .quick-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}
</style>
