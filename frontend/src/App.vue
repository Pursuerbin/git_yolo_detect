<!-- src/App.vue -->
<template>
    <!-- 主内容区域 -->
    <main class="main-content">
      <RouterView />
    </main>

</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 响应式数据
const username = ref('admin') // 可以从登录状态获取
const isLoggedIn = ref(true) // 可以从登录状态获取

// 计算属性
const showNav = computed(() => {
  // 登录和注册页面不显示导航栏
  return !['/login', '/register'].includes(route.path)
})

const showFooter = computed(() => {
  // 登录和注册页面不显示页脚
  return !['/login', '/register'].includes(route.path)
})

// 方法
const logout = () => {
  isLoggedIn.value = false
  username.value = ''
  router.push('/login')
}

// 监听路由变化
watch(() => route.path, (newPath) => {
  // 这里可以添加路由变化时的逻辑
  console.log('路由变化:', newPath)
})
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 导航栏样式 */
.main-nav {
  background: linear-gradient(135deg, #1e3c72, #2a5298);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.nav-brand h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
  font-weight: 500;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: bold;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logout-btn {
  padding: 6px 12px;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #dc2626;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 20px;
}

/* 页脚样式 */
.main-footer {
  background-color: #2d3748;
  color: white;
  padding: 20px 0;
  margin-top: auto;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  text-align: center;
}

.footer-container p {
  margin: 5px 0;
  color: #cbd5e0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    height: auto;
    padding: 15px 20px;
  }

  .nav-brand {
    margin-bottom: 15px;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 15px;
  }

  .nav-user {
    flex-direction: column;
    gap: 10px;
  }

  .main-content {
    padding: 15px;
  }
}
</style>
