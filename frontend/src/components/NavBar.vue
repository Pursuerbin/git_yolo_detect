<template>
  <div class="top-nav">
    <div class="nav-brand">
      <h1>
        <span class="icon-wrapper">🔌</span>
        <span class="title-text">绝缘子缺陷检测系统</span>
      </h1>
      <p class="subtitle">基于YOLOv11的智能检测平台</p>
    </div>
    <div class="nav-menu">
      <el-button @click="goToHome" type="primary" size="large" class="nav-btn">
        <el-icon><Picture /></el-icon>
        图片检测
      </el-button>
      <el-button @click="goToVideo" type="primary" size="large" class="nav-btn">
        <el-icon><VideoCamera /></el-icon>
        视频检测
      </el-button>
      <el-button @click="goToHistory" type="info" size="large" class="nav-btn">
        <el-icon><Histogram /></el-icon>
        历史记录
      </el-button>
      <el-button @click="goToAbout" type="info" size="large" class="nav-btn">
        <el-icon><InfoFilled /></el-icon>
        关于系统
      </el-button>
      <el-button @click="logout" type="warning" size="large" class="nav-btn">
        <el-icon><SwitchButton /></el-icon>
        退出登录
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const router = useRouter()

const goToHome = () => router.push('/upload')
const goToVideo = () => router.push('/video')
const goToHistory = () => router.push('/history')
const goToAbout = () => router.push('/about')
const logout = () => router.push('/login')
</script>

<style scoped>
.top-nav {
  background: linear-gradient(135deg, #1e3c72, #2a5298);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 15px 20px;
  margin-bottom: 20px;
}

.nav-brand {
  margin-bottom: 10px;
}

.nav-brand h1 {
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 0 0 5px 0;
  font-size: 24px;
  font-weight: 700;
}

.icon-wrapper {
  font-size: 32px;
}

.title-text {
  flex: 1;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.nav-menu {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.nav-btn {
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .top-nav {
    padding: 10px 15px;
  }
  
  .nav-brand h1 {
    font-size: 20px;
  }
  
  .icon-wrapper {
    font-size: 24px;
  }
  
  .nav-menu {
    justify-content: center;
  }
  
  .nav-btn {
    size: medium;
  }
}
</style>