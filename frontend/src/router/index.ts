import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: '文件上传'
    }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis.vue'),
    meta: {
      title: '分析报告'
    }
  },
  {
    path: '/analysis/:taskId',
    name: 'AnalysisDetail',
    component: () => import('@/views/AnalysisDetail.vue'),
    meta: {
      title: '分析详情'
    }
  },
  {
    path: '/analysis/:taskId/filter-details/:filterType',
    name: 'FilterDetail',
    component: () => import('@/views/FilterDetail.vue'),
    props: true,
    meta: {
      title: '过滤详情'
    }
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/Config.vue'),
    meta: {
      title: '配置管理'
    }
  },
  {
    path: '/system',
    name: 'System',
    component: () => import('@/views/System.vue'),
    meta: {
      title: '系统状态'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - Tineco聊天记录分析系统`
  }
  next()
})

export default router
