import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
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
