import { createRouter, createWebHistory } from 'vue-router'


const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'login',
            component: () => import('@/views/Login.vue'),
        },
        {
            path: '/register',
            name: 'register',
            component: () => import('@/views/Register.vue'),
        },
        {
            path: '/chat',
            name: 'chatroom',
            component: () => import('@/views/Chatroom.vue'),
        },
        {
            path: '/api',
            name: 'api',
            component: () => import('@/components/SwaggerUI.vue'),
            props: { specUrl: '/api/swagger.json' },
        },
    ],
})

export default router
