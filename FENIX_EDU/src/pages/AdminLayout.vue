<template>
    <div class="admin-layout">
        <!-- Хедер админ-панели -->
        <header class="admin-header">
            <div class="header-left">
                <h1 class="logo">FENIX.EDU</h1>
                <div class="admin-info">
                    <span class="admin-role">Администратор системы</span>
                    <span class="admin-name">{{ userName }}</span>
                </div>
            </div>
            <div class="header-right">
                <button @click="goToDashboard" class="btn-dashboard">
                    ← Вернуться на сайт
                </button>
            </div>
        </header>

        <div class="admin-container">
            <!-- Боковое меню -->
            <aside class="admin-sidebar">
                <nav class="admin-nav">
                    <router-link to="/admin/users" class="nav-item" :class="{ active: $route.path === '/admin/users' }">
                        <span class="nav-icon">👥</span>
                        <span class="nav-text">Пользователи</span>
                        <span v-if="pendingCount > 0" class="badge">{{ pendingCount }}</span>
                    </router-link>
                    <router-link to="/admin/courses" class="nav-item">
                        <span class="nav-icon">📚</span>
                        <span class="nav-text">Курсы</span>
                    </router-link>
                    <router-link to="/admin/statistics" class="nav-item">
                        <span class="nav-icon">📊</span>
                        <span class="nav-text">Статистика</span>
                    </router-link>
                    <router-link to="/admin/settings" class="nav-item">
                        <span class="nav-icon">⚙️</span>
                        <span class="nav-text">Настройки</span>
                    </router-link>
                </nav>
            </aside>

            <!-- Основной контент -->
            <main class="admin-main">
                <router-view />
            </main>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const pendingCount = ref(0);

const userName = computed(() => {
    return authStore.user?.full_name || 'Admin';
});

const goToDashboard = () => {
    router.push('/dashboard');
};

const loadPendingCount = async () => {
    try {
        const data = await authStore.fetchPendingUsers({ limit: 1 });
        pendingCount.value = data.total || 0;
    } catch (error) {
        console.error('Ошибка загрузки количества ожидающих:', error);
    }
};

onMounted(() => {
    if (authStore.isAdmin) {
        loadPendingCount();
    }
});
</script>

<style scoped>
.admin-layout {
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.admin-header {
    background: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    border-bottom: 3px solid #2f4156;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.logo {
    font-family: 'Holtwood One SC', serif;
    font-size: 1.5rem;
    color: #2f4156;
    margin: 0;
    padding: 0.5rem 1rem;
    background: #f5d6d8;
    border-radius: 12px;
}

.admin-info {
    display: flex;
    flex-direction: column;
}

.admin-role {
    font-size: 0.875rem;
    color: #718096;
    font-weight: 500;
}

.admin-name {
    font-size: 1.125rem;
    color: #2f4156;
    font-weight: 600;
}

.btn-dashboard {
    padding: 0.5rem 1rem;
    background: #2f4156;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.3s;
}

.btn-dashboard:hover {
    background: #1a2a3a;
}

.admin-container {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 0;
    min-height: calc(100vh - 80px);
}

.admin-sidebar {
    background: white;
    border-right: 1px solid #e2e8f0;
    padding: 1.5rem 0;
}

.admin-nav {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0 1rem;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.875rem 1rem;
    text-decoration: none;
    color: #4a5568;
    border-radius: 8px;
    transition: all 0.3s;
    position: relative;
}

.nav-item:hover {
    background: #f7fafc;
    color: #2f4156;
}

.nav-item.active {
    background: #2f4156;
    color: white;
}

.nav-icon {
    font-size: 1.25rem;
}

.nav-text {
    font-size: 0.95rem;
    font-weight: 500;
    flex: 1;
}

.badge {
    background: #f56565;
    color: white;
    border-radius: 10px;
    padding: 0.1rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
}

.admin-main {
    padding: 2rem;
    background: #f7fafc;
    overflow-y: auto;
}
</style>