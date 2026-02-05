// vite.config.ts 完整修改
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],

  // 服务配置
  server: {
    host: '0.0.0.0',          // 允许所有IP访问
    port: 5173,               // 指定端口
    strictPort: true,         // 严格使用指定端口

    // 解决HMR热更新问题
    hmr: {
      host: 'localhost',      // 使用localhost进行HMR连接
      port: 5173,
      protocol: 'ws'          // 明确使用WebSocket协议
    },

    // 代理配置（如果需要）
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    },

    // 监听配置
    watch: {
      usePolling: true        // 解决某些文件系统监控问题
    },

    // 禁用自动打开浏览器
    open: false,

    // 禁用host检查
    allowedHosts: true
  },

  // 构建配置
  build: {
    sourcemap: process.env.NODE_ENV !== 'production', // 生产环境关闭sourcemap
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'], // 根据你的依赖调整
          axios: ['axios']
        }
      }
    },
    chunkSizeWarningLimit: 1000 // 增大chunk大小警告限制
  },

  // 解析配置
  resolve: {
    alias: {
      '@': resolve(__dirname, './src') // 如果使用@别名
    },
    extensions: ['.js', '.ts', '.vue', '.json'] // 自动解析的扩展名
  },

  // CSS配置
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";` // 如果有全局样式
      }
    }
  },

  // 环境变量
  define: {
    'process.env': process.env,
    '__VUE_PROD_DEVTOOLS__': false, // 禁用生产环境devtools
    '__VUE_OPTIONS_API__': true,    // 启用Options API
    '__VUE_PROD_HYDRATION_MISMATCH_DETAILS__': false
  }
})
