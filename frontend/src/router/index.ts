// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import UploadView from '../views/UploadView.vue'
import HistoryView from '../views/HistoryView.vue'
import RecordDetailView from '../views/RecordDetailView.vue'
import AboutView from '../views/AboutView.vue'
import VideoDetectView from '../views/VideoDetect.vue' // 新增

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  { path: '/upload', component: UploadView },
  { path: '/history', component: HistoryView },
  { path: '/record/:id', component: RecordDetailView },
  { path: '/about', component: AboutView },
  { path: '/video', component: VideoDetectView, meta: { title: '视频检测' } } // 新增
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 绝缘子缺陷检测系统`
  } else {
    document.title = '绝缘子缺陷检测系统'
  }
  next()
})

export default router
