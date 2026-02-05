// 根据环境动态设置 API 地址
const API_BASE = import.meta.env.DEV
  ? 'http://localhost:5000'  // 开发环境
  : '/api'                    // 生产环境（使用 Nginx 代理）

export default {
  BASE_URL: API_BASE,
  LOGIN: `${API_BASE}/login`,
  REGISTER: `${API_BASE}/register`,
  DETECT: `${API_BASE}/detect`,
  // ... 其他 API 端点
}
