import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/redirect',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '/redirect/:path(.*)',
        component: () => import('@/views/redirect/index')
      }
    ]
  },
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/auth-redirect',
    component: () => import('@/views/login/auth-redirect'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error-page/404'),
    hidden: true
  },
  {
    path: '/401',
    component: () => import('@/views/error-page/401'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        component: () => import('@/views/coming-soon/index'),
        name: 'Dashboard',
        meta: { title: '面板信息', icon: 'dashboard', affix: true }
      }
    ]
  },
  {
    path: '/post',
    component: Layout,
    redirect: '/post/list',
    name: 'Post',
    meta: { title: '帖子管理', icon: 'el-icon-s-management' },
    children: [
      {
        path: 'list',
        component: () => import('@/views/post/list'),
        name: 'PostList',
        meta: { title: '帖子列表', icon: 'list' }
      },
      {
        path: 'create',
        component: () => import('@/views/post/create'),
        name: 'CreatePost',
        hidden: true,
        meta: { title: '新增帖子', activeMenu: '/post/list' }
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/post/edit'),
        name: 'EditPost',
        hidden: true,
        meta: { title: '编辑帖子', noCache: true, activeMenu: '/post/list' }
      }
    ]
  },
  {
    path: '/settings',
    component: Layout,
    children: [
      {
        path: 'index',
        component: () => import('@/views/coming-soon/index'),
        name: 'Settings',
        meta: { title: '系统设置', icon: 'el-icon-setting' }
      }
    ]
  },
  {
    path: '/profile',
    component: Layout,
    redirect: '/profile/index',
    hidden: true,
    children: [
      {
        path: 'index',
        component: () => import('@/views/profile/index'),
        name: 'Profile',
        meta: { title: 'Profile', icon: 'user', noCache: true }
      }
    ]
  }
]

/**
 * asyncRoutes
 * the routes that need to be dynamically loaded based on user roles
 */
export const asyncRoutes = [
  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
