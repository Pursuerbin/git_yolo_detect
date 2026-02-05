// src/utils/logger.ts 新建文件
import axios from 'axios'

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  NONE = 4
}

export interface LogData {
  level: keyof typeof LogLevel
  message: string
  data?: Record<string, any>
  timestamp: string
  url?: string
  userAgent?: string
  stack?: string
}

class Logger {
  private level: LogLevel = LogLevel.DEBUG
  private readonly isDev: boolean = import.meta.env.DEV
  private readonly isProd: boolean = import.meta.env.PROD
  private readonly localStorageKey = 'app_logs'

  private readonly maxLocalStorageLogs = 20  // 减少存储数量
  private readonly flushThreshold = 10      // 增加触发阈值
  private readonly flushDelay = 3000        // 增加延迟时间

  private queue: LogData[] = []
  private isFlushing = false

  constructor() {
    // 根据环境设置日志级别
    this.level = this.isDev ? LogLevel.DEBUG : LogLevel.WARN

    // 检查是否有旧的错误日志
    this.checkStoredLogs()

    // 全局错误捕获
    this.setupGlobalErrorHandlers()
  }

  /**
   * 设置日志级别
   */
  setLevel(level: keyof typeof LogLevel) {
    this.level = LogLevel[level]
  }

  /**
   * 调试日志
   */
  debug(message: string, data?: Record<string, any>) {
    if (this.level <= LogLevel.DEBUG) {
      const logData: LogData = {
        level: 'DEBUG',
        message,
        data,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent
      }

      console.debug(`🔍 [DEBUG] ${new Date().toLocaleTimeString()}: ${message}`, data || '')
      this.sendToServer(logData)
    }
  }

  /**
   * 信息日志
   */
  info(message: string, data?: Record<string, any>) {
    if (this.level <= LogLevel.INFO) {
      const logData: LogData = {
        level: 'INFO',
        message,
        data,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent
      }

      console.info(`ℹ️ [INFO] ${new Date().toLocaleTimeString()}: ${message}`, data || '')
      this.sendToServer(logData)
    }
  }

  /**
   * 警告日志
   */
  warn(message: string, data?: Record<string, any>) {
    if (this.level <= LogLevel.WARN) {
      const logData: LogData = {
        level: 'WARN',
        message,
        data,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent
      }

      console.warn(`⚠️ [WARN] ${new Date().toLocaleTimeString()}: ${message}`, data || '')
      this.sendToServer(logData)
    }
  }

  /**
   * 错误日志
   */
  error(message: string, error?: Error | any, data?: Record<string, any>) {
    if (this.level <= LogLevel.ERROR) {
      const logData: LogData = {
        level: 'ERROR',
        message,
        data: {
          ...data,
          errorMessage: error?.message,
          errorStack: error?.stack,
          errorType: error?.name
        },
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        stack: error?.stack
      }

      console.error(`❌ [ERROR] ${new Date().toLocaleTimeString()}: ${message}`, error || '', data || '')

      // 错误日志立即发送并存储到本地
      this.sendToServer(logData)
      this.storeLog(logData)
    }
  }

  /**
   * 性能日志
   */
  performance(name: string, startTime: number, data?: Record<string, any>) {
    const duration = Date.now() - startTime
    const logData: LogData = {
      level: 'INFO',
      message: `Performance: ${name}`,
      data: {
        ...data,
        duration: `${duration}ms`,
        name
      },
      timestamp: new Date().toISOString(),
      url: window.location.href
    }

    console.log(`⚡ [PERF] ${name}: ${duration}ms`)
    this.sendToServer(logData)
  }

  /**
   * 用户行为日志
   */
  action(action: string, data?: Record<string, any>) {
    const logData: LogData = {
      level: 'INFO',
      message: `User Action: ${action}`,
      data: {
        action,
        ...data
      },
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    }

    console.log(`🎯 [ACTION] ${action}`, data || '')
    this.sendToServer(logData)
  }

  /**
   * 发送日志到服务器
   */
  private async sendToServer(logData: LogData) {
    // 开发环境不发送到服务器，除非强制开启
    if (this.isDev && !import.meta.env.VITE_LOG_SERVER) {
      return
    }

    // 添加到队列，批量发送
    this.queue.push(logData)

    if (this.queue.length >= 5 && !this.isFlushing) {
      this.flushQueue()
    }

    // 延迟发送，确保不会频繁请求
    if (!this.isFlushing && this.queue.length > 0) {
      setTimeout(() => this.flushQueue(), 1000)
    }
  }

  /**
   * 批量发送日志
   */
  // 修改 flushQueue 函数
  private async flushQueue() {
      if (this.isFlushing || this.queue.length === 0) return

      this.isFlushing = true
      const logsToSend = [...this.queue]
      this.queue = []

      try {
          // 获取后端URL（使用与登录相同的逻辑）
          const getBackendUrl = () => {
              const { protocol, hostname } = window.location
              const port = 5000

              if (hostname === 'localhost' || hostname === '127.0.0.1') {
                  return `http://localhost:${port}`
              }

              // 判断是否为内网IP
              const isPrivateIP = /^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)/.test(hostname)

              if (isPrivateIP) {
                  return `${protocol}//${hostname}:${port}`
              }

              return `${protocol}//${hostname}:${port}`
          }

          const backendUrl = getBackendUrl()

          // 发送到后端日志接口
          await axios.post(`${backendUrl}/api/logs`, {
              logs: logsToSend
          }, {
              timeout: 3000,
              headers: { 'Content-Type': 'application/json' }
          })

      } catch (error) {
          // 发送失败，重新加入队列（但限制重试次数）
          console.warn('日志发送失败，重新加入队列')
          if (logsToSend.length > 0) {
              // 只保留最近的日志
              const recentLogs = logsToSend.slice(-10)
              this.queue.unshift(...recentLogs)
          }
      } finally {
          this.isFlushing = false
      }
  }

  /**
   * 存储日志到localStorage（用于离线情况）
   */
  private storeLog(logData: LogData) {
    try {
      const storedLogs = this.getStoredLogs()
      storedLogs.unshift(logData)

      // 限制存储数量
      if (storedLogs.length > this.maxLocalStorageLogs) {
        storedLogs.length = this.maxLocalStorageLogs
      }

      localStorage.setItem(this.localStorageKey, JSON.stringify(storedLogs))
    } catch (error) {
      // localStorage可能已满或不可用
      console.warn('无法存储日志到localStorage')
    }
  }

  /**
   * 获取存储的日志
   */
  private getStoredLogs(): LogData[] {
    try {
      const stored = localStorage.getItem(this.localStorageKey)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  }

  /**
   * 检查并上传存储的日志
   */
  private async checkStoredLogs() {
    const storedLogs = this.getStoredLogs()
    if (storedLogs.length > 0) {
      try {
        await axios.post('/api/logs', { logs: storedLogs })
        localStorage.removeItem(this.localStorageKey)
        console.info('📤 已上传离线日志')
      } catch (error) {
        // 保持日志在本地，下次再试
      }
    }
  }

  /**
   * 设置全局错误处理器
   */
  private setupGlobalErrorHandlers() {
    // Vue错误
    window.addEventListener('vue-error', (event: CustomEvent) => {
      this.error('Vue错误', event.detail.error, event.detail.info)
    })

    // JavaScript错误
    window.addEventListener('error', (event) => {
      this.error('JavaScript错误', event.error, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      })
    })

    // Promise错误
    window.addEventListener('unhandledrejection', (event) => {
      this.error('未处理的Promise错误', event.reason)
    })

    // 网络错误
    window.addEventListener('offline', () => {
      this.warn('网络已断开')
    })

    window.addEventListener('online', () => {
      this.info('网络已恢复')
    })
  }

  /**
   * 手动上传所有未发送的日志
   */
  async flushAllLogs() {
    await this.flushQueue()
  }

  /**
   * 清除所有本地存储的日志
   */
  clearLocalLogs() {
    localStorage.removeItem(this.localStorageKey)
    this.queue = []
  }

  /**
   * 获取当前队列长度
   */
  getQueueLength() {
    return this.queue.length
  }
}

// 创建单例实例
export const logger = new Logger()

// 导出默认实例
export default logger
