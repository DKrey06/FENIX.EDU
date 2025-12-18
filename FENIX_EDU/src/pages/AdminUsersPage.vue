<template>
    <div class="admin-users-page">
        <div class="page-header">
            <h1>Управление пользователями</h1>
            <p>Подтверждение учетных записей пользователей</p>
        </div>

        <div class="filters">
            <div class="filter-group">
                <label>Статус:</label>
                <select v-model="filters.status" @change="loadUsers">
                    <option value="">Все</option>
                    <option value="pending">Ожидают подтверждения</option>
                    <option value="active">Активные</option>
                    <option value="rejected">Отклоненные</option>
                </select>
            </div>

            <div class="filter-group">
                <label>Роль:</label>
                <select v-model="filters.role" @change="loadUsers">
                    <option value="">Все</option>
                    <option value="student">Студенты</option>
                    <option value="teacher">Преподаватели</option>
                </select>
            </div>
        </div>

        <div class="users-table">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>ФИО</th>
                        <th>Email</th>
                        <th>Роль</th>
                        <th>Курс/Группа</th>
                        <th>Статус</th>
                        <th>Дата регистрации</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in users" :key="user.id">
                        <td>{{ user.id }}</td>
                        <td>{{ user.full_name }}</td>
                        <td>{{ user.email }}</td>
                        <td>
                            <span class="role-badge" :class="user.role">
                                {{ getRoleLabel(user.role) }}
                            </span>
                        </td>
                        <td>
                            <span v-if="user.course">{{ user.course }} курс</span>
                            <span v-if="user.group">, {{ user.group }}</span>
                        </td>
                        <td>
                            <span class="status-badge" :class="user.status">
                                {{ getStatusLabel(user.status) }}
                            </span>
                        </td>
                        <td>{{ formatDate(user.created_at) }}</td>
                        <td class="actions">
                            <button v-if="user.status === 'pending'" @click="approveUser(user.id)" class="btn-approve">
                                Подтвердить
                            </button>
                            <button v-if="user.status === 'pending'" @click="rejectUser(user.id)" class="btn-reject">
                                Отклонить
                            </button>
                            <button v-if="user.status === 'active'" @click="blockUser(user.id)" class="btn-block">
                                Заблокировать
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div v-if="users.length === 0" class="empty-state">
                <p>Нет пользователей для отображения</p>
            </div>
        </div>

        <div class="pagination" v-if="totalPages > 1">
            <button @click="prevPage" :disabled="currentPage === 1">
                ←
            </button>
            <span>Страница {{ currentPage }} из {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage === totalPages">
                →
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const users = ref([])
const filters = ref({
    status: '',
    role: ''
})
const currentPage = ref(1)
const totalPages = ref(1)
const totalUsers = ref(0)

const loadUsers = async () => {
    try {
        const response = await authStore.fetchAdminUsers({
            page: currentPage.value,
            ...filters.value
        })

        users.value = response.users
        totalPages.value = response.pages
        totalUsers.value = response.total
    } catch (error) {
        console.error('Ошибка загрузки пользователей:', error)
    }
}

const approveUser = async (userId) => {
    try {
        await authStore.updateUserStatus(userId, 'active')
        await loadUsers()
    } catch (error) {
        console.error('Ошибка подтверждения:', error)
    }
}

const rejectUser = async (userId) => {
    try {
        await authStore.updateUserStatus(userId, 'rejected')
        await loadUsers()
    } catch (error) {
        console.error('Ошибка отклонения:', error)
    }
}

const blockUser = async (userId) => {
    try {
        await authStore.updateUserStatus(userId, 'blocked')
        await loadUsers()
    } catch (error) {
        console.error('Ошибка блокировки:', error)
    }
}

const prevPage = () => {
    if (currentPage.value > 1) {
        currentPage.value--
        loadUsers()
    }
}

const nextPage = () => {
    if (currentPage.value < totalPages.value) {
        currentPage.value++
        loadUsers()
    }
}

const getRoleLabel = (role) => {
    const labels = {
        student: 'Студент',
        teacher: 'Преподаватель',
        department_head: 'Зав. кафедрой',
        admin: 'Администратор'
    }
    return labels[role] || role
}

const getStatusLabel = (status) => {
    const labels = {
        pending: 'Ожидает',
        active: 'Активен',
        rejected: 'Отклонен',
        blocked: 'Заблокирован'
    }
    return labels[status] || status
}

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU')
}

onMounted(() => {
    loadUsers()
})
</script>

<style scoped>
.admin-users-page {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.page-header {
    margin-bottom: 2rem;
}

.filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.users-table {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
}

th {
    background: #f7fafc;
    font-weight: 600;
}

.role-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
}

.role-badge.student {
    background: #bee3f8;
    color: #2c5282;
}

.role-badge.teacher {
    background: #c6f6d5;
    color: #22543d;
}

.status-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
}

.status-badge.pending {
    background: #fefcbf;
    color: #744210;
}

.status-badge.active {
    background: #c6f6d5;
    color: #22543d;
}

.status-badge.rejected {
    background: #fed7d7;
    color: #742a2a;
}

.actions {
    display: flex;
    gap: 0.5rem;
}

.btn-approve {
    background: #48bb78;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn-reject {
    background: #f56565;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn-block {
    background: #718096;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 2rem;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: #718096;
}
</style>