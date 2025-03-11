import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import messageInstance from './utils/message'

const app = createApp(App)

app.use(router)
app.use(messageInstance)
app.mount('#app')
