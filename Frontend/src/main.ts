import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import messageInstance from './utils/message'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(router)
app.use(messageInstance)
app.use(ElementPlus)
app.mount('#app')
