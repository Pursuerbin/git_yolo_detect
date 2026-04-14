<template>
  <div class="register-container">
    <div class="register-card">
      <div class="header">
        <div class="logo">
          <div class="logo-icon">⚡</div>
          <h2>绝缘子缺陷检测系统</h2>
        </div>
        <p>创建新账户，开始智能检测</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
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
            placeholder="请输入密码（至少6位）"
            required
          />
        </div>

        <div class="input-group">
          <label for="confirmPassword">
            <i class="icon-confirm"></i>
            确认密码
          </label>
          <input
            v-model="confirmPassword"
            type="password"
            id="confirmPassword"
            placeholder="请再次输入密码"
            required
          />
        </div>

        <button
          type="submit"
          class="register-btn"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '注册中...' : '立即注册' }}
        </button>
      </form>

      <div class="footer">
        <p>已有账号？</p>
        <button @click="goToLogin" class="login-link-btn">
          返回登录
        </button>
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="system-info">
      <p>技术支持：吴权彬 | 版本：v1.0</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { logger } from '@/utils/logger'

const router = useRouter()

// 表单数据
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

// 动态获取后端URL（与LoginView保持一致）
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

// 注册处理函数
async function handleRegister() {
  const startTime = Date.now()
  const registerData = {
    username: username.value,
    password: password.value ? '***' : '',
    confirmProvided: !!confirmPassword.value
  }

  logger.action('register_attempt', registerData)

  // 前端表单验证
  if (!username.value || !password.value || !confirmPassword.value) {
    logger.warn('注册验证失败：存在空字段', registerData)
    alert('请填写所有字段')
    return
  }

  if (password.value.length < 6) {
    logger.warn('密码长度不足6位', { username: username.value })
    alert('密码长度至少为6位')
    return
  }

  if (password.value !== confirmPassword.value) {
    logger.warn('密码确认不一致', { username: username.value })
    alert('两次输入的密码不一致')
    return
  }

  loading.value = true
  logger.debug('开始注册请求', { backendUrl, username: username.value })

  try {
    logger.info('发送注册API请求', {
      url: `${backendUrl}/api/register`,
      username: username.value
    })

    const res = await axios.post(`${backendUrl}/api/register`, {
      username: username.value,
      password: password.value
    }, {
      timeout: 10000,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
      }
    })

    const responseTime = Date.now() - startTime
    logger.debug('收到注册响应', {
      success: res.data.success,
      responseTime: `${responseTime}ms`
    })

    if (res.data.success) {
      logger.info('注册成功', {
        username: username.value,
        responseTime: `${responseTime}ms`
      })

      alert('注册成功，请登录')
      // 延迟跳转，确保用户看到提示
      setTimeout(() => {
        logger.action('register_success_redirect', { to: '/login' })
        router.push('/login')
      }, 800)
    } else {
      logger.warn('注册失败（服务器返回）', {
        message: res.data.message,
        username: username.value
      })
      alert(res.data.message || '注册失败，请稍后重试')
    }

  } catch (err) {
    const errorTime = Date.now() - startTime
    logger.error('注册请求异常', err, {
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
    } else if (err.message && err.message.includes('timeout')) {
      errorMsg = '请求超时，请稍后重试'
    }

    alert(`注册失败：${errorMsg}`)
  } finally {
    loading.value = false
    const totalTime = Date.now() - startTime
    logger.performance('register_process_complete', startTime, {
      success: !loading.value,
      totalTime: `${totalTime}ms`
    })
  }
}

// 跳转到登录页
function goToLogin() {
  logger.action('navigate_to_login_from_register')
  router.push('/login')
}

// 页面可见性变化处理
function handleVisibilityChange() {
  if (document.visibilityState === 'visible') {
    logger.debug('注册页面变为可见状态')
  } else {
    logger.debug('注册页面变为隐藏状态')
  }
}

// 组件挂载日志
onMounted(() => {
  logger.debug('RegisterView组件已挂载')

  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

// 组件卸载清理
onUnmounted(() => {
  logger.debug('RegisterView组件卸载')
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
.register-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(45deg, #2c3e50 0%, #3498db 100%);
  position: relative;
  overflow: hidden;
}

.register-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none" opacity="0.05"><path d="M0,0 L100,0 L100,100 Z" fill="white"/></svg>');
  background-size: cover;
}

.register-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  z-index: 1;
  animation: slideUp 0.6s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
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
  color: white;
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  text-align: left;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.header p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  margin-top: 5px;
}

.register-form {
  margin-bottom: 30px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 16px;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

.icon-user::before {
  content: "👤";
}

.icon-lock::before {
  content: "🔒";
}

.icon-confirm::before {
  content: "✓";
  display: inline-block;
  font-weight: bold;
}

.input-group input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.9);
}

.input-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
  background: white;
}

.register-btn {
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
  margin-top: 10px;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
}

.register-btn:disabled {
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

.footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 25px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.footer p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 10px;
}

.login-link-btn {
  padding: 12px 30px;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.login-link-btn:hover {
  background: #3498db;
  border-color: #3498db;
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
