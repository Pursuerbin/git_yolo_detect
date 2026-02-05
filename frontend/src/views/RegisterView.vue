<template>
  <div class="login-container">
    <div class="login-card">
      <div class="header">
        <div class="logo">
          <div class="logo-icon">⚡</div>
          <h2>绝缘子缺陷检测系统</h2>
        </div>
          <p>基于视觉算法的智能检测平台</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label for="username">
            <i class="icon-user"></i>
            用户名
          </label>
          <input
            v-model="username"
            type="text"
            id="username"
            placeholder="请输入用户名"
            required
          />
        </div>

        <div class="input-group">
          <label for="password">
            <i class="icon-lock"></i>
            密码
          </label>
          <input
            v-model="password"
            type="password"
            id="password"
            placeholder="请输入密码"
            required
          />
        </div>

        <div class="options">
          <label class="remember">
            <input type="checkbox" v-model="rememberMe">
            记住我
          </label>
          <button type="button" @click="showForgotPassword" class="forgot-btn">
            忘记密码？
          </button>
        </div>

        <button
          type="submit"
          class="login-btn"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '登录中...' : '登录系统' }}
        </button>

        <div class="divider">
          <span>或</span>
        </div>

        <button type="button" @click="useDemoAccount" class="demo-btn">
          使用演示账号登录
        </button>
      </form>

      <div class="footer">
        <p>还没有账号？</p>
        <button @click="goToRegister" class="register-link-btn">
          创建新账户
        </button>
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="system-info">
      <p>技术支持：吴权彬 | 版本：v1.0</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 在顶部导入
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { logger } from '@/utils/logger'

const router = useRouter()
const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const perfStartTime = ref(Date.now())


// 动态获取后端URL（优化版）
const getBackendUrl = () => {
  const { protocol, hostname } = window.location
  const port = 5000

  logger.debug('获取后端URL', { hostname, protocol, port })

  // 本地开发环境
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    logger.debug('使用本地后端地址')
    return `http://localhost:${port}`
  }

  // 判断是否为内网IP（192.168.x.x, 10.x.x.x, 172.16.x.x-172.31.x.x）
  const isPrivateIP = /^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)/.test(hostname)

  if (isPrivateIP) {
    logger.debug('使用内网后端地址', { hostname })
    return `${protocol}//${hostname}:${port}`
  }

  // 公网环境
  logger.debug('使用公网后端地址', { hostname })
  return `${protocol}//${hostname}:${port}`
}

const backendUrl = getBackendUrl()

// 登录处理函数（带完整日志）
async function handleLogin() {
  const startTime = Date.now()
  const loginData = {
    username: username.value,
    password: password.value ? '***' : '', // 隐藏密码
    rememberMe: rememberMe.value
  }

  logger.action('login_attempt', loginData)

  if (!username.value || !password.value) {
    logger.warn('登录验证失败：用户名或密码为空', loginData)
    alert('请输入用户名和密码')
    return
  }

  loading.value = true
  logger.debug('开始登录请求', { backendUrl })

  try {
    logger.info('发送登录API请求', {
      url: `${backendUrl}/api/login`,
      username: username.value
    })

    const res = await axios.post(`${backendUrl}/api/login`, {
      username: username.value,
      password: password.value
    }, {
      timeout: 10000, // 10秒超时
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
      }
    })

    const responseTime = Date.now() - startTime
    logger.debug('收到登录响应', {
      success: res.data.success,
      responseTime: `${responseTime}ms`
    })

    if (res.data.success) {
      logger.info('登录成功', {
        username: username.value,
        responseTime: `${responseTime}ms`
      })

      if (rememberMe.value) {
        try {
          localStorage.setItem('rememberedUser', username.value)
          logger.debug('保存记住我状态到localStorage')
        } catch (storageError) {
          logger.warn('localStorage存储失败，可能已满', { error: storageError })
        }
      }

      // 记录成功登录后的跳转
      setTimeout(() => {
        logger.action('login_success_redirect', { to: '/upload' })
        router.push('/upload')
      }, 800)

    } else {
      logger.warn('登录失败（服务器返回）', {
        message: res.data.message,
        username: username.value
      })
      alert(res.data.message)
    }

  } catch (err: any) {
    const errorTime = Date.now() - startTime
    logger.error('登录请求异常', err, {
      username: username.value,
      backendUrl,
      requestTime: `${errorTime}ms`,
      errorCode: err.code,
      errorStatus: err.response?.status
    })

    let errorMsg = '服务器连接失败'
    if (err.response?.data?.message) {
      errorMsg = err.response.data.message
    } else if (err.code === 'ECONNABORTED') {
      errorMsg = '请求超时，请检查网络连接'
    } else if (err.code === 'ERR_NETWORK') {
      errorMsg = '网络错误，请检查后端服务是否启动'
    }

    alert(`登录失败：${errorMsg}`)
  } finally {
    loading.value = false
    const totalTime = Date.now() - startTime
    logger.performance('login_process_complete', startTime, {
      success: loading.value,
      totalTime: `${totalTime}ms`
    })
  }
}

// 使用演示账号
function useDemoAccount() {
  logger.action('use_demo_account')
  username.value = 'demo'
  password.value = '123456'
  alert('已填充演示账号，点击登录即可体验')
  logger.info('演示账号已填充')
}

// 忘记密码
function showForgotPassword() {
  logger.action('forgot_password_click')
  alert('请联系系统管理员重置密码\n邮箱：1597338110@qq.com\n电话：193-0301-0517')
}

// 跳转到注册
function goToRegister() {
  logger.action('navigate_to_register')
  router.push('/register')
}

// 页面加载时检查记住的用户
onMounted(() => {
  logger.debug('LoginView组件已挂载')

  try {
    const rememberedUser = localStorage.getItem('rememberedUser')
    if (rememberedUser) {
      username.value = rememberedUser
      rememberMe.value = true
      logger.debug('从localStorage恢复记住的用户', { username: rememberedUser })
    }

    // 监听页面可见性变化
    document.addEventListener('visibilitychange', handleVisibilityChange)

  } catch (storageError) {
    logger.warn('读取localStorage失败', { error: storageError })
  }
})

// 页面卸载
onUnmounted(() => {
  logger.debug('LoginView组件卸载')
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

// 页面可见性变化处理
function handleVisibilityChange() {
  if (document.visibilityState === 'visible') {
    logger.debug('页面变为可见状态')
  } else {
    logger.debug('页面变为隐藏状态')
  }
}

// 添加键盘事件支持
function handleKeyPress(event: KeyboardEvent) {
  if (event.key === 'Enter' && !loading.value) {
    logger.action('keyboard_login_enter')
    handleLogin()
  }
}

// 添加点击外部关闭功能（如果需要）
function handleClickOutside(event: MouseEvent) {
  // 可以添加点击外部逻辑
}

</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;

  /* 修改这里：替换渐变为背景图片---放于public文件夹中 */
  background-image: url('/1.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed; /* 可选：让背景固定，内容滚动时背景不动 */

  //background: linear-gradient(45deg, #2c3e50 0%, #3498db 100%);

  position: relative;
  overflow: hidden;
}

/* 添加加载遮罩样式 */
.login-btn:disabled::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  border-radius: inherit;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none" opacity="0.05"><path d="M0,0 L100,0 L100,100 Z" fill="white"/></svg>');
  background-size: cover;
}

/*背景毛玻璃实现    */
.login-card {
  width: 100%;
  max-width: 420px;

  background: rgba(255, 255, 255, 0.05); /* 透明度调整为0.15，可以根据需要调整 */

  //background: white;

  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  z-index: 1;
  animation: slideUp 0.6s ease;

  /* 可选：为卡片内部元素提供更好的可读性 */
  backdrop-filter: blur(10px); /* 毛玻璃效果，可选 */
  border: 1px solid rgba(255, 255, 255, 0.2); /* 可选：添加边框增强层次感 */

}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 15px;
}

.logo-icon {
  font-size: 36px;
  background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
}

.header h2 {
  color: #2c3e50;
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  text-align: left;
}

.header p {
  color: #2c3e50;
  font-size: 16px;
  margin-top: 5px;
}

.login-form {
  margin-bottom: 30px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2c3e50;
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 16px;
}

.icon-user::before {
  content: "👤";
}

.icon-lock::before {
  content: "🔒";
}

.input-group input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s;
  box-sizing: border-box;
}

.input-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.remember {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
}

.remember input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.forgot-btn {
  background: none;
  border: none;
  color: #3498db;
  font-size: 14px;
  cursor: pointer;
  padding: 0;
}

.forgot-btn:hover {
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.divider {
  display: flex;
  align-items: center;
  margin: 25px 0;
  color: #95a5a6;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #ecf0f1;
}

.divider span {
  padding: 0 15px;
  font-size: 14px;
}

.demo-btn {
  width: 100%;
  padding: 14px;
  background: #f8f9fa;
  color: #666;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.demo-btn:hover {
  background: #e9ecef;
  border-color: #3498db;
  color: #3498db;
}

.footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 25px;
  border-top: 1px solid #ecf0f1;
}

.footer p {
  color: #7f8c8d;
  margin-bottom: 10px;
}

.register-link-btn {
  padding: 12px 30px;
  background: white;
  color: #3498db;
  border: 2px solid #3498db;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.register-link-btn:hover {
  background: #3498db;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
}

.system-info {
  position: absolute;
  bottom: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  text-align: center;
  width: 100%;
}
</style>
