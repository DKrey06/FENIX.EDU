<template>
    <div class="admin-page-container">
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
                        <option value="blocked">Заблокированные</option>
                    </select>
                </div>

                <div class="filter-group">
                    <label>Роль:</label>
                    <select v-model="filters.role" @change="loadUsers">
                        <option value="">Все</option>
                        <option value="student">Студенты</option>
                        <option value="teacher">Преподаватели</option>
                        <option value="department_head">Зав. кафедрой</option>
                        <option value="admin">Администраторы</option>
                    </select>
                </div>

                <div class="filter-group">
                    <button class="btn-reset" @click="resetFilters">Сбросить фильтры</button>
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
                                <button v-if="user.status === 'pending'" @click="approveUser(user.id)"
                                    class="btn-approve">
                                    Подтвердить
                                </button>
                                <button v-if="user.status === 'pending'" @click="rejectUser(user.id)"
                                    class="btn-reject">
                                    Отклонить
                                </button>
                                <button v-if="user.status === 'active'" @click="blockUser(user.id)" class="btn-block">
                                    Заблокировать
                                </button>
                                <button v-if="user.status === 'active' && user.role === 'teacher'"@click="promoteToDepartmentHead(user.id)" class="btn-promote">
                                    Сделать зав. кафедрой 
                                </button>
                                <button v-if="user.status === 'blocked'" @click="unblockUser(user.id)"
                                    class="btn-unblock">
                                    Разблокировать
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

            <div class="summary" v-if="totalUsers > 0">
                <p>Всего пользователей: {{ totalUsers }}</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const users = ref([])
const filters = ref({
    status: '',
    role: ''
})
const currentPage = ref(1)
const totalPages = ref(1)
const totalUsers = ref(0)
const isLoading = ref(false)

const loadUsers = async () => {
    try {
        isLoading.value = true;

        // Очищаем пустые параметры фильтров
        const cleanFilters = {};
        if (filters.value.status) {
            cleanFilters.status = filters.value.status;
        }
        if (filters.value.role) {
            cleanFilters.role = filters.value.role;
        }

        const response = await authStore.fetchAdminUsers({
            page: currentPage.value,
            ...cleanFilters
        });

        users.value = response.users || [];
        totalPages.value = response.pages || 1;
        totalUsers.value = response.total || 0;

    } catch (error) {
        console.error('Ошибка загрузки пользователей:', error);
        users.value = [];
        totalPages.value = 1;
        totalUsers.value = 0;
    } finally {
        isLoading.value = false;
    }
}

// Добавляем watch для отслеживания изменений фильтров
watch(filters, () => {
    // При изменении фильтров сбрасываем на первую страницу
    currentPage.value = 1;
    loadUsers();
}, { deep: true });

const approveUser = async (userId) => {
    try {
        await authStore.approveUser(userId);
        await loadUsers();
    } catch (error) {
        console.error('Ошибка подтверждения:', error);
    }
};

const rejectUser = async (userId) => {
    try {
        await authStore.rejectUser(userId);
        await loadUsers();
    } catch (error) {
        console.error('Ошибка отклонения:', error);
    }
};

const blockUser = async (userId) => {
    try {
        await authStore.updateUserStatus(userId, 'blocked');
        await loadUsers();
    } catch (error) {
        console.error('Ошибка блокировки:', error);
    }
}

const promoteToDepartmentHead = async (userId) => {
    try {
    await authStore.promoteTeacherToDepartmentHead(userId);
    await loadUsers(); 
    } catch (error) {
    console.error("Ошибка повышения до зав. кафедры:", error);
    }
};


const unblockUser = async (userId) => {
    try {
        await authStore.updateUserStatus(userId, 'active');
        await loadUsers();
    } catch (error) {
        console.error('Ошибка разблокировки:', error);
    }
}

const resetFilters = () => {
    filters.value = {
        status: '',
        role: ''
    };
    currentPage.value = 1;
}

const prevPage = () => {
    if (currentPage.value > 1) {
        currentPage.value--;
        loadUsers();
    }
}

const nextPage = () => {
    if (currentPage.value < totalPages.value) {
        currentPage.value++;
        loadUsers();
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
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('ru-RU')
}

onMounted(() => {
    loadUsers()
})
</script>
<style scoped>
.admin-page-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.admin-users-page {
    max-width: 1200px;
    margin: 0 auto;
}
.btn-promote {
    background: #2d6cdf;
    color: white;
    border: none;
    padding: 8px 10px;
    border-radius: 8px;
    cursor: pointer;
    margin-left: 6px;
}
.btn-promote:hover {
    opacity: 0.9;
}

.page-header {
    margin-bottom: 2rem;
    text-align: center;
}

.page-header h1 {
    font-size: 2rem;
    color: #2f4156;
    margin-bottom: 0.5rem;
}

.page-header p {
    color: #718096;
    font-size: 1rem;
}

.filters {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
    align-items: flex-end;
    flex-wrap: wrap;
    padding: 1.5rem;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 200px;
}

.filter-group label {
    font-weight: 600;
    color: #4a5568;
    font-size: 0.9rem;
}

.filter-group select {
    padding: 0.5rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.95rem;
    color: #2f4156;
    background: white;
    cursor: pointer;
    transition: border-color 0.3s;
}

.filter-group select:focus {
    outline: none;
    border-color: #667eea;
}

.btn-reset {
    padding: 0.5rem 1.5rem;
    background: #718096;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.3s;
}

.btn-reset:hover {
    background: #4a5568;
}

.users-table {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 1000px;
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
    color: #4a5568;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

tbody tr:hover {
    background: #f7fafc;
}

.role-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 500;
    display: inline-block;
}

.role-badge.student {
    background: #bee3f8;
    color: #2c5282;
}

.role-badge.teacher {
    background: #c6f6d5;
    color: #22543d;
}

.role-badge.department_head {
    background: #e9d8fd;
    color: #553c9a;
}

.role-badge.admin {
    background: #fed7d7;
    color: #742a2a;
}

.status-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 500;
    display: inline-block;
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

.status-badge.blocked {
    background: #cbd5e0;
    color: #2d3748;
}

.actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.btn-approve {
    background: #48bb78;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: background 0.3s;
    white-space: nowrap;
}

.btn-approve:hover {
    background: #38a169;
}

.btn-reject {
    background: #f56565;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: background 0.3s;
    white-space: nowrap;
}

.btn-reject:hover {
    background: #e53e3e;
}

.btn-block {
    background: #718096;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: background 0.3s;
    white-space: nowrap;
}

.btn-block:hover {
    background: #4a5568;
}

.btn-unblock {
    background: #4299e1;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: background 0.3s;
    white-space: nowrap;
}

.btn-unblock:hover {
    background: #3182ce;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 2rem;
    padding: 1rem;
    background: #f7fafc;
    border-radius: 8px;
}

.pagination button {
    padding: 0.5rem 1rem;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s;
    font-weight: 500;
}

.pagination button:hover:not(:disabled) {
    background: #2f4156;
    color: white;
    border-color: #2f4156;
}

.pagination button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination span {
    font-weight: 500;
    color: #4a5568;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: #718096;
    font-size: 1.1rem;
}

.empty-state p {
    margin: 0;
}

.summary {
    margin-top: 1.5rem;
    text-align: center;
    padding: 1rem;
    background: #f7fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

.summary p {
    margin: 0;
    font-weight: 500;
    color: #4a5568;
}

/* Индикатор загрузки */
.loading-indicator {
    text-align: center;
    padding: 2rem;
    color: #718096;
}

@media (max-width: 768px) {
    .filters {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }

    .filter-group {
        min-width: auto;
    }

    .actions {
        flex-direction: column;
    }

    .actions button {
        width: 100%;
    }
}
</style>