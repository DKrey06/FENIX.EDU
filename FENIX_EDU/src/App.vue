<template>
  <div id="app">
    <Header v-if="!isAuthPage" />
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Header from './components/Header.vue';

const route = useRoute();

const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register' || route.path === '/';
});
</script>

<style>
#app {
  min-height: 100vh;
  background: #f7fafc;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
  color: #2f4156;
}
</style>