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
