<template>
  <div class="about-container">
    <!-- 返回按钮 - 固定在右上角 -->
    <div class="floating-nav">
      <el-button
        @click="goToHome"
        type="primary"
        size="large"
        class="home-btn"
        round
      >
        <el-icon><HomeFilled /></el-icon>
        返回首页
      </el-button>
    </div>
    <!-- 顶部标题区域 -->
    <div class="header-section">
      <div class="title-wrapper">
        <h1 class="system-title">
          <span class="title-text">绝缘子缺陷检测系统</span>
          <span class="title-badge">AI-Powered</span>
        </h1>
        <p class="subtitle">基于深度学习的电力设备智能检测解决方案</p>
      </div>
      <div class="header-decoration">
        <div class="circuit-line"></div>
        <div class="circuit-node"></div>
      </div>
    </div>

    <!-- 系统简介卡片 -->
    <div class="card info-card">
      <div class="card-header">
        <div class="icon-wrapper">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M19.5 12h-15m7.5-7.5v15m-7.5-7.5h15" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <h2 class="card-title">系统简介</h2>
      </div>
      <div class="card-body">
        <p class="description">
          本系统基于先进的 YOLOv11 深度学习架构，专为电力行业绝缘子表面缺陷自动化识别而设计。
          通过计算机视觉技术，系统能够精准检测绝缘子类型以及污秽、破损、锈蚀等常见缺陷，为电力设备维护提供
          智能化决策支持。系统具备实时参数调整、多格式数据导出和检测历史追溯等核心功能。
        </p>
        <div class="tech-tags">
          <span class="tech-tag">YOLOv11</span>
          <span class="tech-tag">计算机视觉</span>
          <span class="tech-tag">深度学习</span>
          <span class="tech-tag">实时检测</span>
        </div>
      </div>
    </div>

    <!-- 功能特性网格 -->
    <div class="card features-card">
      <div class="card-header">
        <div class="icon-wrapper">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" stroke-width="2"/>
          </svg>
        </div>
        <h2 class="card-title">核心功能</h2>
      </div>
      <div class="features-grid">
        <div class="feature-item" v-for="feature in features" :key="feature.id">
          <div class="feature-icon" :style="{ backgroundColor: feature.color + '15' }">
            <svg class="feature-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path :d="feature.icon" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="feature-content">
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 联系方式卡片 -->
    <div class="card contact-card">
      <div class="card-header">
        <div class="icon-wrapper">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" stroke-width="2"/>
          </svg>
        </div>
        <h2 class="card-title">联系</h2>
      </div>
      <div class="contact-content">
        <div class="developer-info">
          <div class="avatar">W</div>
          <div class="developer-details">
            <h3 class="developer-name">吴权彬</h3>
            <p class="developer-title">系统开发者</p>
          </div>
        </div>

        <div class="contact-methods">
          <div class="contact-item">
            <div class="contact-icon phone">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" stroke-width="2"/>
              </svg>
            </div>
            <div class="contact-details">
              <p class="contact-label">联系电话</p>
              <p class="contact-value">19303010517</p>
            </div>
          </div>

          <div class="contact-item">
            <div class="contact-icon email">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" stroke-width="2"/>
              </svg>
            </div>
            <div class="contact-details">
              <p class="contact-label">电子邮箱</p>
              <p class="contact-value">1597338110@qq.com</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统信息底部栏 -->
    <div class="footer-info">
      <p class="version">系统版本 v1.1.0 | 基于 Vue 3 + YOLOv11</p>
      <p class="copyright">© 2026 绝缘子缺陷检测系统 - 智能检测</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { HomeFilled } from '@element-plus/icons-vue'

const router = useRouter()

// 返回首页功能
const goToHome = () => {
  router.push('/upload') // 假设首页路由为 '/'
  // 如果没有使用Vue Router，可以使用以下方式：
  // window.location.href = '/'
  // 或者触发自定义事件
  // emit('go-home')
}

const features = ref([
  {
    id: 1,
    title: '多模型支持',
    description: '兼容多种YOLO模型格式，支持多种预训练模型',
    icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
    color: '#3b82f6'
  },
  {
    id: 2,
    title: '智能参数调整',
    description: '实时调整置信度与IoU阈值，优化检测精度与召回率',
    icon: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4',
    color: '#10b981'
  },
  {
    id: 3,
    title: '历史记录管理',
    description: '自动保存检测记录，支持按时间、类型筛选与查看',
    icon: 'M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.773-.118m-3.75 0a48.424 48.424 0 01-1.773.118A2.25 2.25 0 005.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z',
    color: '#8b5cf6'
  },
  {
    id: 4,
    title: '可视化对比',
    description: '原始图像与检测结果同屏对比展示，直观呈现检测效果',
    icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7',
    color: '#f59e0b'
  },
  {
    id: 5,
    title: '数据导出',
    description: '支持检测结果导出为Excel/XLSX/PDF格式，便于数据分析与报告生成',
    icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: '#ef4444'
  }
])

</script>
<style scoped>
/* 悬浮导航按钮 */
.floating-nav {
  position: fixed;
  top: 50px;
  right: 50px;
  z-index: 1000;
  animation: slideInRight 0.5s ease-out;
}

.home-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.home-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.home-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3);
}

.home-btn .el-icon {
  margin-right: 8px;
  font-size: 1.1em;
}

/* 动画效果 */
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .floating-nav {
    top: 16px;
    right: 16px;
  }

  .home-btn {
    padding: 10px 18px;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .floating-nav {
    top: 12px;
    right: 12px;
  }

  .home-btn {
    padding: 8px 16px;
    font-size: 0.85rem;
  }

  .home-btn .el-icon {
    margin-right: 6px;
  }
}

/* 如果需要更突出的效果，可以添加脉冲动画 */
@keyframes pulse {
  0% {
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
  }
  50% {
    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.5);
  }
  100% {
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
  }
}

.home-btn.pulse {
  animation: pulse 2s infinite;
}

.about-container {
  padding: 0;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 头部区域 */
.header-section {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}

.title-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.system-title {
  font-size: 2.8rem;
  font-weight: 800;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.title-text {
  background: linear-gradient(90deg, #60a5fa 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-badge {
  background: rgba(255, 255, 255, 0.15);
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 1rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.subtitle {
  font-size: 1.2rem;
  color: #cbd5e1;
  margin-bottom: 0;
  max-width: 600px;
}

.nav-menu {
  display: flex;
  gap: 15px;
  align-items: center;
}

.header-decoration {
  position: absolute;
  right: 20px;
  bottom: 20px;
  z-index: 1;
}

.circuit-line {
  width: 200px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.6));
  transform: rotate(45deg);
  transform-origin: right bottom;
}

.circuit-node {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 12px;
  height: 12px;
  background: #60a5fa;
  border-radius: 50%;
  box-shadow: 0 0 20px #60a5fa;
}

/* 卡片通用样式 */
.card {
  max-width: 1200px;
  margin: 30px auto;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.8);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 32px;
  background: linear-gradient(90deg, #f8fafc 0%, white 100%);
  border-bottom: 1px solid #f1f5f9;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon {
  width: 24px;
  height: 24px;
  color: white;
}

.card-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

/* 简介卡片 */
.info-card .card-body {
  padding: 32px;
}

.description {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #475569;
  margin-bottom: 24px;
}

.tech-tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.tech-tag {
  background: #f1f5f9;
  color: #475569;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.tech-tag:hover {
  background: #3b82f6;
  color: white;
  transform: translateY(-2px);
}

/* 功能卡片 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  padding: 0 32px 32px;
}

.feature-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.feature-item:hover {
  background: white;
  border-color: #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-svg {
  width: 24px;
  height: 24px;
  color: inherit;
}

.feature-content {
  flex: 1;
}

.feature-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.feature-desc {
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.5;
  margin: 0;
}

/* 联系方式卡片 */
.contact-content {
  padding: 32px;
}

.developer-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f1f5f9;
}

.avatar {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.8rem;
  font-weight: 700;
}

.developer-details {
  flex: 1;
}

.developer-name {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.developer-title {
  color: #64748b;
  margin: 0;
}

.contact-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.contact-item:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.contact-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.contact-icon.phone {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.contact-icon.email {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.contact-icon svg {
  width: 20px;
  height: 20px;
}

.contact-details {
  flex: 1;
}

.contact-label {
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 4px;
}

.contact-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

/* 底部信息 */
.footer-info {
  text-align: center;
  padding: 30px 20px;
  color: #64748b;
  font-size: 0.9rem;
  max-width: 1200px;
  margin: 0 auto;
}

.version {
  font-weight: 600;
  margin-bottom: 8px;
}

.copyright {
  margin: 0;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .system-title {
    font-size: 2rem;
    flex-direction: column;
    align-items: flex-start;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .contact-methods {
    grid-template-columns: 1fr;
  }

  .card-header {
    padding: 20px;
  }

  .card-body,
  .contact-content {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .header-section {
    padding: 30px 16px;
  }

  .system-title {
    font-size: 1.8rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .card {
    margin: 20px 16px;
  }
}
</style>
