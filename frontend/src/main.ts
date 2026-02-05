// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createRouter, createWebHistory } from 'vue-router'

// 创建Vue应用
const app = createApp(App)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(ElementPlus)
app.use(router)

// 全局错误处理
// main.ts 修改
app.config.errorHandler = (err, instance, info) => {
  console.error('🚨 全局错误捕获:', err)
  console.log('📄 Vue实例:', instance)
  console.log('ℹ️ 错误信息:', info)

  // 可以在这里添加错误上报到服务器的逻辑
  if (err instanceof Error) {
    console.error('错误堆栈:', err.stack)

    // 显示友好的错误提示
    if (typeof window !== 'undefined' && window.alert) {
      // 在生产环境中，可以显示更友好的提示
      if (process.env.NODE_ENV === 'production') {
        alert('系统出现错误，请刷新页面重试或联系管理员。')
      }
    }
  }
}

// 添加未处理的Promise错误捕获
window.addEventListener('unhandledrejection', event => {
  console.error('🚨 未处理的Promise错误:', event.reason)
  event.preventDefault() // 阻止默认行为（控制台输出）
})



// 挂载应用
app.mount('#app')

console.log('🚀 Vue应用已启动')
console.log('📡 前端地址: http://localhost:5173')
console.log('🔗 后端地址: http://localhost:5000')
