import { createApp } from 'vue'
import './style.css' // 如果报错，可删除这行
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

const app = createApp(App)

app.use(createPinia()) // 挂载 Pinia
app.use(router)      // 挂载 Router

app.mount('#app')