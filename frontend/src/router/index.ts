import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/AdminLoginView.vue')
    },
    {
      path: '/admin/events',
      name: 'admin-events',
      component: () => import('@/views/AdminEventsView.vue')
    },
    {
      path: '/admin/events/:id',
      name: 'admin-event-detail',
      component: () => import('@/views/AdminEventDetailView.vue')
    },
    {
      path: '/event/:eventCode',
      name: 'event',
      component: () => import('@/views/EventView.vue')
    },
    {
      path: '/print',
      name: 'print',
      component: () => import('@/views/PrintView.vue')
    }
  ]
})

export default router
