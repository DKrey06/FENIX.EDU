<!-- src/pages/LandingPage.vue -->
<template>
    <div class="landing-page">
        <header class="header">
            <div class="logo">FENIX.EDU</div>
            <nav class="nav">
                <router-link to="/login" class="nav-link">Вход</router-link>
                <router-link to="/register" class="nav-link nav-link-primary">
                    Регистрация
                </router-link>
            </nav>
        </header>

        <main class="main-content">
            <div class="hero">
                <h1 class="hero-title">Добро пожаловать в FENIX.EDU</h1>
                <p class="hero-subtitle">
                    Современная образовательная платформа для студентов и преподавателей
                </p>
                <div class="hero-buttons">
                    <router-link to="/register" class="btn btn-primary">
                        Начать обучение
                    </router-link>
                    <router-link to="/login" class="btn btn-secondary">
                        Войти в аккаунт
                    </router-link>
                </div>
            </div>
        </main>
    </div>
</template>

<style scoped>
.landing-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #c8dae8 42%, #d3a5b1 69%);
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.logo {
    font-family: "Holtwood One SC", serif;
    font-size: 1.5rem;
    color: #2f4156;
    font-weight: 400;
}

.nav {
    display: flex;
    gap: 1.5rem;
}

.nav-link {
    padding: 0.5rem 1rem;
    text-decoration: none;
    color: #2f4156;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.3s;
}

.nav-link:hover {
    background: rgba(255, 255, 255, 0.2);
}

.nav-link-primary {
    background: #2f4156;
    color: white;
}

.nav-link-primary:hover {
    background: #1a2a3a;
}

.main-content {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 80px);
    padding: 2rem;
}

.hero {
    text-align: center;
    max-width: 800px;
}

.hero-title {
    font-size: 3rem;
    color: #2f4156;
    margin-bottom: 1rem;
    font-weight: 700;
}

.hero-subtitle {
    font-size: 1.25rem;
    color: #4a5568;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

.btn {
    padding: 0.875rem 2rem;
    border-radius: 10px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s;
    display: inline-block;
}

.btn-primary {
    background: #2f4156;
    color: white;
    border: 2px solid #2f4156;
}

.btn-primary:hover {
    background: #1a2a3a;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(47, 65, 86, 0.3);
}

.btn-secondary {
    background: transparent;
    color: #2f4156;
    border: 2px solid #2f4156;
}

.btn-secondary:hover {
    background: rgba(47, 65, 86, 0.1);
    transform: translateY(-2px);
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem;
    }

    .hero-buttons {
        flex-direction: column;
        align-items: center;
    }

    .btn {
        width: 100%;
        max-width: 300px;
        text-align: center;
    }
}
</style>