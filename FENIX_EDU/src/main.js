// main.js
import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Инициализируем хранилище auth
import { useAuthStore } from "./stores/auth";
const authStore = useAuthStore();
authStore.init();

app.mount("#app");
