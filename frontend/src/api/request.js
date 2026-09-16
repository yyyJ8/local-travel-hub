import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, clearSession } from '../utils/session'

/**
 * Axios 统一封装（开发架构：请求层与页面解耦）
 * - 统一响应结构 { code, message, data }，此处自动解包出 data
 * - baseURL 使用相对路径 /api，由 Vite 代理转发到本地后端（无需处理跨域）
 * - 自动附加 Authorization: Bearer <token>；收到 401 时清理会话并跳登录页
 */
const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器：自动带令牌
request.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** 未登录/会话失效时统一跳登录页（登录、注册接口本身除外） */
function handleUnauthorized(url) {
  const isAuthApi = (url || '').includes('/auth/login') || (url || '').includes('/auth/register')
  if (isAuthApi) return // 登录页自身的 401 由页面提示，不做跳转
  clearSession()
  const current = window.location.hash.replace(/^#/, '') || '/'
  if (!current.startsWith('/login')) {
    const redirect = encodeURIComponent(current)
    window.location.hash = `#/login?redirect=${redirect}`
    ElMessage.warning('登录状态已失效，请重新登录')
  }
}

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res && typeof res === 'object' && 'code' in res) {
      if (res.code === 0) return res.data
      if (res.code === 401) handleUnauthorized(response.config?.url)
      ElMessage.error(res.message || '接口返回异常')
      return Promise.reject(new Error(res.message || '接口返回异常'))
    }
    return res
  },
  (error) => {
    ElMessage.error('网络请求失败，请确认后端服务已启动（127.0.0.1:8000）')
    return Promise.reject(error)
  }
)

export default request
