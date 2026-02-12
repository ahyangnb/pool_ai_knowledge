import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/home/index.vue'),
  },
  {
    path: '/posts',
    name: 'Posts',
    component: () => import('../views/posts/index.vue'),
  },
  {
    path: '/posts/:id',
    name: 'PostDetail',
    component: () => import('../views/posts/detail.vue'),
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/chat/index.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
