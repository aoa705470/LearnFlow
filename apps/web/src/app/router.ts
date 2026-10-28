import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/features/home/HomeView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
  ],
})
