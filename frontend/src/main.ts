import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { setupCalendar, DatePicker } from 'v-calendar';
import 'v-calendar/style.css';
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(createPinia()) // 挂载 Pinia
app.use(router)      // 挂载 Router
app.use(setupCalendar, {})
app.component('VDatePicker', DatePicker)
app.use(ElementPlus)
app.mount('#app')